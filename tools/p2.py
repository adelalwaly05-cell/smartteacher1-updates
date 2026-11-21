import sys,re,json
from docx import Document
from docx.text.paragraph import Paragraph
AD='٠١٢٣٤٥٦٧٨٩'
def isblue(r):
    try:
        c=r.font.color.rgb if r.font.color and r.font.color.type else None
    except Exception: c=None
    if c is None: return False
    c=str(c);R,G,B=int(c[0:2],16),int(c[2:4],16),int(c[4:6],16)
    return B>140 and R<90 and G<120
def isred(r):
    try:c=str(r.font.color.rgb) if r.font.color and r.font.color.type else ''
    except Exception:c=''
    if not c:return False
    R,G,B=int(c[0:2],16),int(c[2:4],16),int(c[4:6],16)
    return R>150 and G<60 and B<60
def paras(path):
    d=Document(path);out=[]
    for el in d.element.body.iter():
        if el.tag.endswith('}p'):
            # skip paragraphs nested inside textboxes handled anyway
            p=Paragraph(el,d)
            runs=[(r.text,isblue(r),isred(r),bool(r.bold)) for r in p.runs]
            t=''.join(x[0] for x in runs)
            if t.strip():out.append((t,runs))
    return out
MK=re.compile(r'\s*\(([٠-٩\d½¼]+|درجتان|درجة واحدة)\s*(درجات|درجة)?\)\s*$')
def marks(t):
    m=MK.search(t)
    if not m:return t.strip(),None
    v=m.group(1)
    if v=='درجتان':n=2
    elif v=='درجة واحدة':n=1
    else:
        v=v.replace('½','.5').replace('¼','.25')
        v=''.join(str(AD.index(c)) if c in AD else c for c in v)
        if v.startswith('.'):v='0'+v
        n=float(v);n=int(n) if n==int(n) else n
    return t[:m.start()].strip(),n
