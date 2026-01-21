import time

try:
    from .helpers import SCRIPT_DIR, file_exists, get_first_line, write_txt_file, clean_log, log, list_files, exit_prg
except ImportError:
    from apps.nocturne.helpers import SCRIPT_DIR, file_exists, get_first_line, write_txt_file, clean_log, log, list_files, exit_prg

try:
    from .draw import _DISPLAY_HEIGHT, clear_screen, draw_text, draw_rect, refresh_screen, CH_W, CH_H, MAX_COL, MAX_ROW
except ImportError:
    from apps.nocturne.draw import _DISPLAY_HEIGHT, MAX_ROW, clear_screen, draw_text, draw_rect, refresh_screen, CH_W, CH_H, MAX_COL, MAX_ROW

try:
    from .uinput import get_char
except ImportError:
    from apps.nocturne.uinput import  get_char

try:
    from .nocturne import play_arp
except ImportError:
    from apps.nocturne.musica import play_arp

app_info = ["Nocturne", "0.01a"]
RECENT_FILES_LIST = "recent.txt"
song_loaded = False

def select_from_list(items):
    recent_exists = file_exists(SCRIPT_DIR + "/" + RECENT_FILES_LIST)
    recent_file_name = None
    if not items:
        return None
    idx = 0
    count = len(items)
    while True:
        clear_screen()
        draw_text(0, 4, "Select file ...")
        if recent_exists:
            recent_file_name = get_first_line(SCRIPT_DIR + "/" + RECENT_FILES_LIST)
            draw_text(12, 16, "[R] RECENT: {}".format(recent_file_name))
        draw_text(12, 34, "< " + items[idx] + " >")
        draw_text(0, _DISPLAY_HEIGHT-8, "Press [opt] + [q] to quit.")
        refresh_screen()
        key = get_char()
        if key in ("RIGHT", "/"):
            idx += 1
            if idx >= count:
                idx = 0

        elif key in ("LEFT", ","):
            idx -= 1
            if idx < 0:
                idx = count - 1
        elif key == "ENT":
            return items[idx]
        elif (key in ("R", "r")) and (recent_file_name is not None):
            return recent_file_name


def load_song(filename="/songs/song.mml"):
    title = None
    composer = None
    tracks = {}

    #log("load_song()")

    try:
        fullpath = __file__
        i = fullpath.rfind("/")     # find the last '/'
        if i == -1:
            SCRIPT_DIR = ""
        else:
            SCRIPT_DIR = fullpath[:i]
    except:
        print("Exception rised for fullpath = __file__")
        SCRIPT_DIR = "/sd/apps/Nocturne"
    
    filename = SCRIPT_DIR + filename

    #log("Filename: {}".format(filename))

    with open(filename, "r") as f:
        for raw_line in f:
            line = raw_line.strip()

            if not line:
                continue

            if line.startswith("#"):
                upper = line.upper()
                if "TITLE" in upper and ":" in line:
                    title = line.split(":", 1)[1].strip()
                elif "COMPOSER" in upper and ":" in line:
                    composer = line.split(":", 1)[1].strip()
                continue
            # reading tracks
            if "=" in line:
                name, value = line.split("=", 1)
                name = name.strip().lower()
                value = value.strip()

                if name.startswith("track"):
                    # get track number
                    try:
                        num = int(name[5:])
                        tracks[num] = value
                    except ValueError:
                        pass
                        
    # sort by number
    ordered_tracks = [tracks[n] for n in sorted(tracks)]
    song_loaded = True
    return title, composer, ordered_tracks

def main_menu():
    clear_screen()
    draw_text(6,4,app_info[0]+" (version: "+app_info[1]+")")
    draw_text(6,16, "[L] Load song.")
    draw_text(6,28, "[Q] Quit.")
    draw_rect(4,2,204,38)
    refresh_screen()
    while True:
        key = get_char()
        if key in ("Q", "q"):
            return 0
        elif key in ("L", "l"):
            return 1

def play_screen():
    clear_screen()
    draw_text(4,4,app_info[0]+" (version: "+app_info[1]+")")
    draw_text(4,16, "Playing...")
    draw_rect(2,2,204,24)

def main():
    LINE_SPACING = 4
    clean_log()
    while True:
        clear_screen()
        action = main_menu()
        if action == 0:
            exit_prg()
        else:
            song_list = list_files("songs", "mml")
            selected = select_from_list(song_list)
            write_txt_file(RECENT_FILES_LIST, selected)
            title, composer, tracks = load_song("/songs/"+selected)
            #log("Tracks:\n{}".format(tracks))
            play_screen()

            if title:
                draw_text(0,26+LINE_SPACING, "TITLE   : {}".format(title))
            if composer:
                draw_text(0,34+LINE_SPACING, "COMPOSER: {}".format(composer))
        
            refresh_screen()

            if not tracks:
                draw_text(0,12+LINE_SPACING, "No tracks found.")
                #log("No tracks found!")
                refresh_screen()
                time.sleep(3)
                return
        
            play_arp(tracks)



main()
exit_prg()
