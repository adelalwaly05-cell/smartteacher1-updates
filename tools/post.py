import json,re,os
import os;X=os.environ.get('EXAMS_OUT',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','state','exams'))+'/'
A=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'all.json')))
G10A="الشعور الأول: الخوف والهلع والإشفاق عليه أن يُقتَل؛ حتى كادت تُبدي أمرَه من شدّة الاضطراب، لولا أن ربط الله على قلبها.\nالشعور الثاني: الطمأنينة والثقة بوعد الله؛ إذ أصبح فؤادها فارغًا من الخوف والحزن بعد أن ثبّتها الله، فصارت واثقة بحسن عاقبته.\n(ومن مشاعرها أيضًا: الفرح وقرّة العين حين ردّه الله إليها)."
def fixit(it):
    # اختيار من متعدد مُحلَّل خطأً: (جملتان أ/ب ثم معنيان)
    ch=it.get('choices') or []
    if it['k']=='mcq' and ch and re.search(r'\s{3,}ب-\s',ch[0]) and any(c.startswith('المعنى') for c in ch[1:]):
        a,b=re.split(r'\s{3,}ب-\s',ch[0],1)
        ms=[c for c in ch[1:]]
        it.update(k='essay',x='أ- '+a.strip()+'\nب- '+b.strip(),a='أ- '+ms[0]+'\nب- '+ms[1]);it.pop('choices',None)
for g,models in A.items():
    for M in models:
        for P in M['papers']:
            for S in P['sections']:
                for it in S['items']:
                    fixit(it)
                    if g=='10' and M['model']==1 and 'تباينت مشاعر أم موسى' in it['q']:it['a']=G10A
        names=[P['name'] for P in M['papers']]
        M['title']=re.sub(r'\s*–.*$','',M['title'])+' – '+('الورقتان الأولى والثانية' if len(names)>1 else names[0])
        json.dump(M,open(X+'g%s-%d.json'%(g,M['model']),'w'),ensure_ascii=False)
I=json.load(open(X+'index.json'))
for g,models in A.items():I[g]=[{'m':M['model'],'t':M['title'],'total':M['total']} for M in models]
# الصف الحادي عشر (القديم): أضف وصف الورقتين
for g in list(I):
    if g in A:continue
    for e in I[g]:
        M=json.load(open(X+'g%s-%d.json'%(g,e['m'])))
        if '–' not in M['title']:
            names=[P.get('name','') for P in M.get('papers',[])]
            M['title']+=' – '+('الورقتان الأولى والثانية' if len(names)>1 else (names[0] if names else ''))
            json.dump(M,open(X+'g%s-%d.json'%(g,e['m']),'w'),ensure_ascii=False)
        e['t']=M['title']
json.dump(dict(sorted(I.items(),key=lambda x:int(x[0]))),open(X+'index.json','w'),ensure_ascii=False)
for g,v in sorted(I.items(),key=lambda x:int(x[0])):print(g,[e['t'][-25:] for e in v])
