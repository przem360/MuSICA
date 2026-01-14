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
    tempo, octave, length, vol, wave = 140, 4, 8, 32, 0
    ticks = []
    
    def add_event(f, v, w, dur_ms):
        num_ticks = int((dur_ms / 1000) * TICK_RATE)
        for _ in range(max(1, num_ticks)):
            ticks.append((f, v / 64.0, w))

    i = 0
    while i < len(mml):
        ch = mml[i].lower()
        if ch in "cdefgab":
            note = ch.upper()
            i += 1
            if i < len(mml) and mml[i] in "+#": note += "#"; i += 1
            freq = FREQ_TABLE[note][octave]
            dur = (60000 / tempo * 4 / length)
            add_event(freq, vol, wave, dur)
        elif ch == "r":
            i += 1; add_event(0, 0, wave, (60000 / tempo * 4 / length))
        elif ch == "t":
            i += 1; n = ""; 
            while i < len(mml) and mml[i].isdigit(): n += mml[i]; i += 1
            tempo = int(n)
        elif ch == "v":
            i += 1; n = ""; 
            while i < len(mml) and mml[i].isdigit(): n += mml[i]; i += 1
            vol = int(n)
        elif ch == "@":
            i += 1; n = "";
            while i < len(mml) and mml[i].isdigit(): n += mml[i]; i += 1
            wave = int(n)
        elif ch == "o":
            i += 1; octave = int(mml[i]); i += 1
        elif ch == "<": octave -= 1; i += 1
        elif ch == ">": octave += 1; i += 1
        elif ch == "l":
            i += 1; n = "";
            while i < len(mml) and mml[i].isdigit(): n += mml[i]; i += 1
            length = int(n)
        else: i += 1
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
        # make sure that Arpeggio picks only available tracks
        self.arp_step = (self.arp_step + 1) % self.num_tracks
        
        track = self.tracks[self.arp_step]
        
        if self.current_tick >= len(track):
            return 0

        freq, vol, wave_type = track[self.current_tick]
        if freq == 0: 
            return 0

        # Update channels phase
        self.phases[self.arp_step] = (self.phases[self.arp_step] + (freq / SAMPLE_RATE)) % 1.0
        
        # Selecting generator
        wave_func = WAVE_MAP.get(wave_type, gen_square)
        
        # There can be less than 4 tracks, 
        # so we need to compensate volume. In 1 track arpeggio 
        # we will have 100% time, in 4-tracks 25%.
        # Div by number of tracks to avoid clipping.
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
    "t80 @0 l8 v16 c e g > c <",   # Square
    "t80 @1 l8 v16 r4 a4 c4 r4",   # Saw
    "t80 @2 l8 v16 c  g  a  c",    # Triangle
    "t80 @3 l8 v16 r4 e4 r4 r4"    # Noise
]

play_arp(tracks)
