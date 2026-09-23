"""Проверяемые промежуточные материалы анализа; исходники не изменяются."""
import concurrent.futures
import html
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone
from urllib import request, parse

from dotenv import dotenv_values
from PIL import Image, ImageDraw, ImageFont

WORK = Path(__file__).resolve().parent
BASE = WORK.parent
ROOT = Path('/home/egor/agent-second-brain')
DURATION = 18639.423855

def save(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2))
    temp.replace(path)

def stamp(t):
    t = int(t)
    return f'{t//3600:02}:{t//60%60:02}:{t%60:02}'

def prepare():
    frames = sorted((BASE/'frames').glob('frame-*.jpg'))
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
    for start in range(0,len(frames),25):
        canvas=Image.new('RGB',(2000,1250),'white')
        draw=ImageDraw.Draw(canvas)
        for j,p in enumerate(frames[start:start+25]):
            x,y=(j%5)*400,(j//5)*250
            with Image.open(p) as im:
                im.thumbnail((400,225))
                canvas.paste(im,(x,y+25))
            draw.text((x+5,y+2),p.stem,font=font,fill='black')
        canvas.save(WORK/f'контакт-{start//25+1:03}.jpg',quality=92)
    raw=(BASE/'subtitles/X-pbJWKmwi0.en-orig.vtt').read_text()
    cues=[]
    for block in raw.split('\n\n'):
        match=re.search(r'(\d\d):(\d\d):(\d\d\.\d+) --> (\d\d):(\d\d):(\d\d\.\d+)',block)
        if not match: continue
        vals=list(map(float,match.groups()))
        a=vals[0]*3600+vals[1]*60+vals[2]
        b=vals[3]*3600+vals[4]*60+vals[5]
        # Rolling VTT captions have a brief previous-line duplicate cue.
        body=block[match.end():].split('\n',1)
        if len(body)<2: continue
        value=html.unescape(re.sub('<[^>]+>','',body[1])).strip()
        if not value or b-a < .1: continue
        cues.append({'start':a,'end':b,'text':value})
    save(WORK/'субтитры-по-времени.json',cues)
    chapters=json.loads((BASE/'metadata.json').read_text())['chapters']
    for i,ch in enumerate(chapters,1):
        selected=[c for c in cues if ch['start_time']<=c['start']<ch['end_time']]
        (WORK/f'текст-глава-{i:02}.txt').write_text('\n'.join(f"[{stamp(c['start'])}] {c['text'].replace(chr(10),' ')}" for c in selected))
    save(WORK/'проверка-состояние.json',{'started':datetime.now(timezone.utc).isoformat(),'status':'выполняется','frames_total':len(frames),'frames_reviewed':0,'text_chapters_reviewed':[],'audio':'ожидает','note':'Подготовка файлов и OCR не считаются смысловым анализом.'})
    print('Подготовлено',len(frames),'кадров;',len(cues),'реплик;',len(chapters),'глав',flush=True)

def audio_chunk(i):
    a=i*600
    duration=min(600,DURATION-a)
    out=WORK/f'аудио-{i+1:02}.json'
    mp3=WORK/f'аудио-{i+1:02}.mp3'
    if out.exists(): return json.loads(out.read_text())
    if not mp3.exists():
        subprocess.run(['ffmpeg','-v','error','-ss',str(a),'-i',str(BASE/'video.mp4'),'-t',str(duration),'-vn','-ac','1','-ar','16000','-b:a','64k',str(mp3)],check=True)
    key=dotenv_values(ROOT/'.env')['DEEPGRAM_API_KEY']
    params=parse.urlencode({'model':'nova-3','language':'en','punctuate':'true','smart_format':'true','paragraphs':'true','utterances':'true'})
    req=request.Request('https://api.deepgram.com/v1/listen?'+params,data=mp3.read_bytes(),headers={'Authorization':'Token '+key,'Content-Type':'audio/mpeg'},method='POST')
    with request.urlopen(req,timeout=1800) as response:
        data=json.loads(response.read())
    data['audit']={'source':'video.mp4','offset':a,'requested_duration':duration,'processed_at':datetime.now(timezone.utc).isoformat()}
    alt=data['results']['channels'][0]['alternatives'][0]
    if not alt.get('words'): raise RuntimeError(f'Нет распознанной речи в части {i+1}')
    save(out,data)
    print(f"Аудио {i+1}/32: {len(alt['words'])} слов, {data['metadata'].get('duration')} секунд",flush=True)
    return data

def audio():
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        parts=list(ex.map(audio_chunk,range(32)))
    words=[]
    paragraphs=[]
    for part in parts:
        offset=part['audit']['offset']
        alt=part['results']['channels'][0]['alternatives'][0]
        words.extend([{**w,'start':w['start']+offset,'end':w['end']+offset} for w in alt['words']])
        for p in alt.get('paragraphs',{}).get('paragraphs',[]):
            paragraphs.append({'start':p['start']+offset,'end':p['end']+offset,'text':' '.join(s['text'] for s in p['sentences'])})
    save(BASE/'аудио-расшифровка.json',{'source':'Deepgram nova-3, en; независимое распознавание исходной звуковой дорожки','duration':DURATION,'chunks':32,'words':words,'paragraphs':paragraphs})
    (BASE/'аудио-расшифровка.md').write_text('# Независимая расшифровка аудиодорожки\n\n'+'\n\n'.join(f"[{stamp(p['start'])}–{stamp(p['end'])}] {p['text']}" for p in paragraphs)+'\n')
    chapters=json.loads((BASE/'metadata.json').read_text())['chapters']
    for i,ch in enumerate(chapters,1):
        selected=[p for p in paragraphs if ch['start_time']<=p['start']<ch['end_time']]
        (WORK/f'звук-глава-{i:02}.txt').write_text('\n'.join(f"[{stamp(p['start'])}] {p['text']}" for p in selected))
    print('Аудиодорожка распознана целиком:',len(words),'слов',flush=True)

def ocr_one(path):
    out=WORK/(path.stem+'-ocr.txt')
    if out.exists(): return
    env={**os.environ,'OMP_THREAD_LIMIT':'1'}
    p=subprocess.run(['tesseract',str(path),'stdout','-l','eng','--psm','11'],capture_output=True,text=True,env=env,check=True)
    out.write_text(p.stdout)

def ocr():
    frames=sorted((BASE/'frames').glob('frame-*.jpg'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for i,_ in enumerate(ex.map(ocr_one,frames),1):
            if i%50==0: print('Распознавание надписей',i,'/',len(frames),flush=True)
    print('Распознавание надписей завершено',flush=True)

def timeline():
    log=WORK/'сцены-журнал.txt'
    with log.open('w') as out:
        subprocess.run(['ffmpeg','-hide_banner','-threads','2','-i',str(BASE/'video.mp4'),'-an','-vf',"select='gt(scene,0.18)',showinfo",'-fps_mode','vfr','-f','null','-'],stdout=subprocess.DEVNULL,stderr=out,check=True)
    text=log.read_text()
    times=[float(v) for v in re.findall(r'\bn:\s*\d+\s+pts:.*?pts_time:([\d.]+)',text)]
    frames=sorted((BASE/'frames').glob('frame-*.jpg'))
    if len(times)!=len(frames): raise RuntimeError(f'Число сцен не совпало: {len(times)} / {len(frames)}')
    save(BASE/'кадры-время.json',[{'frame':p.name,'seconds':t,'time':stamp(t)} for p,t in zip(frames,times)])
    print('Восстановлены временные метки',len(times),'кадров',flush=True)

if __name__=='__main__':
    globals()[sys.argv[1]]()
