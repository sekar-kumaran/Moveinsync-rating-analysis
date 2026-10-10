import pathlib

FIXES = [
    (b'\xe2\x98\x85', b'&#9733;'),
    (b'\xe2\x98\x86', b'&#9734;'),
    (b'\xc2\xb7',     b'&middot;'),
    (b'\xe2\x80\x94', b'--'),
    (b'\xe2\x80\x93', b'-'),
    (b'\xe2\x80\xa6', b'...'),
    (b'\xe2\x86\x92', b'->'),
    (b'\xc2\xa0',     b' '),
    (b'\xe2\x80\x9c', b'"'),
    (b'\xe2\x80\x9d', b'"'),
]
QUOTE_FIX = [(b'\xe2\x80\x98', b"'"), (b'\xe2\x80\x99', b"'")]

for f in pathlib.Path('app').rglob('*.py'):
    raw = f.read_bytes()
    new = raw
    for old, repl in FIXES + QUOTE_FIX:
        new = new.replace(old, repl)
    if new != raw:
        f.write_bytes(new)
        print('Fixed:', f.name)

print('done')
