import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import os
import random
import requests
import numpy as np
import subprocess
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageOps
from moviepy.editor import *
from moviepy.video.fx.all import lum_contrast

BASE_PATH = "/storage/emulated/0/ChimeraVideoProject/"
ASSET_PATH = os.path.join(BASE_PATH, "assets")
TEMP_PATH = os.path.join(BASE_PATH, "temp")
OUTPUT_NAME = "CHIMERA_CORE_V3_FINAL_IMPACT.mp4"
SCREEN_SIZE = (1920, 1080)
FPS = 24
SOX_BINARY = "sox"

os.makedirs(ASSET_PATH, exist_ok=True)
os.makedirs(TEMP_PATH, exist_ok=True)

AUDIO_BASE = "https://taira-komori.net/sound_os2/"
CHIMERA_SOUNDS = {
    "ANIMALS": "animals01", "COOKING": "cooking01", "DAILY": "daily01",
    "STATIONERY": "daily02", "EATING": "eating01", "ELECTRIC": "electric01",
    "ENV_URBAN": "environment01", "ENV_CONSTRUCT": "environment02",
    "UI_ACTION": "game01", "PURE_HORROR": "horror01", "HORROR_ALT": "horror02",
    "HUMAN": "human01", "JAPANESE": "jidaigeki01", "NATURE": "nature01",
    "OPENCLOSE": "openclose01", "PUTTING": "putting01",
    "ATMOSPHERIC": "sample_noise", "GLITCH_VOID": "sf01"
}

AUDIO_MANIFEST = {
    "ANIMALS01":["bulbul.mp3", "cat1a.mp3", "cat1b.mp3", "crow1.mp3"],
    "HORROR01":["ghost_sigh.mp3", "dark_atmosphere.mp3", "shock1.mp3", "going_mad1.mp3", "coming_of_terror.mp3"],
    "HORROR02":["bangbangbang1.mp3", "hell_fire.mp3", "air_leaking3.mp3", "falling_down.mp3"],
    "SF01":["alien_beam.mp3", "computer_broken.mp3", "electric_shock1.mp3", "ufo.mp3", "cosmic_signal.mp3"],
    "ELECTRIC01":["click.mp3", "camera1.mp3", "pc_keyboard.mp3", "fluorescent_switch1.mp3"],
    "SAMPLE_NOISE":["bg_white_noise1.mp3", "tv_noise1.mp3", "atmosphere_noise2.mp3", "electrical_noise2.mp3"]
}

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
    'PURE_HORROR': {'color': '#ff003c', 'contrast': 2.0, 'bright': -0.1, 'noise': 0.35, 'shake': 40, 'pitch': '-1200', 'sfx': ['PURE_HORROR', 'HORROR_ALT']},
    'GLITCH_VOID': {'color': '#bd00ff', 'contrast': 1.8, 'bright': 0.1, 'noise': 0.45, 'shake': 60, 'pitch': '400', 'sfx': ['GLITCH_VOID', 'SF01']},
    'ELECTRIC':    {'color': '#00f3ff', 'contrast': 1.5, 'bright': 0.05, 'noise': 0.25, 'shake': 30, 'pitch': '200', 'sfx': ['ELECTRIC', 'SF01']},
    'JAPANESE':    {'color': '#ffffff', 'contrast': 1.2, 'bright': -0.05, 'noise': 0.15, 'shake': 20, 'pitch': '0', 'sfx':['JAPANESE', 'NATURE']},
    'UI_ACTION':   {'color': '#00f3ff', 'contrast': 1.3, 'bright': 0.1, 'noise': 0.10, 'shake': 10, 'pitch': '600', 'sfx':['UI_ACTION', 'STATIONERY']}
}

