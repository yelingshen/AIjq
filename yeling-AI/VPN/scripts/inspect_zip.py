import os
import zipfile

zip_path = r"C:\Users\WJ\Desktop\VPN\VPN\multi_tool_release.zip"
if not os.path.exists(zip_path):
    print('ZIP_MISSING')
    raise SystemExit(1)

size = os.path.getsize(zip_path)
print(f'ZIP_PATH: {zip_path}')
print(f'SIZE_BYTES: {size}')

with zipfile.ZipFile(zip_path, 'r') as z:
    entries = z.namelist()
    for i, name in enumerate(entries[:50]):
        print(name)
    print(f'ENTRY_COUNT: {len(entries)}')
