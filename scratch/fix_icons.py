import re, pathlib

files = list(pathlib.Path('app').rglob('*.py'))
pattern = re.compile(r',\s*icon=.{1,30}?\)', re.DOTALL)

for f in files:
    txt = f.read_text(encoding='utf-8')
    # Only strip icon= inside st.page_link calls
    def strip_icon(m):
        return re.sub(r',\s*icon=["\'][^"\']*["\']', '', m.group())
    new = re.sub(r'st\.page_link\([^)]+\)', strip_icon, txt)
    if new != txt:
        f.write_text(new, encoding='utf-8')
        print('Fixed:', f)

print('done')
