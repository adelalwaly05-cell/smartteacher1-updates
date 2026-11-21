# smartteacher1-updates

مستودع التحديث التلقائي لموقع smartteacher1.com.

- `release/manifest.json`: آخر تحديث. يقرؤه الموقع (كل ~15 دقيقة عند الزيارات) ويثبّت الحزمة بعد التحقق من SHA-256.
- الحزم تحتوي ملفات ثابتة فقط (لا PHP).
- `tools/`: أدوات تحويل نماذج الاختبارات (docx نسخة المعلم) إلى JSON:
  1. `EXAMS_SRC=<مجلد الصفوف>/ python3 tools/build.py`
  2. `python3 tools/post.py` (يكتب إلى state/exams)
  3. `python3 tools/release.py <tag> "<ملاحظة>"` ثم commit و push.
