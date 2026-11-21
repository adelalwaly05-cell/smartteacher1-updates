# يبني حزمة تحديث من state/exams ويكتب release/manifest.json
import os,sys,json,hashlib,zipfile,datetime
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
tag=sys.argv[1] if len(sys.argv)>1 else datetime.datetime.utcnow().strftime('%Y%m%d-%H%M')
note=sys.argv[2] if len(sys.argv)>2 else 'تحديث الاختبارات'
name='release/exams-%s.zip'%tag
with zipfile.ZipFile(os.path.join(R,name),'w',zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(os.path.join(R,'state','exams'))):
        if f.endswith('.json'):z.write(os.path.join(R,'state','exams',f),'site/exams/'+f)
h=hashlib.sha256(open(os.path.join(R,name),'rb').read()).hexdigest()
json.dump({'id':tag,'file':name,'sha256':h,'note':note},open(os.path.join(R,'release','manifest.json'),'w'),ensure_ascii=False,indent=1)
print(name,h)
