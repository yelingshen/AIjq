import os, subprocess

MULTI_EXT = [".tar.gz",".tar.xz",".tar.bz2"]

def detect_ext(file_path):
    lf = os.path.basename(file_path).lower()
    for ext in MULTI_EXT:
        if lf.endswith(ext):
            return ext[1:]
    if '.' in lf:
        return lf.split('.')[-1]
    try:
        out = subprocess.check_output(["file","--mime-type","-b",file_path]).decode()
        return out.strip().split("/")[-1]
    except:
        return "unknown"
