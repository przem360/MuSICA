import machine, time
import math

# ------------------------------
# CONFIG
# ------------------------------
SAMPLE_RATE = 22050 
BUFFER = 512
TICK_RATE = 50       
SAMPLES_PER_TICK = SAMPLE_RATE // TICK_RATE

i2s = machine.I2S(
    0,
    sck=machine.Pin(41),
    ws=machine.Pin(43),
    sd=machine.Pin(42),
    mode=machine.I2S.TX,
    bits=16,
    format=machine.I2S.MONO,
    rate=SAMPLE_RATE,
    ibuf=2048
)

 # ------------------------------

# FREQ TABLE AND LUT FOR SINE

# ------------------------------

FREQ_TABLE = {
    'C':  [16.35, 32.70, 65.41, 130.81, 261.63, 523.25, 1046.50, 2093.00],
    'C#': [17.32, 34.65, 69.30, 138.59, 277.18, 554.37, 1108.73, 2217.46],
    'D':  [18.35, 36.71, 73.42, 146.83, 293.66, 587.33, 1174.66, 2349.32],
    'D#': [19.45, 38.89, 77.78, 155.56, 311.13, 622.25, 1244.51, 2489.02],
    'E':  [20.60, 41.20, 82.41, 164.81, 329.63, 659.25, 1318.51, 2637.02],
    'F':  [21.83, 43.65, 87.31, 174.61, 349.23, 698.46, 1396.91, 2793.83],
    'F#': [23.12, 46.25, 92.50, 185.00, 369.99, 739.99, 1479.98, 2959.96],
    'G':  [24.50, 49.00, 98.00, 196.00, 392.00, 783.99, 1567.98, 3135.96],
    'G#': [25.96, 51.91, 103.83, 207.65, 415.30, 830.61, 1661.22, 3322.44],
    'A':  [27.50, 55.00, 110.00, 220.00, 440.00, 880.00, 1760.00, 3520.00],
    'A#': [29.14, 58.27, 116.54, 233.08, 466.16, 932.32, 1864.64, 3729.31],
    'B':  [30.87, 61.74, 123.47, 246.94, 493.88, 987.76, 1975.52, 3951.04]
}


SINE_LUT = [math.sin(2 * math.pi * i / 256) for i in range(256)] 

# wave generators

def gen_square(phase):
    return 0.5 if phase < 0.5 else -0.5

def gen_saw(phase):
    return 2.0 * phase - 1.0

def gen_tri(phase):
    return 4.0 * phase - 1.0 if phase < 0.5 else 3.0 - 4.0 * phase

def gen_sine(phase):
    return SINE_LUT[int(phase * 255) & 255]

def gen_noise(phase):
    return (time.ticks_cpu() & 0x7FFF) / 32768.0

WAVE_MAP = {0: gen_square, 1: gen_saw, 2: gen_tri, 3: gen_noise, 4: gen_sine}

# parser

