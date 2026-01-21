from lib import display
from lib.hydra import config
from lib.device import Device

# ============================= local imports =============================


# =============================== functions ===============================

from font import vga1_8x16 as midfont
#from font import vga2_16x32 as bigfont

DISPLAY = display.Display()
CONFIG = config.Config()

COLOR_BG = CONFIG.palette[2]     # background
COLOR_FG = CONFIG.palette[8]     # txt
COLOR_ERR = CONFIG.palette[9]    # orange?

_DISPLAY_HEIGHT = Device.display_height
_DISPLAY_WIDTH  = Device.display_width

_CHAR_WIDTH = const(8)
_CHAR_HEIGHT = const(8)

CH_W = _CHAR_WIDTH
CH_H = _CHAR_HEIGHT

MAX_COL = _DISPLAY_WIDTH // _CHAR_WIDTH
MAX_ROW = _DISPLAY_HEIGHT // _CHAR_HEIGHT

def refresh_screen():
    DISPLAY.show()

def clr_no_refresh():
    DISPLAY.fill(COLOR_BG)

def clear_screen():
    DISPLAY.fill(COLOR_BG)
    #DISPLAY.show()

def clear_line(row):
    y = row * _CHAR_HEIGHT
    DISPLAY.rect(0, y, DISPLAY.width, _CHAR_HEIGHT, COLOR_BG, fill=True)
    DISPLAY.show()
    
def draw_text(x, y, txt, col=COLOR_FG):
    DISPLAY.text(txt, x, y, col)
    # WARNING: text does not refresh the display

def draw_rect(x, y, w, h, col=COLOR_FG, fill=False):
    DISPLAY.rect(x, y, w, h, col, fill=fill)

def draw_text_ln(x: int, y: int, txt: str, clr=COLOR_FG):
    lines = txt.split("\n")
    cy = y
    for line in lines:
        DISPLAY.text(line, x, cy, clr)
        cy += CH_H + cfg.txt_h_space


def text_below_board(row, txt, col=COLOR_FG):
    DISPLAY.text(txt, 0, ((row*_CHAR_HEIGHT)+(cfg.screen_h*_CHAR_HEIGHT)), col)
    # WARNING: text does not refresh the display
