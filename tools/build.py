import sys,json,glob,os,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));import p1,p2
B=os.environ.get('EXAMS_SRC','/mnt/user-data/uploads/الاختبارات النهائية من الرابع للثاني عشر 2026-2027 ف1/')
GD={'الرابع':4,'الخامس':5,'السادس':6,'السابع':7,'الثامن':8,'التاسع':9,'العاشر':10,'الحادي عشر':11,'الثاني عشر':12}
AN='٠١٢٣٤٥٦٧٨٩'
def an(n):return ''.join(AN[int(c)] if c.isdigit() else c for c in str(n))
def skname(h):
    h=re.sub(r'^(أولًا|ثانيًا|ثالثًا|رابعًا|خامسًا|سادسًا|سابعًا)\s*ـ\s*','',h).strip().rstrip(':').strip()
    return h
def fix(sections,paper1):
    out=[];sk=None
    for S in sections:
        S=dict(S)
        if S['lvl']==1:sk=skname(S['h'])
        S['sk']=sk or skname(S['h'])
        h=S['h'].rstrip().rstrip(':').strip()
        S['h']=h+': '+S['sk']
        items=[]
        for it in S['items']:
            it=dict(it)
            if it['k']=='dict':
                a=it.get('a','').split('\n');lab=a[0].lstrip('§');rest=a[1:]
                # أول سطر بعد العنوان هو النص الإملائي، والباقي ملاحظات المعلم
                S['dlabel']=lab;S['dictation']=rest[0] if rest else ''
                S['tnote']='\n'.join(rest[1:]);S['tlabel']='الكلمات المستهدفة وطريقة التصحيح';continue
            if it['k']=='note':
                S['tnote']=((S.get('tnote','')+'\n') if S.get('tnote') else '')+'§'+it['q']+'\n'+(it.get('a') or '')
                S['tlabel']=it['q'].rstrip(':');continue
            if it['k']=='essay' and it.get('nonum') and not it.get('a') and not it.get('subs') and not it.get('averses') and not it.get('passage') and not it.get('x') and not it.get('qverses'):
                # تعليمات فقط (مثل: اكتب في واحد من الموضوعين)
                S['intro']=((S.get('intro','')+'\n') if S.get('intro') else '')+it['q'];continue
            if it['k']=='topic' and it.get('m') is None:it.pop('m')
            for k in [k for k,v in list(it.items()) if v is None]:it.pop(k)
            items.append(it)
        n=0
        for it in items:
            if not it.get('nonum'):n+=1;it['n']=n
        S['items']=items
        for k in [k for k,v in list(S.items()) if v in (None,'',{},[]) and k!='items']:S.pop(k)
        out.append(S)
    return out
def pmarks(secs):return sum((s.get('marks') or 0) for s in secs if s['lvl']==1) or sum((s.get('marks') or 0) for s in secs)
res={}
for d in sorted(glob.glob(B+'*/')):
    g=GD[os.path.basename(d.rstrip('/')).replace('الصف ','')]
    f1=glob.glob(d+'*الأولى*المعلم*');f2=glob.glob(d+'*الثانية*المعلم*')
    P1=p1.parse(f1[0]) if f1 else [];P2=p2.parse(f2[0]) if f2 else []
    n=max(len(P1),len(P2));models=[]
    for k in range(n):
        papers=[]
        if k<len(P1):s=fix(P1[k]['sections'],True);papers.append({'name':'الورقة الأولى','marks':pmarks(s),'sections':s})
        if k<len(P2):s=fix(P2[k]['sections'],False);papers.append({'name':'الورقة الثانية','marks':pmarks(s),'sections':s})
        tot=sum(p['marks'] for p in papers);tot=int(tot) if tot==int(tot) else tot
        for p in papers:p['marks']=int(p['marks']) if p['marks']==int(p['marks']) else p['marks']
        models.append({'grade':g,'model':k+1,'title':'نموذج الاختبار النهائي التجريبي ('+an(k+1)+')','term':'الفصل الدراسي الأول 2026/2027','total':tot,'papers':papers})
    res[g]=models
    print(g,'models',len(models),[ (m['total'],[p['name'][-6:] for p in m['papers']]) for m in models])
json.dump(res,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'all.json'),'w'),ensure_ascii=False)
