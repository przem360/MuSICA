from lib import userinput

# ============================= local imports =============================


try:
    from .draw import clear_screen, draw_text, refresh_screen, CH_W, CH_H, MAX_COL, MAX_ROW
except ImportError:
    from apps.musica.draw import  clear_screen, draw_text, refresh_screen, CH_W, CH_H, MAX_COL, MAX_ROW

# =============================== functions ===============================

INPUT = userinput.UserInput()

_CHAR_WIDTH = const(8)
_CHAR_HEIGHT = const(8)

BOARD_SIZE = cfg.screen_h

letters = [chr(i) for i in range(ord('a'), ord('z') + 1)]

def get_char():
    while True:
        keys = INPUT.get_new_keys()
        # remove these from keys
        keys = [k for k in keys if k not in ('ALT', 'CTL', 'FN', 'SHIFT', 'OPT')]

        if not keys:
            continue

        # return SPC as ' '
        if 'SPC' in keys:
            return ' '

        # return enter
        if 'ENT' in keys:
            return 'ENT'   # or '\n'

        # Obsługa BACKSPACE
        if 'BSPC' in keys:
            return '\b'   # lub 'BSPC'

        # Obsługa strzałek lub innych specjalnych klawiszy
        special = {'UP','DOWN','LEFT','RIGHT','G0','ESC'}
        for k in keys:
            if k in special:
                return k

        # Jeśli to zwykłe znaki — zwracamy pierwszy
        return keys[0]

def get_line():
    input_data = []
    while True:
        keys = INPUT.get_new_keys()
        keys = [x for x in keys if x not in ('ALT', 'CTL', 'FN', 'SHIFT', 'OPT')] # Strip invisible.

        if 'SPC' in keys:
            keys = list(map(lambda x: x if x != 'SPC' else ' ', keys)) # Expose spaces.

        while 'BSPC' in keys:
            if keys.index('BSPC') == 0:
                if len(input_data) > 0:
                    input_data.pop(-1)
                keys.pop(0)
            else:
                keys.pop(keys.index('BSPC') - 1)
                keys.pop(keys.index('BSPC'))

        if 'UP' in keys or 'DOWN' in keys:
            pass
        if 'LEFT' in keys or 'RIGHT' in keys:
            pass
        if 'ENT' in keys:
            before_ent = keys[:keys.index('ENT')]
            input_data.extend(before_ent)
            return ''.join(input_data)
        elif 'G0' in keys or 'ESC' in keys:
            input_data = []
        else:
            input_data.extend(keys)
            # print letter
            draw_text((len(input_data)*CH_W),(MAX_ROW-1)*CH_H, keys)
            refresh_screen()


