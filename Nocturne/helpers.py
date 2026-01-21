import time
import machine
import os
import io

# ========================== DIR ==========================

try:
    fullpath = __file__
    i = fullpath.rfind("/")     # find the last '/'
    if i == -1:
        SCRIPT_DIR = ""
    else:
        SCRIPT_DIR = fullpath[:i]
except:
    print("Exception rised for fullpath = __file__")
    SCRIPT_DIR = "/sd/apps"

LOG_FILE = SCRIPT_DIR + "/" + "nocturne_log.txt"

# ===================== GENERIC FILES =====================

def file_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError as e:
        return False

def get_first_line(full_path):
    with open(full_path) as f:
        return f.readline().strip('\n')

def write_txt_file(txt_file, txt):
    try:
        if not txt_file.startswith("/"):
            txt_file = "/" + txt_file
        full_path = SCRIPT_DIR + txt_file
        with open(full_path, "w") as f:
            f.write(txt)
        return 0
    except Exception as e:
        print("Could not create file:", e)
        return 1

def list_files(cat: str, ext: str):
    files = []
    ext = ext.lower()
    if not ext.startswith("."):
        ext = "." + ext
    if SCRIPT_DIR:
        path = SCRIPT_DIR + "/" + cat
    else:
        path = cat
    try:
        for name in os.listdir(path):
            full = path + "/" + name

            try:
                stat = os.stat(full)

                # check if it's regular file
                if stat[0] & 0x8000:
                    if name.lower().endswith(ext):
                        files.append(name)
            except:
                pass
    except Exception as e:
        print("list_files error:", e)

    return files

# ========================== LOG ==========================

def clean_log():
    try:
        os.remove(LOG_FILE)
    except:
        pass


def log(msg):
    try:
        timestamp = time.ticks_ms()
        with open(LOG_FILE, "a") as f:
            f.write("[{} ms] {}\n".format(timestamp, msg))
    except:
        pass

# ========================== EXIT =========================

def exit_prg():
    machine.reset()

