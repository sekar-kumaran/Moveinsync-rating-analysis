"""Fix garbled UTF-8 sequences caused by PowerShell Set-Content re-encoding."""
import pathlib

FIXES = [
    (b'\xe2\x98\x85', b'&#9733;'),   # filled star
    (b'\xe2\x98\x86', b'&#9734;'),   # empty star
    (b'\xc2\xb7',     b'&middot;'),  # middle dot
    (b'\xe2\x80\x94', b'--'),        # em dash
    (b'\xe2\x80\xa6', b'...'),       # ellipsis
    (b'\xe2\x86\x92', b'->'),        # right arrow
    (b'\xc2\xa0',     b' '),         # non-breaking space
    (b'\xe2\x80\x98', b"'"),         # left single quote
    (b'\xe2\x80\x99', b"'"),         # right single quote
    (b'\xe2\x80\x9c', b'"'),         # left double quote
    (b'\xe2\x80\x9d', b'"'),         # right double quote
]

# Also fix garbled Latin-1-interpreted sequences still present as text
TEXT_FIXES = [
    ("\u00e2\u02c6\u02dc\u00e2\u02c6\u2026", "&#9733;&#9734;"),  # mangled star sequences
    ("â˜…", "&#9733;"),
    ("â˜†", "&#9734;"),
    ("Â·",  "&middot;"),
    ("â€"", "--"),
    ("â€¦", "..."),
    ("â†'", "->"),
    ("Â ",  " "),
    ("â€™", "'"),
    ("â€˜", "'"),
]

files = list(pathlib.Path("app").rglob("*.py"))
total_fixed = 0

for f in files:
    raw = f.read_bytes()
    new_raw = raw
    for old_b, new_b in FIXES:
        new_raw = new_raw.replace(old_b, new_b)

    if new_raw != raw:
        f.write_bytes(new_raw)
        total_fixed += 1
        print(f"Fixed bytes: {f}")
    else:
        # Try text-level fixes for already-mangled content
        try:
            txt = new_raw.decode("utf-8")
        except UnicodeDecodeError:
            txt = new_raw.decode("latin-1")
        new_txt = txt
        for old_t, new_t in TEXT_FIXES:
            new_txt = new_txt.replace(old_t, new_t)
        if new_txt != txt:
            f.write_text(new_txt, encoding="utf-8")
            total_fixed += 1
            print(f"Fixed text: {f}")

print(f"\nTotal files fixed: {total_fixed}")
