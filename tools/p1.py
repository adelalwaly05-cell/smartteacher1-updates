import sys,re,json
import os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));import p2
HD=re.compile(r'^(أولًا|ثانيًا|ثالثًا|رابعًا|خامسًا|سادسًا)\s*ـ')
def parse(path):
    P=p2.paras(path);models=[];M=None;sec=None;it=None
    def add(line,lab=False):
        nonlocal it
        if it is None:
            it={'k':'essay','q':'','m':None,'nonum':1};sec['items'].append(it)
        it['a']=(it['a']+'\n' if it.get('a') else '')+('§' if lab else '')+line
    for t,runs in P:
        s=t.strip().replace('\t',' ')
        if s.startswith('النموذج'):M={'sections':[]};models.append(M);sec=None;it=None;continue
        if M is None or re.match(r'^(امتحان|مادة |اسم الطالب|انتهت)',s):continue
        blue=any(r[1] for r in runs if r[0].strip());red=any(r[2] for r in runs if r[0].strip())
        if HD.match(s) and not blue:
            h,m=p2.marks(s);sec={'h':h,'marks':m,'lvl':1,'items':[]};M['sections'].append(sec);it=None;continue
        if blue:
            mt=re.match(r'^الموضوع (الأول|الثاني)',s)
            if mt:
                tps=[x for x in sec['items'] if x['k']=='topic'];k=0 if mt.group(1)=='الأول' else 1
                if len(tps)>k:
                    it=tps[k];lab,rest=s.split(':',1) if ':' in s else (s,'');it['a']=(it['a']+'\n' if it.get('a') else '')+'§'+lab.strip()+':\n'+rest.strip();continue
            if s.startswith('معايير التقدير'):
                lab,rest=s.split(':',1);sec['items'].append({'k':'note','q':lab.strip()+':','m':None,'nonum':1,'a':rest.strip()});it=sec['items'][-1];continue
            add(s);continue
        if red or re.search(r'[:：]\s*$',s) and not p2.QN.match(s) and sec['items'] and len(s)<60:
            lab=p2.marks(s)[0]
            if lab.startswith('النص الإملائي'):
                it={'k':'dict','q':'اكتب ما يُملى عليك:','m':None,'nonum':1,'a':'§'+lab};sec['items'].append(it);continue
            if lab.startswith('توزيع الدرجات') or lab.startswith('معايير'):
                it={'k':'note','q':lab,'m':None,'nonum':1};sec['items'].append(it);continue
            if red and not sec['items'] and not lab.startswith('عناصر') and not lab.startswith('نموذج'):
                q,m=p2.marks(s);it={'k':'essay','q':q,'m':m,'nonum':1};sec['items'].append(it);continue
            add(lab,True);continue
        if s.startswith('التلخيص') and it is not None:
            add(p2.marks(s)[0],True);continue
        mq=p2.QN.match(s)
        if mq:
            q,m=p2.marks(s);it={'k':'topic','q':p2.QN.sub('',q),'m':m};sec['items'].append(it);continue
        # black non-numbered
        if not sec['items']:sec['intro']=(sec.get('intro','')+'\n'+p2.marks(s)[0]).strip();continue
        if it is not None and it.get('a') is None and len(s)>120:
            it.setdefault('passage',[]).append(s);continue
        q,m=p2.marks(s)
        it={'k':'essay','q':q,'m':m,'nonum':1};sec['items'].append(it)
    return models
if __name__=='__main__':print(json.dumps(parse(sys.argv[1]),ensure_ascii=False,indent=1))