ACTS_CONFIG = [
    {
        "style": "PURE_HORROR", "bg": "39", 
        "segments": [
            {"file": "1.01.wav", "duration": 3.243, "text": "I left my bag on the", "impact": False, "prop": "36"},
            {"file": "1.02.wav", "duration": 1.451, "text": "BENCH.", "impact": True, "prop": "38"},
            {"file": "1.03.wav", "duration": 6.059, "text": "I left my name in the hallway. The student is", "impact": False, "prop": "33"},
            {"file": "1.04.wav", "duration": 1.109, "text": "DEAD.", "impact": True, "prop": "36"}
        ]
    },
    {
        "style": "GLITCH_VOID", "bg": "38", 
        "segments": [
            {"file": "2.01.wav", "duration": 3.499, "text": "Degrees are just ink on", "impact": False, "prop": "34"},
            {"file": "2.02.wav", "duration": 1.792, "text": "ROTTING PAPER.", "impact": True, "prop": "39"},
            {"file": "2.03.wav", "duration": 3.328, "text": "Coding is the only weapon that", "impact": False, "prop": "34"},
            {"file": "2.04.wav", "duration": 1.365, "text": "NEVER DIES.", "impact": True, "prop": "40"}
        ]
    },
    {
        "style": "ELECTRIC", "bg": "40", 
        "segments": [
            {"file": "3.01.wav", "duration": 3.157, "text": "One thousand five hundred Baht and a", "impact": False, "prop": "35"},
            {"file": "3.02.wav", "duration": 1.195, "text": "BROKEN SCREEN.", "impact": True, "prop": "34"},
            {"file": "3.03.wav", "duration": 3.755, "text": "This is my capital. This is my", "impact": False, "prop": "35"},
            {"file": "3.04.wav", "duration": 0.939, "text": "SOVEREIGNTY.", "impact": True, "prop": "vessel"}
        ]
    },
    {
        "style": "JAPANESE", "bg": "vessel", 
        "segments": [
            {"file": "4.01.wav", "duration": 2.560, "text": "True friends are alliances of", "impact": False, "prop": "37"},
            {"file": "4.02.wav", "duration": 1.024, "text": "CONVENIENCE.", "impact": True, "prop": "37"},
            {"file": "4.03.wav", "duration": 5.291, "text": "I don't need your recognition. I only need the signal to be", "impact": False, "prop": "33"},
            {"file": "4.04.wav", "duration": 0.512, "text": "PURE.", "impact": True, "prop": "39"}
        ]
    },
    {
        "style": "UI_ACTION", "bg": "38", 
        "segments": [
            {"file": "5.01.wav", "duration": 1.792, "text": "The Architect is", "impact": False, "prop": "40"},
            {"file": "5.02.wav", "duration": 1.024, "text": "BORN.", "impact": True, "prop": "33"},
            {"file": "5.03.wav", "duration": 2.219, "text": "The One-Person Business has", "impact": False, "prop": "36"},
            {"file": "5.04.wav", "duration": 0.939, "text": "INITIALIZED.", "impact": True, "prop": "40"},
            {"file": "5.05.wav", "duration": 3.072, "text": "ACCESS THE CORE. END OF LINE.", "impact": True, "prop": "35"}
        ]
    }
]

def get_asset(key, url):
    ext = url.split('.')[-1]
    path = os.path.join(ASSET_PATH, f"{key}.{ext}")
    if not os.path.exists(path) or os.path.getsize(path) < 100:
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
            if r.status_code == 200:
                with open(path, "wb") as f: f.write(r.content)
        except: pass
    return path

def build_soundscape(style_key, duration):
    cfg = SONIC_VISUAL_MAP[style_key]
    layers =[]
    for _ in range(6):
        cat_key = random.choice(cfg['sfx'])
        folder = CHIMERA_SOUNDS.get(cat_key, "sample_noise")
        if folder.upper() in AUDIO_MANIFEST:
            fname = random.choice(AUDIO_MANIFEST[folder.upper()])
            url = f"{AUDIO_BASE}{folder}/{fname}"
            path = get_asset(f"sfx_{fname}", url)
            if os.path.exists(path):
                try:
                    c = AudioFileClip(path).volumex(random.uniform(0.1, 0.2))
                    if c.duration > duration: c = c.subclip(0, duration)
                    layers.append(c.set_start(random.uniform(0, max(0, duration-c.duration))))
                except: continue
    return layers

