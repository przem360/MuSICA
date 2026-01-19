import time
import machine
import os


# =====================================================================
#                         LOGGING SYSTEM
# =====================================================================

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

LOG_FILE = SCRIPT_DIR + "/" + "musica_log.txt"


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


def exit_prg():
    machine.reset()

