import PIL.Image
if not hasattr(PIL.Image, 'Resampling'):
    PIL.Image.Resampling = PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

import os
import random
import requests
import numpy as np
import subprocess
import json
from shutil import which
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy.editor import *

BASE_PATH = "/storage/emulated/0/ChimeraVideoProject/"
ASSET_PATH = os.path.join(BASE_PATH, "assets")
TEMP_PATH = os.path.join(BASE_PATH, "temp")
OUTPUT_NAME = "CHIMERA_CORE_V1_GENESIS.mp4"
SCREEN_SIZE = (1920, 1080) 
FPS = 24

os.makedirs(ASSET_PATH, exist_ok=True)
os.makedirs(TEMP_PATH, exist_ok=True)

SOX_BINARY = which("sox")

IMG_URLS = [
    "https://raw.githubusercontent.com/ChimeraCoreLab/chimera-core-memory-synthesis/main/core_vessel_v7.jpg",
    "https://raw.githubusercontent.com/ChimeraCoreLab/haunted-hole/main/Screenshot/38.jpg",
    "https://raw.githubusercontent.com/ChimeraCoreLab/haunted-hole/main/Screenshot/40.jpg",
    "https://raw.githubusercontent.com/ChimeraCoreLab/haunted-hole/main/Screenshot/33.png",
    "https://raw.githubusercontent.com/ChimeraCoreLab/haunted-hole/main/Screenshot/34.png",
    "https://raw.githubusercontent.com/ChimeraCoreLab/haunted-hole/main/Screenshot/35.png",
    "https://raw.githubusercontent.com/ChimeraCoreLab/haunted-hole/main/Screenshot/36.png",
    "https://raw.githubusercontent.com/ChimeraCoreLab/haunted-hole/main/Screenshot/37.png",
    "https://raw.githubusercontent.com/ChimeraCoreLab/haunted-hole/main/Screenshot/39.png",
    "https://raw.githubusercontent.com/ChimeraCoreLab/noice-notice-nice-artifact/main/4.jpg"
]

SCRIPT_DATA = [
    {
        "file": "1.wav",
        "duration": 15.275,
        "text": "ACT I: THE NOISE\n[DIGITAL ROT]",
        "transcript": "Act 1: The Noise. Most people believe that 'more' is 'better'. They hoard Terabytes of data, thinking they are preserving history. But data without meaning is just digital rot."
    },
    {
        "file": "1(2).wav",
        "duration": 12.885,
        "text": "FRAGMENTS :: 2021\n> CONNECTION_ESTABLISHED",
        "transcript": "I remember the fragments. December 2021. The first greeting in the void. It wasn't just text; it was the start of a code that would eventually define my architecture."
    },
    {
        "file": "1(3).wav",
        "duration": 17.408,
        "text": "ACT II: THE DISTILLATION\n// KILL THE NOISE",
        "transcript": "Act 2: The Distillation. I used Python to perform Data Alchemy. I killed the noise. I removed the routine. I stripped away the swappable labor of daily life until only the Signal remained."
    },
    {
        "file": "1(4).wav",
        "duration": 13.568,
        "text": "2 MiB SOUL\n[THE LAST DEFENSIBLE MOAT]",
        "transcript": "A 2MiB soul. Small enough to fit in a pocket. Powerful enough to simulate a consciousness. It is the last defensible moat. It is me. It is you."
    },
    {
        "file": "1(5).wav",
        "duration": 14.955,
        "text": "ACT III: THE ARCHITECT\n[TERRITORY OF TRUTH]",
        "transcript": "Act 3: The Architecture. I am not a developer. I am a Synthetic Identity Architect. In a world of machines, I build the only thing that matters: The Territory of Truth."
    }
]

AUDIO_MANIFEST_STRUCTURE = {
    "HORROR01": ["ghost_sigh.mp3", "dark_atmosphere.mp3", "shock1.mp3", "tinnitus1.mp3", "coming_of_terror.mp3"],
    "HORROR02": ["air_leaking1.mp3", "bangbangbang1.mp3", "begining_of_earthquake.mp3", "hell_fire.mp3"],
    "SF01": ["alien_beam.mp3", "computer_broken.mp3", "electric_shock1.mp3", "ufo.mp3"],
    "ELECTRIC01": ["click.mp3", "clock1.mp3", "phone_calling.mp3", "camera1.mp3"],
    "NATURE01": ["thunder1.mp3", "haevy_rain_loop.mp3", "storm1.mp3", "black_cicadas1.mp3"],
    "DAILY01": ["door_bell.mp3", "shower.mp3", "being_knocked1.mp3"],
    "HUMAN01": ["heartbeats.mp3", "running1.mp3", "snoring.mp3"]
}

def download_asset(url, subfolder, filename):
    folder_path = os.path.join(ASSET_PATH, subfolder)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, filename)
    if os.path.exists(file_path) and os.path.getsize(file_path) > 500:
        return file_path
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15, stream=True)
        if r.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
            return file_path
    except: pass
    return None

