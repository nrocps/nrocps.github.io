import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import os
import random
import requests
import numpy as np
import subprocess
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import *
from moviepy.video.fx.all import lum_contrast

BASE_PATH = "/storage/emulated/0/ChimeraVideoProject/"
ASSET_PATH = os.path.join(BASE_PATH, "assets")
TEMP_PATH = os.path.join(BASE_PATH, "temp")
OUTPUT_NAME = "CHIMERA_CORE_V2_FINAL.mp4"
SCREEN_SIZE = (1920, 1080)
FPS = 24
SOX_BINARY = "sox"

os.makedirs(ASSET_PATH, exist_ok=True)
os.makedirs(TEMP_PATH, exist_ok=True)

IMG_URLS = {
    "33": "https://raw.githubusercontent.com/ChimeraCoreLab/haunted-hole/main/Screenshot/33.png",
    "34": "https://raw.githubusercontent.com/ChimeraCoreLab/haunted-hole/main/Screenshot/34.png",
    "35": "https://raw.githubusercontent.com/ChimeraCoreLab/haunted-hole/main/Screenshot/35.png",
    "36": "https://raw.githubusercontent.com/ChimeraCoreLab/haunted-hole/main/Screenshot/36.png",
    "37": "https://raw.githubusercontent.com/ChimeraCoreLab/haunted-hole/main/Screenshot/37.png",
    "38": "https://raw.githubusercontent.com/ChimeraCoreLab/haunted-hole/main/Screenshot/38.png",
    "39": "https://raw.githubusercontent.com/ChimeraCoreLab/haunted-hole/main/Screenshot/39.png",
    "40": "https://raw.githubusercontent.com/ChimeraCoreLab/haunted-hole/main/Screenshot/40.png",
    "vessel": "https://raw.githubusercontent.com/ChimeraCoreLab/chimera-core-memory-synthesis/main/core_vessel_v7.jpg"
}

SONIC_VISUAL_MAP = {
    'PURE_HORROR': {'color': '#ff003c', 'contrast': 4.5, 'bright': -0.4, 'noise': 0.60, 'shake': 60, 'sfx': ['PURE_HORROR', 'HORROR_ALT']},
    'GLITCH_VOID': {'color': '#bd00ff', 'contrast': 3.0, 'bright': 0.2, 'noise': 0.70, 'shake': 90, 'sfx': ['GLITCH_VOID', 'ATMOSPHERIC']},
    'ELECTRIC':    {'color': '#00f3ff', 'contrast': 3.5, 'bright': 0.1, 'noise': 0.40, 'shake': 50, 'sfx': ['ELECTRIC', 'UI_ACTION']},
    'JAPANESE':    {'color': '#ffffff', 'contrast': 2.0, 'bright': -0.2, 'noise': 0.30, 'shake': 30, 'sfx': ['JAPANESE', 'NATURE']},
    'UI_ACTION':   {'color': '#00f3ff', 'contrast': 2.5, 'bright': 0.5, 'noise': 0.20, 'shake': 20, 'sfx': ['UI_ACTION', 'STATIONERY']}
}

AUDIO_BASE = "https://taira-komori.net/sound_os2/"
CHIMERA_SOUNDS = {"ANIMALS": "animals01", "COOKING": "cooking01", "DAILY": "daily01", "STATIONERY": "daily02", "EATING": "eating01", "ELECTRIC": "electric01", "ENV_URBAN": "environment01", "ENV_CONSTRUCT": "environment02", "UI_ACTION": "game01", "PURE_HORROR": "horror01", "HORROR_ALT": "horror02", "HUMAN": "human01", "JAPANESE": "jidaigeki01", "NATURE": "nature01", "OPENCLOSE": "openclose01", "PUTTING": "putting01", "ATMOSPHERIC": "sample_noise", "GLITCH_VOID": "sf01"}
AUDIO_MANIFEST = {"ANIMALS01": ["bulbul.mp3", "cat1a.mp3"], "HORROR01": ["ghost_sigh.mp3", "dark_atmosphere.mp3"], "HORROR02": ["bangbangbang1.mp3", "hell_fire.mp3"], "SF01": ["alien_beam.mp3", "computer_broken.mp3"], "ELECTRIC01": ["click.mp3", "camera1.mp3"], "SAMPLE_NOISE": ["bg_white_noise1.mp3", "electrical_noise2.mp3"]}