def apply_impact_glitch(frame, intensity, is_impact=False):
    h, w, _ = frame.shape
    img_rgb = frame[:,:,:3].copy()
    
    if is_impact:
        intensity *= 1.5
        if random.random() < 0.3:
            for _ in range(int(intensity * 30)):
                y1 = random.randint(0, h-10)
                h_s = random.randint(2, 20)
                shift = random.randint(-150, 150)
                img_rgb[y1:y1+h_s] = np.roll(img_rgb[y1:y1+h_s], shift, axis=1)
                
        if random.random() > 0.8:
            img_rgb[:,:,0] = np.roll(img_rgb[:,:,0], 15, axis=1)
            img_rgb[:,:,2] = np.roll(img_rgb[:,:,2], -15, axis=1)
            
    noise = np.random.randint(0, 100, (h, w, 3), dtype='uint8')
    img_rgb = ((1 - intensity * 0.3) * img_rgb + (intensity * 0.3) * noise).astype('uint8')
    return img_rgb

def create_impact_text(text, duration, style, is_impact=False):
    f_path = os.path.join(ASSET_PATH, "onryou.ttf")
    if not os.path.exists(f_path):
        f_path = get_asset("onryou", "https://cdn.jsdelivr.net/gh/h3902340/PrisonOfWordFont@master/onryou-Regular.ttf")

    def make_frame(t):
        img = Image.new('RGB', SCREEN_SIZE, (0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        base_size = int(SCREEN_SIZE[1] * 0.15) if is_impact else int(SCREEN_SIZE[1] * 0.08)
        
        try: font = ImageFont.truetype(f_path, base_size)
        except: font = ImageFont.load_default()
        
        wrapped = textwrap.fill(text, width=25 if not is_impact else 15)
        p = min(1.0, t / (duration * 0.9))
        curr = wrapped[:int(len(wrapped) * p)]
        
        bbox = draw.multiline_textbbox((0, 0), curr, font=font, align="center")
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x, y = (SCREEN_SIZE[0]-tw)/2, (SCREEN_SIZE[1]-th)/2
        
        color = style['color'] if is_impact else "#ffffff"
        shadow = "#ffffff" if is_impact else style['color']
        
        jitter = random.randint(-5, 5) if (is_impact and p >= 1.0) else 0
        
        draw.multiline_text((x-6+jitter, y+6+jitter), curr, font=font, fill=shadow, align="center")
        draw.multiline_text((x, y), curr, font=font, fill=color, align="center")
        return np.array(img)

    def make_mask(t):
        img = Image.new('L', SCREEN_SIZE, 0)
        draw = ImageDraw.Draw(img)
        base_size = int(SCREEN_SIZE[1] * 0.15) if is_impact else int(SCREEN_SIZE[1] * 0.08)
        try: font = ImageFont.truetype(f_path, base_size)
        except: font = ImageFont.load_default()
        
        wrapped = textwrap.fill(text, width=25 if not is_impact else 15)
        p = min(1.0, t / (duration * 0.9))
        curr = wrapped[:int(len(wrapped) * p)]
        
        bbox = draw.multiline_textbbox((0, 0), curr, font=font, align="center")
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x, y = (SCREEN_SIZE[0]-tw)/2, (SCREEN_SIZE[1]-th)/2
        draw.multiline_text((x, y), curr, font=font, fill=255, align="center")
        return np.array(img).astype('float32') / 255.0

    txt = VideoClip(make_frame, duration=duration)
    txt.mask = VideoClip(make_mask, duration=duration, ismask=True)
    return txt

def render_act(act_idx):
    conf = ACTS_CONFIG[act_idx]
    s = SONIC_VISUAL_MAP[conf['style']]
    
    bg_p = get_asset(conf['bg'], IMG_URLS[conf['bg']])
    with Image.open(bg_p) as img:
        bg_static = np.array(img.convert("RGB"))

    act_visual_clips = []
    
    for seg in conf['segments']:
        voice_p = os.path.join(BASE_PATH, seg['file'])
        if not os.path.exists(voice_p): 
            print(f"[!] Warning: Missing {seg['file']}")
            continue
        
        mut_p = os.path.join(TEMP_PATH, f"mut_{seg['file']}")
        subprocess.run([SOX_BINARY, voice_p, mut_p, "pitch", s['pitch'], "reverb", "50", "contrast", "20"], capture_output=True)
        
        v_clip = AudioFileClip(mut_p if os.path.exists(mut_p) else voice_p).volumex(2.5)
        dur = v_clip.duration
        
        if seg.get('impact'):
            sfx_folder = CHIMERA_SOUNDS.get(random.choice(s['sfx']))
            if sfx_folder and sfx_folder.upper() in AUDIO_MANIFEST:
                sfx_file = random.choice(AUDIO_MANIFEST[sfx_folder.upper()])
                sfx_path = get_asset(f"sfx_{sfx_file}", f"{AUDIO_BASE}{sfx_folder}/{sfx_file}")
                try:
                    impact_sfx = AudioFileClip(sfx_path).volumex(0.8)
                    if impact_sfx.duration > dur: impact_sfx = impact_sfx.subclip(0, dur)
                    v_clip = CompositeAudioClip([v_clip, impact_sfx]).set_duration(dur)
                except: pass
        
        bg = ImageClip(bg_static).resize(SCREEN_SIZE).set_duration(dur)
        bg = lum_contrast(bg, lum=s['bright'], contrast=s['contrast']-1)
        
        act_layers = [bg]
        
        if seg.get('prop'):
            pp = get_asset(seg['prop'], IMG_URLS[seg['prop']])
            if os.path.exists(pp):
                with Image.open(pp) as pimg:
                    p_rgba = pimg.convert("RGBA")
                    p_rgb = np.array(p_rgba.convert("RGB"))
                    p_mask = np.array(p_rgba)[:,:,3].astype('float32') / 255.0
                
                p_clip = ImageClip(p_rgb).set_duration(dur)
                p_clip.mask = ImageClip(p_mask, ismask=True).set_duration(dur)
                
                scale_target = 0.8 if seg.get('impact') else 0.4
                p_clip = p_clip.resize(height=SCREEN_SIZE[1] * scale_target)
                p_clip = p_clip.set_position("center")
                
                if seg.get('impact'):
                    p_clip = p_clip.fl(lambda gf, t: np.roll(gf(t), int(s['shake'] * np.sin(t*50)), axis=1))
                    
                act_layers.append(p_clip.set_opacity(0.9))

        txt = create_impact_text(seg['text'], dur, s, is_impact=seg.get('impact'))
        txt = txt.set_position("center")
        act_layers.append(txt)
        
        seg_composite = CompositeVideoClip(act_layers, size=SCREEN_SIZE).set_duration(dur).set_audio(v_clip)
        seg_composite = seg_composite.fl_image(lambda f: apply_impact_glitch(f, s['noise'], seg.get('impact')))
        act_visual_clips.append(seg_composite)

    if not act_visual_clips:
        return None
        
    return concatenate_videoclips(act_visual_clips, method="chain")

print("[NEXUS] INITIATING ATOMIC IMPACT RENDER V3.7...")
final_acts = [clip for i in range(len(ACTS_CONFIG)) if (clip := render_act(i)) is not None]
if final_acts:
    concatenate_videoclips(final_acts, method="chain").write_videofile(
        os.path.join(BASE_PATH, OUTPUT_NAME),
        fps=FPS, codec="libx264", audio_codec="aac", threads=4, preset="ultrafast"
    )
else:
    print("[FATAL] No valid audio fragments found in /storage/emulated/0/ChimeraVideoProject/")