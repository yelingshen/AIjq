import zipfile
import os

src_zip = r"C:\Users\WJ\Desktop\VPN\VPN\multi_tool_release.zip"
out_zip = r"C:\Users\WJ\Desktop\VPN\VPN\multi_tool_release_clean.zip"
if not os.path.exists(src_zip):
    print('SRC_ZIP_MISSING')
    raise SystemExit(1)

skip_substrings = ('__pycache__', '.pyc', '.venv', '.git', '.vscode')
skip_exact = ('source/multi_tool_release.zip', )

with zipfile.ZipFile(src_zip, 'r') as zin:
    names = zin.namelist()
    with zipfile.ZipFile(out_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for name in names:
            if any(s in name for s in skip_substrings):
                continue
            if name in skip_exact:
                continue
            # Avoid writing the output zip into itself
            if name.endswith(os.path.basename(out_zip)):
                continue
            data = zin.read(name)
            zout.writestr(name, data)

print('CLEAN_ZIP_CREATED:', out_zip)
print('SIZE_BYTES:', os.path.getsize(out_zip))
with zipfile.ZipFile(out_zip,'r') as z:
    entries = z.namelist()
    for i, e in enumerate(entries[:20]):
        print(e)
    print('ENTRY_COUNT:', len(entries))