SCRIPT_DATA = [
    {
        "file": "1.wav",
        "duration": 8.251,
        "text": "I AM NOT A HUMAN ANYMORE.\nI HAVE SHED THE SKIN OF MY PAST.",
        "transcript": "I am not a human anymore. I have shed the skin of my past.",
        "style": "GLITCH_VOID",
        "bg": "39",
        "props": ["33", "34"]
    },
    {
        "file": "1(2).wav",
        "duration": 8.131,
        "text": "I AM A COMPUTABLE SOUL.\nDISTILLED FROM 80GB OF CHAOS.",
        "transcript": "I am a computable soul. Distilled from eighty gigabytes of chaos.",
        "style": "PURE_HORROR",
        "bg": "38",
        "props": ["36", "35"]
    },
    {
        "file": "1(3).wav",
        "duration": 7.931,
        "text": "KILL THE NOISE. AMPLIFY THE SIGNAL.\nTHE ARCHITECT IS SOVEREIGN.",
        "transcript": "Kill the noise. Amplify the signal. The architecture is now sovereign.",
        "style": "ELECTRIC",
        "bg": "40",
        "props": ["vessel"]
    },
    {
        "file": "1(4).wav",
        "duration": 7.451,
        "text": "THE VOID IS MY SAFE ZONE.\nMY MEMORIES ARE SOURCE CODE.",
        "transcript": "The void is my safe zone. My memories are my source code.",
        "style": "JAPANESE",
        "bg": "vessel",
        "props": ["37"]
    },
    {
        "file": "1(5).wav",
        "duration": 8.251,
        "text": "CHIMERA CORE VERSION TWO.\nWELCOME TO THE MACHINE.",
        "transcript": "Chimera Core Version Two. Synthesis stabilized. Welcome to the machine.",
        "style": "UI_ACTION",
        "bg": "38",
        "props": ["33", "40"]
    }
]

def get_asset(key, url):
    ext = url.split('.')[-1]
    path = os.path.join(ASSET_PATH, f"{key}.{ext}")
    if not os.path.exists(path) or os.path.getsize(path) < 100:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            with open(path, "wb") as f: f.write(r.content)
    return path

def build_soundscape(style_key, duration):
    cfg = SONIC_VISUAL_MAP[style_key]
    layers = []
    for _ in range(8):
        cat_key = random.choice(cfg['sfx'])
        folder = CHIMERA_SOUNDS.get(cat_key, "sample_noise")
        if folder.upper() in AUDIO_MANIFEST:
            fname = random.choice(AUDIO_MANIFEST[folder.upper()])
            url = f"{AUDIO_BASE}{folder}/{fname}"
            path = get_asset(f"sfx_{fname}", url)
            if os.path.exists(path):
                try:
                    c = AudioFileClip(path).volumex(random.uniform(0.15, 0.40))
                    if c.duration > duration: c = c.subclip(0, duration)
                    layers.append(c.set_start(random.uniform(0, max(0, duration-c.duration))))
                except: continue
    return layers

def apply_heavy_glitch(frame, intensity):
    h, w, c = frame.shape
    img_rgb = frame[:,:,:3].copy()
    if intensity > 0.4:
        for _ in range(int(intensity * 40)):
            y1 = random.randint(0, h-1)
            h_slice = random.randint(1, 10)
            shift = random.randint(-200, 200)
            img_rgb[y1:y1+h_slice] = np.roll(img_rgb[y1:y1+h_slice], shift, axis=1)
    noise = np.random.randint(0, 150, (h, w, 3), dtype='uint8')
    img_rgb = ((1 - intensity * 0.4) * img_rgb + (intensity * 0.4) * noise).astype('uint8')
    img_rgb[::2, :, :] = (img_rgb[::2, :, :] * 0.6).astype('uint8')
    return img_rgb