OPT=re.compile(r'^\s*([أبجده])\s*[-ـ]\s*')
QN=re.compile(r'^\s*([٠-٩]+)\s*[-ـ]\s*')
def parse(path):
    P=paras(path);models=[];M=None;sec=None;it=None
    for t,runs in P:
        s=t.strip()
        if s.startswith('النموذج'):
            M={'sections':[]};models.append(M);sec=None;it=None;continue
        if M is None or s.startswith('امتحان') or s.startswith('مادة ') or s.startswith('اسم الطالب'):continue
        if s.startswith('انتهت الأسئلة'):continue
        red=any(r[2] for r in runs if r[0].strip());bold=any(r[3] for r in runs if r[0].strip() and r[2])
        blue_any=any(r[1] for r in runs if r[0].strip());blue_all=blue_any and all(r[1] for r in runs if r[0].strip())
        if red:
            h,m=marks(s.replace('\t',' '));sec={'h':h,'marks':m,'lvl':1 if bold else 2,'items':[]};M['sections'].append(sec);it=None;continue
        if sec is None:
            sec={'h':'','marks':None,'lvl':2,'items':[]};M['sections'].append(sec)
        if it is not None and OPT.match(s) and re.search(r'\(\s*[✓✗×√]?\s*\)\s*$',s.replace('\t',' ')):
            mk=[r[0].strip() for r in runs if r[0].strip() in ('✓','✗','×','√')]
            q=re.sub(r'\(\s*[✓✗×√]?\s*\)\s*$','',s.replace('\t',' ')).strip()
            it.setdefault('subs',[]).append({'k':'tf','q':OPT.sub('',q).strip(),'a':('✓' if mk and mk[0] in ('✓','√') else '✗') if mk else None});continue
        # verse
        tabs=[x for x in t.split('\t') if x.strip()]
        if t.startswith('\t') and len(tabs)==2 or (len(tabs)==2 and '\t' in t.strip() and not MK.search(t)):
            a=QN.sub('',tabs[0]).strip();b=tabs[1].strip()
            if it is not None and (blue_all or it.get('a') is not None):
                it.setdefault('averses',[]).append([a,b]) if blue_all else it.setdefault('qverses',[]).append([a,b])
            elif it is not None:
                it.setdefault('qverses',[]).append([a,b])
            else:
                sec.setdefault('passage',{}).setdefault('verses',[]).append([a,b])
            continue
        if OPT.match(s) and it is not None:
            # صح/خطأ
            if any(r[1] and r[0].strip() in ('✓','✗','×','√') for r in runs):
                mk=[r[0].strip() for r in runs if r[1] and r[0].strip()][0]
                q=re.sub(r'\(\s*[✓✗×√]?\s*\)\s*$','',s.replace('\t',' ')).strip()
                it.setdefault('subs',[]).append({'k':'tf','q':OPT.sub('',q).strip(),'a':'✓' if mk in ('✓','√') else '✗'});continue
            hasSep='\u2003' in t
            if not hasSep and not blue_any and re.search(r'[:：؟]\s*$',s):
                it.setdefault('subs',[]).append({'k':'mcq','q':OPT.sub('',s).strip(),'choices':[]});continue
            buf='';bl=False;segs=[]
            for txt,b,_,_ in runs:
                for piece in re.split(r'(\u2003+|\t)',txt):
                    if piece and re.fullmatch(r'\u2003+|\t',piece):
                        if buf.strip():segs.append((buf.strip(),bl))
                        buf='';bl=False
                    else:
                        buf+=piece;bl=bl or (b and piece.strip()!='')
            if buf.strip():segs.append((buf.strip(),bl))
            tg=it
            if it.get('subs') and it['subs'][-1]['k']=='mcq' and len(it['subs'][-1]['choices'])<4:tg=it['subs'][-1]
            else:it['k']='mcq'
            ch=tg.setdefault('choices',[])
            for sg,b in segs:
                if b:tg['a']=len(ch)
                ch.append(OPT.sub('',sg).strip())
            continue
        mq=QN.match(s)
        if mq and not blue_any:
            q,m=marks(s.replace('\t',' '))
            it={'k':'essay','q':QN.sub('',q),'m':m};sec['items'].append(it);continue
        if blue_any:
            if it is None:
                it={'k':'essay','q':'','m':None};sec['items'].append(it)
            line=s.replace('\t',' ')
            it['a']=(it['a']+'\n' if isinstance(it.get('a'),str) else '')+line
            continue
        # plain black text
        if MK.search(s) and not QN.match(s) and (it is None or it.get('a') is not None or it.get('k')=='mcq'):
            q,m=marks(s.replace('\t',' '))
            it={'k':'essay','q':q,'m':m,'nonum':1};sec['items'].append(it);continue
        if it is None and not sec['items']:
            if len(s)>140 or sec.get('passage'):
                sec.setdefault('passage',{}).setdefault('paras',[]).append(s)
            else:
                sec['intro']=(sec.get('intro','')+'\n'+s).strip()
        elif it is not None and it.get('a') is None and it.get('k')!='mcq':
            it['x']=(it.get('x','')+'\n'+s).strip()
        elif it is not None and it.get('k')=='mcq':
            it['x']=(it.get('x','')+'\n'+s).strip()
        else:
            # paragraph after an answered item with no number: new item-less text (e.g. instruction for next)
            q,m=marks(s.replace('\t',' '))
            it={'k':'essay','q':q,'m':m,'nonum':1};sec['items'].append(it)
    for M in models:
        for sec in M['sections']:
            for it in sec['items']:
                if it.get('k')=='mcq' and not isinstance(it.get('a'),int):
                    it['x']=((it.get('x','')+'\n') if it.get('x') else '')+'   '.join(c for c in it.get('choices',[]));it['k']='essay';it.pop('choices',None)
    return models
if __name__=='__main__':
    print(json.dumps(parse(sys.argv[1]),ensure_ascii=False,indent=1))
