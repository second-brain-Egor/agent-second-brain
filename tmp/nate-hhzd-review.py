import json, os, sys, subprocess, traceback, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from urllib import request, parse
BASE=Path('/home/egor/agent-second-brain')
V=BASE/'vault/projects/Nate Herk/videos/001-i-tried-100-github-repos-for-claude-these-6-are-the-best'
state={'started_at':datetime.now(timezone.utc).isoformat(),'status':'running','steps':{}}
def save():
    (V/'состояние-проверки.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
def run(args):
    subprocess.run(args,check=True,stdout=subprocess.DEVNULL)
def sheets(files,prefix,labels=None):
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
    for group in range(0,len(files),24):
        subset=files[group:group+24]
        canvas=Image.new('RGB',(1536,6*240),(245,245,245))
        draw=ImageDraw.Draw(canvas)
        for j,path in enumerate(subset):
            img=Image.open(path).convert('RGB'); img.thumbnail((384,216))
            x=(j%4)*384; y=(j//4)*240
            canvas.paste(img,(x,y+24))
            draw.text((x+5,y+2),(labels or {}).get(path.name,path.name),font=font,fill=(0,0,0))
        canvas.save(V/'frames'/f'{prefix}-{group//24+1:02d}.jpg',quality=92)
try:
    save()
    sheets(sorted((V/'frames').glob('frame-*.jpg')),'обзор-сцен')
    state['steps']['original_sheets']='complete'; save()
    run(['ffmpeg','-hide_banner','-loglevel','error','-n','-i',str(V/'video.mp4'),'-vf','fps=fps=1/2:start_time=0,scale=1280:-2','-q:v','3',str(V/'frames'/'контроль-%05d.jpg')])
    files=sorted((V/'frames').glob('контроль-*.jpg'))
    labels={p.name:f'{(i*2)//60:02d}:{(i*2)%60:02d}  {p.name}' for i,p in enumerate(files)}
    sheets(files,'обзор-времени',labels)
    state['steps']['timeline_frames']={'status':'complete','count':len(files),'interval_seconds':2}; save()
    run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(V/'video.mp4'),'-vf',f"select='gt(scene,0.18)',metadata=print:file={V/'метки-сцен.txt'}",'-an','-f','null','-'])
    state['steps']['scene_timestamps']='complete'; save()
    run(['ffmpeg','-hide_banner','-loglevel','error','-n','-i',str(V/'video.mp4'),'-vn','-ac','1','-ar','16000','-b:a','64k',str(V/'аудио.mp3')])
    state['steps']['audio_extraction']='complete';save()
    load_dotenv(BASE/'.env')
    key=os.environ.get('DEEPGRAM_API_KEY')
    if not key:
        raise RuntimeError('В конфигурации нет ключа распознавания аудио')
    params=parse.urlencode({'model':'nova-3','language':'en','punctuate':'true','smart_format':'true','paragraphs':'true','utterances':'true'})
    req=request.Request('https://api.deepgram.com/v1/listen?'+params,data=(V/'аудио.mp3').read_bytes(),headers={'Authorization':'Token '+key,'Content-Type':'audio/mpeg'},method='POST')
    with request.urlopen(req,timeout=300) as response:
        payload=json.loads(response.read().decode())
    (V/'аудио-расшифровка.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    alt=payload['results']['channels'][0]['alternatives'][0]
    paragraphs=alt.get('paragraphs',{}).get('paragraphs',[])
    blocks=['# Независимая расшифровка звуковой дорожки','', 'Источник: аудио из сохранённого video.mp4; Deepgram nova-3, английская речь. Это распознавание речи, не проверка звучания музыки и шумов.','']
    for p in paragraphs:
        t=int(p['start']); blocks.append(f'[{t//60:02d}:{t%60:02d}] '+ ' '.join(s['text'] for s in p['sentences']))
    if not paragraphs: blocks.append(alt.get('transcript',''))
    (V/'аудио-расшифровка.md').write_text('\n\n'.join(blocks)+'\n')
    state['steps']['audio_transcription']={'status':'complete','confidence':alt.get('confidence'),'words':len(alt.get('words',[]))};save()
    state['status']='sources_ready'
except Exception as exc:
    state['status']='error';state['error']=str(exc)
    traceback.print_exc()
finally:
    state['updated_at']=datetime.now(timezone.utc).isoformat();save()