def parse_to_ticks(mml):
    print("Got mml string: "+mml)
    tempo, octave, length, vol, wave = 140, 4, 4, 32, 0
    ticks = []
    
    FLAT_MAP = {
        'C-': ('B', -1), 'D-': ('C#', 0), 'E-': ('D#', 0),
        'F-': ('E', 0), 'G-': ('F#', 0), 'A-': ('G#', 0),
        'B-': ('A#', 0)
    }
    
    def add_event(f, v, w, dur_ms):
        # ! Using round instead of int to avoid timing issues
        num_ticks = max(1, round((dur_ms / 1000) * TICK_RATE))
        for _ in range(num_ticks):
            # For the purpose of future chord implementation
            ticks.append(([f], v / 64.0, w))

    i = 0
    while i < len(mml):
        ch = mml[i].lower()
        
        if ch.isspace():
            i += 1
            continue

        if ch in "cdefgab":
            note = ch.upper()
            print("Found note: "+note)
            i += 1
            
            modifier = "" # do we even need this? see below
            if i < len(mml) and mml[i] in "+#-":
                modifier = mml[i]
                print("Found modifier: "+modifier)
                i += 1
            else:
                modifier = "!" # This is hack :D Well, micropython is stubborn and keeps the value if trying to set it to empty string.
            
            current_note_dur = length
            if i < len(mml) and mml[i].isdigit():
                num_str = ""
                while i < len(mml) and mml[i].isdigit():
                    num_str += mml[i]
                    i += 1
                print("Found rhythmic value of "+num_str)
                current_note_dur = int(num_str)
            
            current_octave = octave
            note_to_find = note
            
            if modifier in "+#":
                if note == 'E': note_to_find = 'F'
                elif note == 'B': 
                    note_to_find = 'C'
                    current_octave += 1
                else: note_to_find = note + "#"
            elif modifier == "-":
                note_to_find, octave_offset = FLAT_MAP[note + "-"]
                current_octave += octave_offset

            current_octave = max(0, min(7, current_octave))
            print("note_to_find: "+str(note_to_find))
            freq = FREQ_TABLE[note_to_find][current_octave]
            dur = (60000 / tempo * 4 / current_note_dur)
            add_event(freq, vol, wave, dur)
            continue

        elif ch == "r":
            i += 1
            current_rest_dur = length
            if i < len(mml) and mml[i].isdigit():
                num_str = ""
                while i < len(mml) and mml[i].isdigit():
                    num_str += mml[i]
                    i += 1
                current_rest_dur = int(num_str)
            
            dur = (60000 / tempo * 4 / current_rest_dur)
            add_event(0, 0, wave, dur)
            continue

        elif ch == "t":
            i += 1; n = ""
            while i < len(mml) and mml[i].isdigit(): n += mml[i]; i += 1
            if n: tempo = int(n)
        elif ch == "v":
            i += 1; n = ""
            while i < len(mml) and mml[i].isdigit(): n += mml[i]; i += 1
            if n: vol = int(n)
        elif ch == "@":
            i += 1; n = ""
            while i < len(mml) and mml[i].isdigit(): n += mml[i]; i += 1
            if n: wave = int(n)
        elif ch == "o":
            i += 1
            if i < len(mml) and mml[i].isdigit():
                octave = int(mml[i]); i += 1
        elif ch == "<": octave -= 1; i += 1
        elif ch == ">": octave += 1; i += 1
        elif ch == "l":
            i += 1; n = ""
            while i < len(mml) and mml[i].isdigit(): n += mml[i]; i += 1
            if n: length = int(n)
        else:
            i += 1
            
    return ticks

# arpeggio playback

class ArpEngine:
    def __init__(self, tracks_mml):
        # Removing empty tracks
        active_mml = [t for t in tracks_mml if t.strip()]
        
        self.tracks = [parse_to_ticks(t) for t in active_mml]
        self.num_tracks = len(self.tracks)
        
        if self.num_tracks == 0:
            raise ValueError("Minimum one MML track is required!")

        self.max_len = max(len(t) for t in self.tracks)
        self.current_tick = 0
        self.phases = [0.0] * self.num_tracks
        self.arp_step = 0

    def get_sample(self):
        self.arp_step = (self.arp_step + 1) % self.num_tracks
        track = self.tracks[self.arp_step]
        
        if self.current_tick >= len(track):
            return 0

        # freq_data to teraz LISTA, np. [440.0] lub [261.6, 329.6, 392.0]
        freq_data, vol, wave_type = track[self.current_tick]
        
        # Jeśli lista zawiera 0 (pauza) lub jest pusta
        if not freq_data or freq_data[0] == 0: 
            return 0

        # Select frequenct
        # If it is a chorg - arp it, if note, just take first value
        if len(freq_data) > 1:
            idx = (time.ticks_ms() // 4) % len(freq_data)
            freq = freq_data[idx]
        else:
            freq = freq_data[0]

        self.phases[self.arp_step] = (self.phases[self.arp_step] + (freq / SAMPLE_RATE)) % 1.0
        
        wave_func = WAVE_MAP.get(wave_type, gen_square)
        
        return (wave_func(self.phases[self.arp_step]) * vol) / self.num_tracks

    def next_tick(self):
        self.current_tick += 1

def play_arp(tracks_mml):
    engine = ArpEngine(tracks_mml)
    buf = bytearray(BUFFER * 2)
    
    while engine.current_tick < engine.max_len:
        for _ in range(0, SAMPLES_PER_TICK, BUFFER // 2):
            for i in range(BUFFER // 2):
                sample = engine.get_sample()
                s16 = int(sample * 30000) 
                buf[2*i] = s16 & 0xFF
                buf[2*i+1] = (s16 >> 8) & 0xFF
            i2s.write(buf)
        engine.next_tick()

# test
# @0: square, @1: saw, @2: triangle, @3: noise

tracks = [
    "t120 @0 o5 c#4 c4 e4 g4",
    #"t120 @0 o4 [ceg]4 [dfa]4",
    "t120 @0 o3 c4 r4 a4 g4",  # Prosty bas
    #"t120 @0 o5 v16 [egb]4. [dfa]8"
]

play_arp(tracks)


