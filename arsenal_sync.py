import os
import time
import re
import html
import base64
import requests
from collections import defaultdict
from datetime import datetime
from googleapiclient.discovery import build
import isodate
from youtube_transcript_api import YouTubeTranscriptApi

ITCHIO_API_KEY = ""
ITCHIO_USER = "nrocps"
GITHUB_USER = "nrocps"
GITHUB_TOKEN = ""
YOUTUBE_API_KEY = ""
CHANNEL_ID = "UCTTZHqy0WF1SzX8Wy_1jB0w"

RAW_LOGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'RAW_LOGS.txt')

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
GH_HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def decimal_to_base36(num, width=2):
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    if num == 0: return "0".zfill(width)
    res = ""
    while num > 0:
        res = chars[num % 36] + res
        num //= 36
    return res.zfill(width)

def human_size_short(size_bytes):
    if size_bytes == 0: return "0B"
    units = ("B", "K", "M", "G")
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024
        i += 1
    return f"{int(size_bytes)}{units[i]}"

def clean_text(text):
    if not text: return "NULL"
    text = html.unescape(str(text))
    text = text.replace('\\', '\\\\').replace('"', '\\"')
    text = text.replace('\r', '').replace('\n', '\\n').replace('|', '&#124;')
    return text.strip()

class SmartInjector:
    def __init__(self):
        self.lines = []
        self.known_artifacts = set()
        self.now = datetime.now()
        self.d_str = self.now.strftime("%Y%m%d")
        self.t_str = self.now.strftime("%H%M")
        self.new_logs = []
        self.idx = 1
        self.has_declaration = False
        self.header = "const RAW_LOGS = ["
        self.load_and_clean()

    def load_and_clean(self):
        if not os.path.exists(RAW_LOGS_PATH): return
        with open(RAW_LOGS_PATH, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        if content.endswith('];'):
            content = content[:-2].strip()
        header_match = re.match(r'^(const\s+RAW_LOGS\s*=\s*\[)', content)
        if header_match:
            self.has_declaration = True
            self.header = header_match.group(1)
            content = content[len(self.header):].strip()
        raw_lines = content.splitlines()
        for line in raw_lines:
            line = line.strip()
            if not line: continue
            clean_line = line.rstrip(',')
            if 'UI0' in clean_line or 'EI0' in clean_line:
                try:
                    parts = clean_line.split('0', 1)[-1].split('&#124;')
                    if len(parts) > 0:
                        self.known_artifacts.add(parts[0].strip().strip('"').strip("'"))
                except: pass
            if any(marker in clean_line for marker in ['UG0', 'EG0', 'UK0', 'EK0', 'UY0', 'EY0']):
                continue
            if not line.endswith(','):
                line += ','
            self.lines.append(line)

    def add(self, l_type, content):
        idx_b36 = decimal_to_base36(self.idx, 2)
        self.new_logs.append(f'"{self.t_str}{idx_b36}U{l_type}0{content}",')
        self.idx += 1

    def save(self):
        today_marker = f'"D:{self.d_str}",'
        today_exists = any(f'D:{self.d_str}' in l for l in self.lines)
        if not today_exists:
            self.lines.append(today_marker)
        self.lines.extend(self.new_logs)
        last_idx = len(self.lines) - 1
        if last_idx >= 0:
            self.lines[last_idx] = self.lines[last_idx].rstrip(',')
        body = '\n'.join(self.lines)
        if self.has_declaration:
            final_output = f"{self.header}\n{body}\n];"
        else:
            final_output = f"const RAW_LOGS = [\n{body}\n];"
        with open(RAW_LOGS_PATH, 'w', encoding='utf-8') as f:
            f.write(final_output)

def get_itch_web_data(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200: return {}
        desc_match = re.search(r'<div class="formatted_description user_formatted">(.*?)</div>', r.text, re.DOTALL)
        description = re.sub('<[^>]*>', '', desc_match.group(1)) if desc_match else "NULL"
        tags = re.findall(r'/directory/tag/[^\"]+\">([^<]+)</a>', r.text)
        noun_match = re.search(r'<td>Genre</td>\s*<td>\s*<a[^>]+>([^<]+)</a>', r.text)
        if not noun_match:
            noun_match = re.search(r'<td>Noun</td>\s*<td>([^<]+)</td>', r.text)
        yt_match = re.search(r'youtube\.com/embed/([^?\"]+)', r.text)
        if not yt_match:
            yt_match = re.search(r'youtube\.com/watch\?v=([^&?\"]+)', r.text)
        video_id = yt_match.group(1) if yt_match else "NULL"
        return {
            "desc": description.strip(),
            "tags": ", ".join(tags) if tags else "NULL",
            "noun": noun_match.group(1).strip() if noun_match else "artifact",
            "video_id": video_id
        }
    except: return {}

def sync_market(injector):
    api_headers = {"Authorization": ITCHIO_API_KEY}
    try:
        games = []
        seen_ids = set()
        page = 1
        while True:
            r = requests.get(f"https://itch.io/api/1/key/my-games?page={page}", headers=api_headers, timeout=15)
            if r.status_code != 200: break
            page_games = r.json().get('games', [])
            if not page_games: break
            new_added = False
            for g in page_games:
                if g['id'] not in seen_ids:
                    seen_ids.add(g['id'])
                    games.append(g)
                    new_added = True
            if not new_added or len(page_games) < 30:
                break
            page += 1
        games.sort(key=lambda g: g.get('published_at') or '', reverse=True)
        total_v = sum(g.get('views_count', 0) for g in games)
        total_d = sum(g.get('downloads_count', 0) for g in games)
        injector.add('K', f'PROFILE|{ITCHIO_USER}|{len(games)}|{total_v}|{total_d}')
        for g in games:
            g_id = g['id']
            web_data = get_itch_web_data(g['url'])
            f_r = requests.get(f"https://itch.io/api/1/key/game/{g_id}/uploads", headers=api_headers)
            f_data = f_r.json().get('uploads', []) if f_r.status_code == 200 else []
            f_list = [f"{u['filename']} ({u['size']//1048576}mb) - {u.get('downloads_count', 0)} DLs" for u in f_data]
            p_val = g.get('min_price', 0)
            try:
                price_float = float(p_val) / 100.0
                price_display = "${:.2f}".format(price_float) if price_float > 0 else "$0.00 or donate"
            except:
                price_display = "$0.00 or donate"
            video_id_val = web_data.get('video_id') or 'NULL'
            v_link = f"https://www.youtube.com/watch?v={video_id_val}" if video_id_val != "NULL" else "NULL"
            desc_val = web_data.get('desc') or 'NULL'
            tags_val = web_data.get('tags') or 'NULL'
            noun_val = web_data.get('noun') or 'artifact'
            entry = [
                clean_text(g['title']),
                clean_text(g.get('short_text', 'NULL')),
                clean_text(g.get('classification', 'Other')),
                "Downloadable" if g.get('type') != 'html' else "HTML",
                "RELEASED" if g.get('published') else "DRAFT",
                price_display,
                "2.00",
                "; ".join(f_list) if f_list else "NULL",
                clean_text(desc_val),
                clean_text(tags_val),
                "Yes (AI Assisted)" if "ai" in tags_val.lower() else "No",
                clean_text(noun_val),
                clean_text(desc_val),
                "Comments Enabled",
                "Public",
                g.get('cover_url', 'NULL'),
                v_link,
                g.get('earnings', [{}])[0].get('amount', '0') if g.get('earnings') else '0',
                g.get('purchases_count', 0),
                g.get('views_count', 0),
                g.get('downloads_count', 0),
                g.get('published_at', 'NULL'),
                g.get('collections_count', 0),
                "0",
                "0"
            ]
            injector.add('K', f'ENTRY|{"|".join(map(str, entry))}')
            time.sleep(0.1)
    except Exception as e: pass

def compress_tree(tree_items, known_artifacts):
    dirs = defaultdict(list)
    for item in tree_items:
        if item['type'] == 'blob':
            parts = item['path'].split('/')
            d_name = "/".join(parts[:-1]) if len(parts) > 1 else 'root'
            dirs[d_name].append(item)
    res = []
    for d, files in dirs.items():
        if d == 'Artifacts':
            new_files = [f for f in files if f['path'].split('/')[-1] not in known_artifacts]
            if not new_files:
                res.append(f"{d}:SYNCED")
            else:
                sz = human_size_short(sum(f.get('size', 0) for f in new_files))
                res.append(f"{d}>{len(new_files)}New({sz})")
        elif any(x in d for x in ['Audio', 'Fonts', 'addons', 'CRTVHS', 'examples', 'CAE', 'ChimeraEngine_V1_Genesis', 'ChimeraEngine_V2_Ultimate', 'ChimeraEngine_V3_Atomic_Cessation', 'ChimeraEngine_V4_Sovereign']):
            sz = human_size_short(sum(f.get('size', 0) for f in files))
            res.append(f"{d}:{len(files)}f({sz})")
        else:
            f_strs = [f"{f['path'].split('/')[-1]}:{human_size_short(f.get('size', 0))}" for f in files]
            res.append(f"{d}>" + ",".join(f_strs))
    return "|".join(res)

def get_gh_tree(owner, repo, branch="main"):
    try:
        r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1", headers=GH_HEADERS, timeout=15)
        if r.status_code == 200: return r.json().get('tree', [])
    except: pass
    return []

def get_gh_file(owner, repo, path):
    try:
        r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=GH_HEADERS, timeout=10)
        if r.status_code == 200: return base64.b64decode(r.json()['content']).decode('utf-8', errors='ignore')
    except: pass
    return None

def sync_github(injector):
    try:
        user_data = requests.get(f"https://api.github.com/users/{GITHUB_USER}", headers=GH_HEADERS).json()
        repos = requests.get(f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100&sort=updated", headers=GH_HEADERS).json()
        injector.add('G', f'PROFILE|{user_data.get("public_repos", 0)}|{sum(r.get("stargazers_count", 0) for r in repos)}|github.com/{GITHUB_USER}|STABLE_ACTIVE|PUBLIC_ENCRYPTED_READ')
        extra_targets = ["synthesis.py", "artifact_audit.py", "chimera_arsenal_sync.py", "injector.py", "zip_tree_generator.py"]
        for r in repos:
            name = r['name']
            tree_items = get_gh_tree(GITHUB_USER, name, r.get('default_branch', 'main'))
            tree_str = compress_tree(tree_items, injector.known_artifacts)
            readme = get_gh_file(GITHUB_USER, name, "README.md") or "No README documentation found."
            other_files = []
            for item in tree_items:
                if item['type'] == 'blob' and item['path'].split('/')[-1] in extra_targets:
                    content = get_gh_file(GITHUB_USER, name, item['path'])
                    if content: other_files.append(f"{item['path']}:{clean_text(content).replace(';' + ';', ';#' + '59;')}")
            injector.add('G', f'REPO|{clean_text(name)}|{"COMPLETED" if r.get("archived") else "ACTIVE_RESEARCH"}|{r.get("stargazers_count", 0)}|{clean_text(tree_str)}|{r.get("license", {}).get("spdx_id", "MIT") if r.get("license") else "MIT"}|{clean_text(readme)}|{(";" + ";").join(other_files)}')
            time.sleep(0.1)
    except: pass

def get_transcript(video_id):
    try:
        return "\\n".join([f"[{time.strftime('%M:%S', time.gmtime(e['start']))}] {e['text']}" for e in YouTubeTranscriptApi.get_transcript(video_id, languages=['th', 'en'])])
    except: return "NULL"

def sync_youtube(injector):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    try:
        ch_res = youtube.channels().list(part='snippet,statistics,contentDetails', id=CHANNEL_ID).execute()
        if not ch_res['items']: return
        ch_data = ch_res['items'][0]
        video_ids = set()
        next_page = None
        while True:
            pl_res = youtube.playlistItems().list(part='contentDetails', playlistId=ch_data['contentDetails']['relatedPlaylists']['uploads'], maxResults=50, pageToken=next_page).execute()
            for item in pl_res['items']: video_ids.add(item['contentDetails']['videoId'])
            next_page = pl_res.get('nextPageToken')
            if not next_page: break
        final_entries = []
        id_list = list(video_ids)
        for i in range(0, len(id_list), 50):
            v_res = youtube.videos().list(part='snippet,contentDetails,statistics,status', id=','.join(id_list[i:i+50])).execute()
            for v in v_res['items']:
                dur_obj = isodate.parse_duration(v['contentDetails']['duration'])
                final_entries.append({
                    'timestamp': v['snippet']['publishedAt'],
                    'log': f'{v["id"]}|{clean_text(v["snippet"]["title"])}|{v["snippet"]["publishedAt"][:10]}|{str(dur_obj).split(".")[0].zfill(8)}|VIDEO|{v["status"]["privacyStatus"].upper()}|{v["statistics"].get("viewCount", "0")}|{v["statistics"].get("likeCount", "0")}|100|0|SIGNAL_LOCKED|{clean_text(v["snippet"]["description"])}|{clean_text(get_transcript(v["id"]))}|NO_COMMUNITY_SIGNALS'
                })
        injector.add('Y', f'CHANNEL|{clean_text(ch_data["snippet"]["title"])}|ESTB_2018|{len(final_entries)}_NODES|{ch_data["statistics"]["viewCount"]}_PULSES')
        for entry in sorted(final_entries, key=lambda x: x['timestamp'], reverse=True):
            injector.add('Y', f'ENTRY|{entry["log"]}')
    except: pass

if __name__ == "__main__":
    injector = SmartInjector()
    sync_market(injector)
    sync_github(injector)
    sync_youtube(injector)
    injector.save()