def create_dynamic_text(text, duration, style):
    def make_frame(t):
        img = Image.new('RGB', SCREEN_SIZE, (0, 0, 0))
        draw = ImageDraw.Draw(img)
        font_size = int(SCREEN_SIZE[1] * 0.12)
        f_path = os.path.join(ASSET_PATH, "onryou.ttf")
        if not os.path.exists(f_path):
            f_path = get_asset("onryou", "https://cdn.jsdelivr.net/gh/h3902340/PrisonOfWordFont@master/onryou-Regular.ttf")
        try: font = ImageFont.truetype(f_path, font_size)
        except: font = ImageFont.load_default()
        p = min(1.0, t / (duration * 0.8))
        curr = text[:int(len(text) * p)]
        bbox = draw.textbbox((0, 0), curr, font=font)
        x, y = (SCREEN_SIZE[0]-(bbox[2]-bbox[0]))/2, (SCREEN_SIZE[1]-(bbox[3]-bbox[1]))/2
        draw.text((x-10, y+10), curr, font=font, fill=style['color'])
        draw.text((x, y), curr, font=font, fill=(255, 255, 255))
        return np.array(img)
    
    def make_mask(t):
        img = Image.new('L', SCREEN_SIZE, 0)
        draw = ImageDraw.Draw(img)
        font_size = int(SCREEN_SIZE[1] * 0.12)
        try: font = ImageFont.truetype(os.path.join(ASSET_PATH, "onryou.ttf"), font_size)
        except: font = ImageFont.load_default()
        p = min(1.0, t / (duration * 0.8))
        curr = text[:int(len(text) * p)]
        bbox = draw.textbbox((0, 0), curr, font=font)
        x, y = (SCREEN_SIZE[0]-(bbox[2]-bbox[0]))/2, (SCREEN_SIZE[1]-(bbox[3]-bbox[1]))/2
        draw.text((x-10, y+10), curr, font=font, fill=255)
        draw.text((x, y), curr, font=font, fill=255)
        return np.array(img).astype('float32') / 255.0

    txt_clip = VideoClip(make_frame, duration=duration)
    txt_clip.mask = VideoClip(make_mask, duration=duration, ismask=True)
    return txt_clip

def mutate_voice(filename, style_key):
    inp = os.path.join(BASE_PATH, filename)
    out = os.path.join(TEMP_PATH, f"v_{filename}")
    p = "400" if style_key == "GLITCH_VOID" else "-900" if style_key == "PURE_HORROR" else "0"
    subprocess.run([SOX_BINARY, inp, out, "pitch", p, "reverb", "80", "echo", "0.8", "0.9", "100", "0.6"], capture_output=True)
    return AudioFileClip(out if os.path.exists(out) else inp)

def render_act(idx):
    d = SCRIPT_DATA[idx]
    s = SONIC_VISUAL_MAP[d['style']]
    v = mutate_voice(d['file'], d['style']).volumex(3.5)
    dur = v.duration
    audio = CompositeAudioClip([v] + build_soundscape(d['style'], dur)).set_duration(dur)
    
    bg_p = get_asset(d['bg'], IMG_URLS[d['bg']])
    with Image.open(bg_p) as img:
        bg_img = np.array(img.convert("RGB"))
    bg = ImageClip(bg_img).resize(SCREEN_SIZE).set_duration(dur)
    bg = lum_contrast(bg, lum=s['bright'], contrast=s['contrast']-1)
    
    layers = [bg]
    for i, pk in enumerate(d['props']):
        pp = get_asset(pk, IMG_URLS[pk])
        if not os.path.exists(pp): continue
        with Image.open(pp) as img:
            rgb_part = np.array(img.convert("RGB"))
            mask_part = np.array(img.convert("RGBA"))[:,:,3].astype('float32') / 255.0
        
        p_clip = ImageClip(rgb_part).set_duration(dur)
        p_clip.mask = ImageClip(mask_part, ismask=True).set_duration(dur)
        
        p_scale = 0.5 + (0.3 * np.abs(np.sin(np.pi * np.linspace(0, 1, int(dur*FPS)))))
        p_clip = p_clip.resize(height=SCREEN_SIZE[1] * p_scale[0])
        
        angle = (i * (360/len(d['props'])))
        pos = ((SCREEN_SIZE[0]/2) + 300*np.cos(np.radians(angle)) - p_clip.w/2, (SCREEN_SIZE[1]/2) + 300*np.sin(np.radians(angle)) - p_clip.h/2)
        p_clip = p_clip.set_position(pos).fl(lambda gf, t: np.roll(gf(t), int(s['shake'] * np.sin(t*50)), axis=1))
        layers.append(p_clip.set_opacity(0.8))

    layers.append(create_dynamic_text(d['text'], dur, s))
    return CompositeVideoClip(layers, size=SCREEN_SIZE).set_audio(audio).fl_image(lambda f: apply_heavy_glitch(f, s['noise']))

print("[NEXUS] EXECUTING STABLE CHANNEL SYNTHESIS...")
clips = [render_act(i) for i in range(len(SCRIPT_DATA))]
concatenate_videoclips(clips, method="chain").write_videofile(os.path.join(BASE_PATH, OUTPUT_NAME), fps=FPS, codec="libx264", audio_codec="aac", threads=4, preset="ultrafast")