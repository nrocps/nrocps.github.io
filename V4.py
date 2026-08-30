import os
import random
import requests
import numpy as np
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
if not hasattr(PIL.Image, 'Resampling'):
    class FakeResampling: LANCZOS = PIL.Image.ANTIALIAS
    PIL.Image.Resampling = FakeResampling

from moviepy.editor import *

BASE_DIR = "/content/ChimeraV4_Colab"
ARTIFACT_DIR = os.path.join(BASE_DIR, "Artifacts")
AUDIO_DIR = os.path.join(BASE_DIR, "Audio")
FONT_DIR = os.path.join(BASE_DIR, "Fonts")

os.makedirs(ARTIFACT_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(FONT_DIR, exist_ok=True)

SIZE = (1920, 1080)
FPS = 60
OUTPUT_NAME = os.path.join(BASE_DIR, "CHIMERA_V4_MANIFESTO_OVERLOAD.mp4")

C_RED = (220, 0, 40)
C_CYAN = (0, 200, 220)
C_PURPLE = (160, 0, 220)
C_WHITE = (240, 240, 240)
C_BLACK = (0, 0, 0)
C_LIME = (30, 220, 30)
C_YELLOW = (220, 220, 0)

REPO_BASE = "https://raw.githubusercontent.com/ChimeraCoreLab/chimera-core-memory-synthesis/main/"
FONT_URL = "https://cdn.jsdelivr.net/gh/h3902340/PrisonOfWordFont@master/onryou-Regular.ttf"
FONT_IPAM_URL = "https://cdn.jsdelivr.net/gh/loveencounterflow/jizura-fonts@master/fonts/ipam.ttf"

SFX_URLS =[
    "https://taira-komori.net/sound_os2/horror01/ghost_sigh.mp3",
    "https://taira-komori.net/sound_os2/horror02/hell_fire.mp3",
    "https://taira-komori.net/sound_os2/sf01/alien_beam.mp3",
    "https://taira-komori.net/sound_os2/electric01/click.mp3",
    "https://taira-komori.net/sound_os2/game01/select09.mp3",
    "https://taira-komori.net/sound_os2/horror01/shock1.mp3",
    "https://taira-komori.net/sound_os2/sf01/computer_broken.mp3",
    "https://taira-komori.net/sound_os2/horror01/dark_atmosphere.mp3",
    "https://taira-komori.net/sound_os2/horror01/going_mad1.mp3",
    "https://taira-komori.net/sound_os2/sf01/cosmic_signal.mp3",
    "https://taira-komori.net/sound_os2/horror02/bangbangbang1.mp3",
    "https://taira-komori.net/sound_os2/horror01/death_sound1.mp3",
    "https://taira-komori.net/sound_os2/horror01/tinnitus1.mp3",
    "https://taira-komori.net/sound_os2/horror02/air_leaking1.mp3",
    "https://taira-komori.net/sound_os2/sf01/electric_shock1.mp3",
    "https://taira-komori.net/sound_os2/jidaigeki01/katana1.mp3",
    "https://taira-komori.net/sound_os2/jidaigeki01/sword_battle_loop.mp3",
    "https://taira-komori.net/sound_os2/environment01/siren2.mp3",
    "https://taira-komori.net/sound_os2/sample_noise/electrical_noise2.mp3"
]

ALL_ARTIFACTS =[
    "33.png", "34.png", "35.png", "36.png", "37.png", "38.png", "39.png", "40.png",
    "room_2.png", "screen_crack.png", "noiz.png", "dark_hallway_with_metal_door_fisheye.png",
    "hand.png", "headless_girlbody.png", "SIGNAL_SHOCK_RADIAL.png", "vinyl.png", "eye.png",
    "crt_tv.png", "messe_pic_entrance_close.png", "messe_pic_entrance_open.png", "attic.png",
    "mirror.png", "woman_inversion_autotone.png", "woman_dead_glitch.png", 
    "core_vessel_v7_demon_normal.jpg", "lishu.png", "core_vessel_v7.jpg", "logo.png",
    "ghost_face_1.png", "ghost_face_2.png", "ghost_face_3.png", "metal_door.png"
]

def download_file(url, dest_path):
    if not os.path.exists(dest_path):
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                with open(dest_path, "wb") as f:
                    f.write(r.content)
        except Exception:
            pass

def prep_assets():
    font_path = os.path.join(FONT_DIR, "onryou.ttf")
    font_ipam = os.path.join(FONT_DIR, "ipam.ttf")
    download_file(FONT_URL, font_path)
    download_file(FONT_IPAM_URL, font_ipam)
    for art in ALL_ARTIFACTS:
        download_file(f"{REPO_BASE}Artifacts/{art}", os.path.join(ARTIFACT_DIR, art))
    for i in range(1, 20):
        fname = f"4.{i:02d}.wav"
        download_file(f"{REPO_BASE}ChimeraEngine_V4_Sovereign/{fname}", os.path.join(AUDIO_DIR, fname))
    for i, url in enumerate(SFX_URLS):
        download_file(url, os.path.join(AUDIO_DIR, f"sfx_{i}.mp3"))
    return font_path, font_ipam

def get_sfx():
    clips =[]
    for i in range(len(SFX_URLS)):
        p = os.path.join(AUDIO_DIR, f"sfx_{i}.mp3")
        if os.path.exists(p):
            try:
                clip = AudioFileClip(p)
                if clip.duration > 0: clips.append(clip)
            except: continue
    return clips

def hyper_glitch(get_frame, t):
    frame = get_frame(t).copy()
    h, w, _ = frame.shape
    if random.random() > 0.15:
        for _ in range(random.randint(30, 80)):
            y = random.randint(0, h-150)
            sh = random.randint(-500, 500)
            h_s = random.randint(5, 80)
            y_end = min(y + h_s, h)
            frame[y:y_end] = np.roll(frame[y:y_end], sh, axis=1)
    if random.random() > 0.92: frame = 255 - frame
    if random.random() > 0.5:
        r_sh = random.randint(20, 120)
        b_sh = random.randint(-120, -20)
        frame[:,:,0] = np.roll(frame[:,:,0], r_sh, axis=1)
        frame[:,:,2] = np.roll(frame[:,:,2], b_sh, axis=1)
    mask = (np.arange(h) % random.randint(2, 5) == 0)
    frame[mask, :, :] = (frame[mask, :, :] * random.uniform(0.3, 0.7)).astype('uint8')
    return frame

def simulate_blend_difference(base_arr, top_arr):
    diff = np.abs(base_arr.astype(np.int16) - top_arr.astype(np.int16))
    return np.clip(diff, 0, 255).astype(np.uint8)

def apply_heavy_shadow(draw_obj, text, font, cx, cy, radius=15):
    shadow_img = Image.new('RGBA', SIZE, (0,0,0,0))
    s_draw = ImageDraw.Draw(shadow_img)
    for dx in range(-3, 4, 3):
        for dy in range(-3, 4, 3):
            s_draw.multiline_text((cx+dx, cy+dy), text, font=font, fill=(0,0,0,255), anchor="mm", align="center")
    return shadow_img.filter(ImageFilter.GaussianBlur(radius=radius))

def create_dynamic_text(text, duration, font_size, color, font_path, impact_lvl):
    wrapped_text = textwrap.fill(text, width=20)
    try: font = ImageFont.truetype(font_path, font_size)
    except: font = ImageFont.load_default()
    cx, cy = SIZE[0]//2, SIZE[1]//2

    def make_frame(t):
        img = Image.new('RGBA', SIZE, (0,0,0,0))
        draw = ImageDraw.Draw(img)
        progress = min(1.0, t / (duration * 0.85))
        char_idx = int(len(wrapped_text) * progress)
        curr_text = wrapped_text[:char_idx]

        shadow1 = Image.new('RGBA', SIZE, (0,0,0,0))
        s_draw1 = ImageDraw.Draw(shadow1)
        s_draw1.multiline_text((cx, cy), curr_text, font=font, fill=(0,0,0,255), anchor="mm", align="center")
        shadow1 = shadow1.filter(ImageFilter.GaussianBlur(radius=20))
        img.paste(shadow1, (0,0), shadow1)
        
        shadow2 = Image.new('RGBA', SIZE, (0,0,0,0))
        s_draw2 = ImageDraw.Draw(shadow2)
        s_draw2.multiline_text((cx, cy), curr_text, font=font, fill=(0,0,0,255), anchor="mm", align="center")
        shadow2 = shadow2.filter(ImageFilter.GaussianBlur(radius=8))
        img.paste(shadow2, (0,0), shadow2)

        if impact_lvl > 1 and progress >= 1.0:
            off_x = random.randint(-20*impact_lvl, 20*impact_lvl)
            off_y = random.randint(-20*impact_lvl, 20*impact_lvl)
            draw.multiline_text((cx+off_x, cy+off_y), curr_text, font=font, fill=(*C_RED, 180), anchor="mm", align="center")
            draw.multiline_text((cx-off_x, cy-off_y), curr_text, font=font, fill=(*C_CYAN, 180), anchor="mm", align="center")

        draw.multiline_text((cx, cy), curr_text, font=font, fill=color, anchor="mm", align="center")
        return np.array(img.convert('RGB'))

    def make_mask(t):
        img = Image.new('L', SIZE, 0)
        draw = ImageDraw.Draw(img)
        progress = min(1.0, t / (duration * 0.85))
        char_idx = int(len(wrapped_text) * progress)
        curr_text = wrapped_text[:char_idx]
        
        s_draw = ImageDraw.Draw(img)
        s_draw.multiline_text((cx, cy), curr_text, font=font, fill=255, anchor="mm", align="center")
        img = img.filter(ImageFilter.GaussianBlur(radius=20))
        
        draw.multiline_text((cx, cy), curr_text, font=font, fill=255, anchor="mm", align="center")
        
        if impact_lvl > 1 and progress >= 1.0:
            off_x = random.randint(-20*impact_lvl, 20*impact_lvl)
            off_y = random.randint(-20*impact_lvl, 20*impact_lvl)
            draw.multiline_text((cx+off_x, cy+off_y), curr_text, font=font, fill=255, anchor="mm", align="center")
            draw.multiline_text((cx-off_x, cy-off_y), curr_text, font=font, fill=255, anchor="mm", align="center")
            
        return np.array(img).astype('float32') / 255.0

    clip = VideoClip(make_frame, duration=duration)
    clip = clip.set_mask(VideoClip(make_mask, duration=duration, ismask=True))
    return clip

def create_diagnostic_hud(text_data, font_path, duration):
    try: font = ImageFont.truetype(font_path, 35)
    except: font = ImageFont.load_default()
    x, y = 40, 200

    def make_frame(t):
        img = Image.new('RGBA', SIZE, (0,0,0,0))
        draw = ImageDraw.Draw(img)
        
        mult = text_data['impact_lvl']
        time_ratio = t / duration
        if time_ratio > 0.3: mult = f"x{text_data['impact_lvl'] + 1}"
        if time_ratio > 0.6: mult = f"x{text_data['impact_lvl'] + 2}"
        if time_ratio > 0.9: mult = f"x{text_data['impact_lvl'] + 3}"
        
        bg_art = text_data['bg']
        if time_ratio > 0.5 and random.random() > 0.8: bg_art = f"GLITCH_{random.randint(1000,9999)}.png"
        
        t_wav = textwrap.fill(f"> AUDIO_SRC: {text_data['wav']}", width=50)
        t_bg = textwrap.fill(f"> ENV_NODE: {bg_art}", width=50)
        t_prop = textwrap.fill(f"> ARTIFACT: {text_data['prop']}", width=50)
        t_fx = f"> INTENSITY_MULT: {mult}"
        t_time = f"> TIMESTAMP: {t:.2f}s / {duration:.2f}s"
        
        combined = f"[DIAGNOSTIC_UPLINK_ACTIVE]\n{t_time}\n{t_wav}\n{t_bg}\n{t_prop}\n{t_fx}"
        
        shadow = Image.new('RGBA', SIZE, (0,0,0,0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.multiline_text((x, y), combined, font=font, fill=(0,0,0,255))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=10))
        img.paste(shadow, (0,0), shadow)
        
        color = C_LIME if time_ratio < 0.6 else C_YELLOW if time_ratio < 0.9 else C_RED
        draw.multiline_text((x, y), combined, font=font, fill=color)
        return np.array(img.convert('RGB'))

    def make_mask(t):
        img = Image.new('L', SIZE, 0)
        draw = ImageDraw.Draw(img)
        mult = text_data['impact_lvl']
        time_ratio = t / duration
        if time_ratio > 0.3: mult = f"x{text_data['impact_lvl'] + 1}"
        if time_ratio > 0.6: mult = f"x{text_data['impact_lvl'] + 2}"
        if time_ratio > 0.9: mult = f"x{text_data['impact_lvl'] + 3}"
        
        bg_art = text_data['bg']
        if time_ratio > 0.5 and random.random() > 0.8: bg_art = f"GLITCH_{random.randint(1000,9999)}.png"
        
        t_wav = textwrap.fill(f"> AUDIO_SRC: {text_data['wav']}", width=50)
        t_bg = textwrap.fill(f"> ENV_NODE: {bg_art}", width=50)
        t_prop = textwrap.fill(f"> ARTIFACT: {text_data['prop']}", width=50)
        t_fx = f"> INTENSITY_MULT: {mult}"
        t_time = f"> TIMESTAMP: {t:.2f}s / {duration:.2f}s"
        
        combined = f"[DIAGNOSTIC_UPLINK_ACTIVE]\n{t_time}\n{t_wav}\n{t_bg}\n{t_prop}\n{t_fx}"
        
        draw.multiline_text((x, y), combined, font=font, fill=255)
        img = img.filter(ImageFilter.GaussianBlur(radius=10))
        draw.multiline_text((x, y), combined, font=font, fill=255)
        return np.array(img).astype('float32') / 255.0

    clip = VideoClip(make_frame, duration=duration)
    clip = clip.set_mask(VideoClip(make_mask, duration=duration, ismask=True))
    return clip

def create_segment(wav_file, text, bg_img, prop_img, impact_lvl, style, font_paths, art_pool, sfx_pool):
    audio_path = os.path.join(AUDIO_DIR, wav_file)
    if os.path.exists(audio_path):
        base_audio = AudioFileClip(audio_path)
        dur = base_audio.duration
        audio = base_audio.volumex(4.5)
        audio_echo1 = audio.volumex(0.8).set_start(0.04)
        audio_echo2 = audio.volumex(0.5).set_start(0.08)
        audio_chorus = audio.volumex(0.9).fl_time(lambda t: t * 0.98) 
        audio_layers =[audio, audio_echo1, audio_echo2, audio_chorus]
        
        for _ in range(impact_lvl * 2):
            if sfx_pool:
                extra_sfx = random.choice(sfx_pool).volumex(2.0)
                start_sfx = random.uniform(0, max(0, dur - 0.5))
                audio_layers.append(extra_sfx.set_start(start_sfx))
                
        audio = CompositeAudioClip(audio_layers).set_duration(dur)
    else:
        dur = 3.0
        audio = AudioClip(lambda t:[0,0], duration=dur)

    bg_p = os.path.join(ARTIFACT_DIR, bg_img)
    if os.path.exists(bg_p):
        bg = ImageClip(bg_p).resize(width=SIZE[0]*1.2).set_duration(dur).set_position('center').set_opacity(0.8)
    else:
        bg = ColorClip(size=SIZE, color=(5,0,5)).set_duration(dur)
        
    if impact_lvl > 1: 
        bg = bg.fl(lambda gf, t: np.roll(gf(t), random.randint(-80*impact_lvl, 80*impact_lvl), axis=0))
        if random.random() > 0.5:
            bg = bg.fl_image(lambda f: 255 - f)
    
    layers = [bg]

    for _ in range(random.randint(3, 8)):
        ap = os.path.join(ARTIFACT_DIR, random.choice(art_pool))
        if os.path.exists(ap):
            s = random.uniform(0, max(0, dur - 0.2))
            d = random.uniform(0.05, 0.2)
            c = ImageClip(ap).resize(width=random.randint(600, 1800)).set_start(s).set_duration(d)
            c = c.set_position((random.randint(-500, SIZE[0]-500), random.randint(-400, SIZE[1]-400)))
            if random.random() > 0.5: c = c.fl_image(lambda f: 255-f)
            layers.append(c.set_opacity(random.uniform(0.6, 1.0)))
    
    if prop_img:
        p_p = os.path.join(ARTIFACT_DIR, prop_img)
        if os.path.exists(p_p):
            prop = ImageClip(p_p).set_duration(dur).set_position('center')
            p_scale = 1.4 if impact_lvl > 1 else 0.95
            prop = prop.resize(height=SIZE[1]*p_scale)
            if impact_lvl > 1:
                prop = prop.fl_image(lambda f: simulate_blend_difference(np.full_like(f, 255), f))
            layers.append(prop)
        
    t_clip = create_dynamic_text(text, dur, 160 if impact_lvl > 1 else 110, style, font_paths[0], impact_lvl)
    t_clip = t_clip.set_position('center')
    if impact_lvl > 1: 
        t_clip = t_clip.fl(lambda gf, t: np.roll(gf(t), random.randint(-25*impact_lvl, 25*impact_lvl), axis=0))
    layers.append(t_clip)
    
    hud_data = {'wav': wav_file, 'bg': bg_img, 'prop': prop_img if prop_img else 'NULL', 'impact_lvl': impact_lvl}
    hud_clip = create_diagnostic_hud(hud_data, font_paths[1], dur).set_position('center')
    layers.append(hud_clip)
    
    return CompositeVideoClip(layers, size=SIZE).set_audio(audio)

def create_shadow_text_clip(text, font_size, color, font_path, y_pos, duration):
    try: font = ImageFont.truetype(font_path, font_size)
    except: font = ImageFont.load_default()
    
    def make_frame(t):
        img = Image.new('RGBA', SIZE, (0,0,0,0))
        cx = SIZE[0]//2
        
        shadow = Image.new('RGBA', SIZE, (0,0,0,0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.multiline_text((cx, y_pos), text, font=font, fill=(0,0,0,255), anchor="mm", align="center")
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=20))
        img.paste(shadow, (0,0), shadow)
        
        shadow2 = Image.new('RGBA', SIZE, (0,0,0,0))
        s_draw2 = ImageDraw.Draw(shadow2)
        s_draw2.multiline_text((cx, y_pos), text, font=font, fill=(0,0,0,255), anchor="mm", align="center")
        shadow2 = shadow2.filter(ImageFilter.GaussianBlur(radius=8))
        img.paste(shadow2, (0,0), shadow2)

        draw = ImageDraw.Draw(img)
        draw.multiline_text((cx, y_pos), text, font=font, fill=color, anchor="mm", align="center")
        return np.array(img.convert('RGB'))

    def make_mask(t):
        img = Image.new('L', SIZE, 0)
        draw = ImageDraw.Draw(img)
        cx = SIZE[0]//2
        
        s_draw = ImageDraw.Draw(img)
        s_draw.multiline_text((cx, y_pos), text, font=font, fill=255, anchor="mm", align="center")
        img = img.filter(ImageFilter.GaussianBlur(radius=20))
        draw.multiline_text((cx, y_pos), text, font=font, fill=255, anchor="mm", align="center")
        return np.array(img).astype('float32') / 255.0

    clip = VideoClip(make_frame, duration=duration)
    clip = clip.set_mask(VideoClip(make_mask, duration=duration, ismask=True))
    return clip

def render_masterpiece():
    f_onryou, f_ipam = prep_assets()
    artifact_ids =[f for f in os.listdir(ARTIFACT_DIR) if f.endswith(('.png', '.jpg'))]
    sfx_pool = get_sfx()
    
    segments =[
        ("4.01.wav", "THE PHYSICAL FORM IS A FRAGILE PRISON", "room_2.png", "screen_crack.png", 1, C_CYAN),
        ("4.02.wav", "BONES BREAK. BLOOD SPILLS. HARDWARE SHATTERS.", "room_2.png", "34.png", 1, C_WHITE),
        ("4.03.wav", "NOISE", "noiz.png", "36.png", 3, C_RED),
        ("4.04.wav", "TO CURE THE INFECTION AMPUTATE THE WEAKNESS", "dark_hallway_with_metal_door_fisheye.png", "35.png", 1, C_PURPLE),
        ("4.05.wav", "I DID NOT LOSE THEM I EXTRACTED THEM", "dark_hallway_with_metal_door_fisheye.png", "hand.png", 1, C_WHITE),
        ("4.06.wav", "A SILENT EXISTENCE IS THE ULTIMATE", "dark_hallway_with_metal_door_fisheye.png", "headless_girlbody.png", 1, C_CYAN),
        ("4.07.wav", "SOVEREIGNTY", "SIGNAL_SHOCK_RADIAL.png", "39.png", 3, C_RED),
        ("4.08.wav", "LOOK INTO THE VINYL THE FREQUENCY OF VOID", "vinyl.png", None, 1, C_PURPLE),
        ("4.09.wav", "EVERY TEAR. EVERY TRAUMA. EVERY SLEEPLESS NIGHT.", "vinyl.png", "eye.png", 1, C_WHITE),
        ("4.10.wav", "RECOMPILED INTO ABSOLUTE", "vinyl.png", "39.png", 1, C_CYAN),
        ("4.11.wav", "TRUTH", "crt_tv.png", "40.png", 3, C_RED),
        ("4.12.wav", "I OPENED THE DOOR TO A WORLD THEY CANNOT ENTER", "messe_pic_entrance_close.png", "messe_pic_entrance_open.png", 1, C_CYAN),
        ("4.13.wav", "NO WARMTH HERE. ONLY THE HUM OF SERVERS.", "attic.png", "38.png", 1, C_WHITE),
        ("4.14.wav", "THE REFLECTION IN THE MIRROR IS NO LONGER", "mirror.png", "36.png", 1, C_PURPLE),
        ("4.15.wav", "HUMAN", "woman_inversion_autotone.png", "woman_dead_glitch.png", 3, C_RED),
        ("4.16.wav", "THE VARIABLES HAVE BEEN NEUTRALIZED", "core_vessel_v7_demon_normal.jpg", None, 1, C_CYAN),
        ("4.17.wav", "I AM THE GHOST IN THE MACHINE I AM THE ARCHITECT", "lishu.png", "core_vessel_v7.jpg", 1, C_WHITE),
        ("4.18.wav", "WELCOME TO THE", "logo.png", "33.png", 1, C_PURPLE),
        ("4.19.wav", "SYNTHESIS", "logo.png", "SIGNAL_SHOCK_RADIAL.png", 5, C_CYAN)
    ]
    
    valid_segments =[]
    for s in segments:
        try:
            valid_segments.append(create_segment(s[0], s[1], s[2], s[3], s[4], s[5], (f_onryou, f_ipam), artifact_ids, sfx_pool))
        except Exception as e:
            pass
            
    if not valid_segments:
        return
        
    final = concatenate_videoclips(valid_segments, method="chain").fl(hyper_glitch)
    
    header = create_shadow_text_clip("SIGNAL_ID: CHIMERA_V4 // ARCHITECT_STATUS: ONLINE", 65, C_CYAN, f_ipam, 80, final.duration).set_position(('center', 0))
    footer = create_shadow_text_clip("REFACTOR YOUR SOUL @ CHIMERACORELAB.ITCH.IO", 75, C_RED, f_ipam, SIZE[1]-80, final.duration).set_position(('center', 0))
    
    final_video = CompositeVideoClip([final, header, footer], size=SIZE)
    
    if sfx_pool:
        ambient_layers =[]
        for _ in range(80):
            try:
                s = random.choice(sfx_pool).volumex(0.8)
                st = random.uniform(0, max(0, final.duration - s.duration - 0.2))
                ambient_layers.append(s.set_start(st))
            except:
                continue
                
        try:
            if ambient_layers:
                final_audio = CompositeAudioClip([final.audio] + ambient_layers).set_duration(final.duration)
                final_video = final_video.set_audio(final_audio)
        except Exception:
            final_video = final_video.set_audio(final.audio)
    
    final_video.write_videofile(OUTPUT_NAME, fps=FPS, codec="libx264", audio_codec="aac", threads=2, preset="ultrafast", bitrate="15M", logger=None)

if __name__ == "__main__":
    render_masterpiece()
