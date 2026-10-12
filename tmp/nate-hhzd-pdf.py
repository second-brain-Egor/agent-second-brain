from pathlib import Path
from html import escape
from urllib.parse import quote
import re,json
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
V=Path('vault/projects/Nate Herk/videos/001-i-tried-100-github-repos-for-claude-these-6-are-the-best')
for name,file in [('D','DejaVuSans.ttf'),('D-Bold','DejaVuSans-Bold.ttf'),('D-Mono','DejaVuSansMono.ttf')]:pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
pdfmetrics.registerFontFamily('D',normal='D',bold='D-Bold',italic='D',boldItalic='D-Bold')
W,H=A4;margin=44;content=W-2*margin
sty=getSampleStyleSheet()
for name in ['Normal','BodyText','Title','Heading1','Heading2','Heading3']:sty[name].fontName='D'
sty['BodyText'].fontSize=10;sty['BodyText'].leading=14.3;sty['BodyText'].spaceAfter=7;sty['BodyText'].textColor=HexColor('#202936')
sty['Title'].fontName='D-Bold';sty['Title'].fontSize=23;sty['Title'].leading=28;sty['Title'].alignment=TA_LEFT;sty['Title'].spaceAfter=17;sty['Title'].textColor=HexColor('#123d4c')
for name,size in [('Heading1',15),('Heading2',12)]:sty[name].fontName='D-Bold';sty[name].fontSize=size;sty[name].leading=size+4;sty[name].spaceBefore=13;sty[name].spaceAfter=7;sty[name].textColor=HexColor('#123d4c');sty[name].keepWithNext=True
sty.add(ParagraphStyle(name='SmallRu',fontName='D',fontSize=8.2,leading=11,spaceAfter=5,textColor=HexColor('#50606d')))
sty.add(ParagraphStyle(name='CellRu',fontName='D',fontSize=8.5,leading=11.5,spaceAfter=1))
frame_rows=json.loads((V/'журнал-просмотра.json').read_text())['frames'];frames={r['file']:r.get('seconds',r.get('nominal_seconds',0)) for r in frame_rows}
def dest(url):
 if url.startswith(('http://','https://')):return url
 if url in frames:return 'https://www.youtube.com/watch?v=HhZdNYI4pJs&t='+str(int(frames[url]))+'s'
 p=(V/url).resolve()
 if p.name=='analysis.md':
  mp=p.parent/'metadata.json'
  if mp.exists():return json.loads(mp.read_text()).get('webpage_url')
 return None
def inline(s):
 parts=re.split(r'(\[[^\]]+\]\([^\)]+\)|\*\*[^*]+\*\*|`[^`]+`)',s);out=[]
 for part in parts:
  if part.startswith('**') and part.endswith('**'):out.append('<b>'+escape(part[2:-2])+'</b>')
  elif part.startswith('`') and part.endswith('`'):out.append('<font name="D-Mono" size="9">'+escape(part[1:-1])+'</font>')
  else:
   m=re.fullmatch(r'\[([^\]]+)\]\(([^\)]+)\)',part)
   if m:
    label,url=m.groups();url=dest(url)
    out.append('<link href="'+escape(url,quote=True)+'" color="#136b80">'+escape(label)+'</link>' if url else escape(label))
   else:out.append(escape(part))
 return ''.join(out)
source=(V/'analysis.md').read_text().split('---\n',2)[2].strip();lines=source.splitlines()
flow=[];i=0
while i<len(lines):
 l=lines[i].strip()
 if not l:i+=1;continue
 if l.startswith('|'):
  tab=[]
  while i<len(lines) and lines[i].strip().startswith('|'):
   row=lines[i].strip();i+=1
   if re.match(r'^\|[\s:|\-]+\|$',row):continue
   cells=[x.strip() for x in row.strip('|').split('|')]
   tab.append([Paragraph(inline(x),sty['CellRu']) for x in cells])
  table=Table(tab,colWidths=[72,205,content-277],repeatRows=1,hAlign='LEFT')
  table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#e2eff0')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,HexColor('#93b6c1')),('LINEBELOW',(0,1),(-1,-1),.3,HexColor('#d4dce0')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]));flow.extend([table,Spacer(1,9)]);continue
 if l.startswith('# '):style=sty['Title'];l=l[2:]
 elif l.startswith('## '):style=sty['Heading1'];l=l[3:]
 elif l.startswith('### '):style=sty['Heading2'];l=l[4:]
 elif l.startswith('- '):style=sty['BodyText'];l='• '+l[2:]
 else:style=sty['BodyText']
 flow.append(Paragraph(inline(l),style));i+=1
flow.append(PageBreak())
flow.append(Paragraph('Кадры, которые меняют понимание ролика',sty['Heading1']))
for fname,title,note in [
 ('контроль-00019.jpg','Около 00:36 — готовое окружение монтажа','На экране перечислены Hyperframes, video-use и связывающие их скрипты. Показанный процесс опирается на несколько заранее настроенных частей.'),
 ('контроль-00085.jpg','Около 02:48 — результат поиска Apify','Видна карточка файла «Пекарни Чикаго». Содержимое таблицы в ролике не раскрыто.'),
 ('контроль-00226.jpg','Около 07:30 — разрешения Supabase','Показаны операции записи и выбор разрешения создания проекта. Это не подтверждает заявленный голосом режим только чтения.'),
 ('контроль-00240.jpg','Около 07:58 — две ошибки формы','Claude сообщает о проблемах перехода по Enter и перекрывающем слое старой страницы. Завершённое исправление и повторная проверка в этом фрагменте отсутствуют.')]:
 item=[Paragraph(title,sty['Heading2']),Image(str(V/'frames'/fname),width=content,height=content*9/16),Spacer(1,6),Paragraph(note,sty['SmallRu'])]
 flow.append(KeepTogether(item))
def decorate(c,doc):
 c.setFont('D',8);c.setFillColor(HexColor('#667580'));c.drawString(margin,H-27,'Nate Herk · Проверено 12 октября 2026')
 c.line(margin,34,W-margin,34);c.drawString(margin,22,'Ролик HhZdNYI4pJs · ссылки в тексте открывают источники');c.drawRightString(W-margin,22,str(doc.page))
pdf=V/'Разбор ролика — дополнения для Claude.pdf'
doc=SimpleDocTemplate(str(pdf),pagesize=A4,rightMargin=margin,leftMargin=margin,topMargin=49,bottomMargin=47,title='Дополнения для Claude — полный разбор ролика Nate Herk',author='Помощник Егора')
doc.build(flow,onFirstPage=decorate,onLaterPages=decorate)
print(pdf)