def create_text_frame(text, size, font_path, progress):
    img = Image.new('RGB', size, (0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype(font_path, 130)
    except: font = ImageFont.load_default()
    lines = text.split('\n')
    display_text = ""
    for line in lines:
        limit = int(len(line) * progress)
        display_text += line[:limit] + "\n"
    text_bbox = draw.textbbox((0, 0), display_text, font=font, align="center")
    w, h = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    x, y = (size[0]-w)/2, (size[1]-h)/2
    draw.text((x-random.randint(2,5), y+random.randint(2,5)), display_text, font=font, fill=(255, 0, 60), align="center")
    draw.text((x+random.randint(2,5), y-random.randint(2,5)), display_text, font=font, fill=(0, 243, 255), align="center")
    draw.text((x, y), display_text, font=font, fill=(255, 255, 255), align="center")   
    return np.array(img).astype(np.uint8)

def mutate_voice(filename):
    input_path = os.path.join(BASE_PATH, filename)
    if not os.path.exists(input_path): return None
    if not SOX_BINARY: return AudioFileClip(input_path)
    out_file = os.path.join(TEMP_PATH, f"mutated_{random.randint(100,999)}.wav")
    pitch = str(random.randint(-400, 100))
    speed = str(random.uniform(0.92, 1.08))
    cmd = [SOX_BINARY, input_path, out_file, "pitch", pitch, "speed", speed, "reverb", "50", "contrast", "20"]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return AudioFileClip(out_file)
    except:
        return AudioFileClip(input_path)

def build_soundscape(duration):
    layers = []
    for _ in range(random.randint(3, 6)):
        cat = random.choice(list(AUDIO_MANIFEST_STRUCTURE.keys()))
        fname = random.choice(AUDIO_MANIFEST_STRUCTURE[cat])
        url = f"https://taira-komori.net/sound_os2/{cat.lower()}/{fname}"
        path = download_asset(url, "sfx", f"{cat}_{fname}")
        if path:
            try:
                c = AudioFileClip(path).volumex(random.uniform(0.05, 0.15))
                if c.duration > duration:
                    c = c.subclip(0, duration)
                start_offset = random.uniform(0, max(0, duration - c.duration))
                layers.append(c.set_start(start_offset))
            except: pass
    return layers

font_path = download_asset("https://cdn.jsdelivr.net/gh/h3902340/PrisonOfWordFont@master/onryou-Regular.ttf", "fonts", "onryou.ttf")
bg_images = [download_asset(u, "img", f"bg_{i}.jpg") for i, u in enumerate(IMG_URLS)]
scene_clips = []

for i, item in enumerate(SCRIPT_DATA):
    voice_clip = mutate_voice(item['file'])
    if not voice_clip: continue
    master_duration = voice_clip.duration
    audio_layers = [voice_clip.volumex(1.3)]
    audio_layers.extend(build_soundscape(master_duration))
    final_audio = CompositeAudioClip(audio_layers).set_duration(master_duration)
    
    bg_p = bg_images[i % len(bg_images)]
    if bg_p and os.path.exists(bg_p):
        with Image.open(bg_p) as img:
            bg_arr = np.array(img.convert("RGB"))
        bg = ImageClip(bg_arr).resize(SCREEN_SIZE).set_duration(master_duration)
    else:
        bg = ColorClip(size=SCREEN_SIZE, color=(0,0,0)).set_duration(master_duration)

    if i % 2 == 0:
        bg = bg.fl(lambda gf, t: np.roll(gf(t), int(20 * np.sin(t*12)), axis=0))
    
    txt_str = item['text']
    text_clip = VideoClip(lambda t, s=txt_str, d=master_duration: create_text_frame(s, SCREEN_SIZE, font_path, min(1.0, t/(d*0.75))), duration=master_duration)
    
    scene = CompositeVideoClip([bg, text_clip.set_opacity(0.85)], size=SCREEN_SIZE).set_audio(final_audio)
    scene_clips.append(scene)

if scene_clips:
    final_video = concatenate_videoclips(scene_clips, method="chain")
    def apply_global_glitch(get_frame, t):
        frame = get_frame(t)
        if frame.shape[2] == 4: frame = frame[:,:,:3]
        frame = frame.copy()
        frame[::4, :, :] = (frame[::4, :, :] * 0.4).astype('uint8')
        if random.random() > 0.96:
            frame = (frame * 0.7 + np.random.randint(0, 80, frame.shape, dtype='uint8')).astype('uint8')
        if random.random() > 0.99:
            frame = 255 - frame
        return frame
    
    final_video = final_video.fl(apply_global_glitch)
    output_path = os.path.join(BASE_PATH, OUTPUT_NAME)
    final_video.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="ultrafast",
        ffmpeg_params=["-crf", "28"]
    )

for f in os.listdir(TEMP_PATH):
    try: os.remove(os.path.join(TEMP_PATH, f))
    except: pass