import time

try:
    from .helpers import clean_log, log, exit_prg
except ImportError:
    from apps.musica.helpers import clean_log, log, exit_prg

try:
    from .draw import clear_screen, draw_text, refresh_screen, CH_W, CH_H, MAX_COL, MAX_ROW
except ImportError:
    from apps.musica.draw import  clear_screen, draw_text, refresh_screen, CH_W, CH_H, MAX_COL, MAX_ROW

try:
    from .musica import play_arp
except ImportError:
    from apps.musica.musica import play_arp


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
        SCRIPT_DIR = "/sd/apps/MuSICA"
    
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

    return title, composer, ordered_tracks


def main():
    LINE_SPACING = 4
    clean_log()
    #log("Start")
    clear_screen()
    draw_text(0,4,"MuSICA test.")
    refresh_screen()
    title, composer, tracks = load_song("/songs/song.mml")
    log("Tracks:\n{}".format(tracks))

    if title:
        draw_text(0,12+LINE_SPACING, "TITLE   : {}".format(title))
        #log("TITLE   : {}".format(title))
    if composer:
        draw_text(0,20+LINE_SPACING, "COMPOSER: {}".format(composer))
        #log("COMPOSER: {}".format(composer))
    
    refresh_screen()

    if not tracks:
        draw_text(0,12+LINE_SPACING, "No tracks found")
        log("No tracks found!")
        refresh_screen()
        time.sleep(3)
        return
    
    play_arp(tracks)



main()
exit_prg()
