#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import datetime
from pathlib import Path
from PIL import Image

def decimal_to_base36(num, width=2):
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    if num == 0:
        return "0".zfill(width)
    res = ""
    while num > 0:
        res = chars[num % 36] + res
        num //= 36
    return res.zfill(width)

def compress_html_markup(html_str):
    html_str = re.sub(r'\x3c!--.*?--\x3e', '', html_str, flags=re.DOTALL)
    lines = [l.strip() for l in html_str.splitlines() if l.strip() and not l.strip().startswith('//')]
    return '\n'.join(lines)

def parse_raw_logs_structure(raw_text):
    content = raw_text.strip()
    if content.startswith('const RAW_LOGS = ['):
        content = content[18:]
    if content.endswith('];'):
        content = content[:-2]
    elif content.endswith(']'):
        content = content[:-1]

    raw_lines = [l.strip().strip(',').strip('"') for l in content.splitlines() if l.strip().strip(',').strip('"')]

    normal_lines = []
    tail_lines = []
    in_tail = False

    for line in raw_lines:
        if line.startswith('D:CORE') or line.startswith('D:SYS'):
            in_tail = True
        
        formatted_line = f'"{line}"'
        if in_tail:
            tail_lines.append(formatted_line)
        else:
            normal_lines.append(formatted_line)

    return normal_lines, tail_lines

def process_input_text_signals(base_path, normal_lines):
    f_in = base_path / "input.txt"
    f_bak = base_path / "raw_logs_backup.txt"

    if not f_in.exists() or f_in.stat().st_size == 0:
        return normal_lines

    try:
        with open(f_in, 'r', encoding='utf-8') as f:
            data = f.read()

        segs = [s.strip() for s in data.split("[NEXT_SIGNAL_9369]") if s.strip()]
        if not segs:
            return normal_lines

        now = datetime.datetime.now()
        d_str = f"D:{now.strftime('%Y%m%d')}"
        h_str = now.strftime('%H%M')

        last_date = ""
        for line in reversed(normal_lines):
            m = re.match(r'^"D:(\d{8})"$', line)
            if m:
                last_date = f"D:{m.group(1)}"
                break

        last_idx = 0
        for line in reversed(normal_lines):
            m = re.match(r'^"(\d{4})([0-9a-z]{2})UM0', line)
            if m:
                lh, ix_b36 = m.groups()
                if lh == h_str:
                    last_idx = int(ix_b36, 36)
                break

        if last_date != d_str:
            normal_lines.append(f'"{d_str}"')

        curr_idx = last_idx
        for s in segs:
            s = s.replace('\\', '\\\\').replace('"', "'").replace('|', '&#124;').replace('`', "'")
            s = re.sub(r'[ \t]{2,}', ' ', s)
            s = s.replace('\r', '').replace('\n', '\\n')
            curr_idx += 1
            idx_b36 = decimal_to_base36(curr_idx, 2)
            normal_lines.append(f'"{h_str}{idx_b36}UM0{s}"')

        with open(f_bak, 'a', encoding='utf-8') as f:
            f.write(f"\n--- {now.isoformat()} ---\n{data}")
        with open(f_in, 'w', encoding='utf-8') as f:
            f.write('')

    except Exception:
        pass

    return normal_lines

def sync_artifacts_and_logs(base_path, normal_lines):
    artifacts_dir = base_path / "Artifacts"
    if not artifacts_dir.exists():
        return normal_lines

    existing_images = {}
    current_date = "00000000"

    image_pattern = re.compile(r'^"(\d{4})([0-9a-z]{2})UI0([^|]+)\|(\d+x\d+)\|(.*)"$')

    for line in normal_lines:
        date_match = re.match(r'^"D:(\d{8})"$', line)
        if date_match:
            current_date = date_match.group(1)
        else:
            match = image_pattern.match(line)
            if match:
                hhmm, idx_b36, fname, dims, desc = match.groups()
                existing_images[fname] = {
                    'date': current_date,
                    'hhmm': hhmm,
                    'idx_b36': idx_b36,
                    'dims': dims,
                    'desc': desc
                }

    valid_exts = {'.png', '.jpg', '.jpeg'}
    artifact_files = [f for f in artifacts_dir.iterdir() if f.suffix.lower() in valid_exts]

    for img_path in artifact_files:
        fname = img_path.name
        try:
            with Image.open(img_path) as img:
                w, h = img.size
                new_dims = f"{w}x{h}"
        except Exception:
            continue

        if fname in existing_images:
            item = existing_images[fname]
            if item['dims'] != new_dims:
                item['dims'] = new_dims
        else:
            mtime = datetime.datetime.fromtimestamp(img_path.stat().st_mtime)
            mdate = mtime.strftime("%Y%m%d")
            hhmm = mtime.strftime("%H%M")
            desc = "PEND"

            idx_b36 = decimal_to_base36(len(existing_images), 2)

            existing_images[fname] = {
                'date': mdate,
                'hhmm': hhmm,
                'idx_b36': idx_b36,
                'dims': new_dims,
                'desc': desc
            }

    structured_days = {}
    current_date = "00000000"

    for line in normal_lines:
        date_match = re.match(r'^"D:(\d{8})"$', line)
        if date_match:
            current_date = date_match.group(1)
            if current_date not in structured_days:
                structured_days[current_date] = []
        else:
            match = image_pattern.match(line)
            if match:
                fname = match.group(3)
                if fname in existing_images:
                    item = existing_images[fname]
                    rebuilt = f'"{item["hhmm"]}{item["idx_b36"]}UI0{fname}|{item["dims"]}|{item["desc"]}"'
                    structured_days[current_date].append(rebuilt)
                    del existing_images[fname]
            else:
                if current_date in structured_days:
                    structured_days[current_date].append(line)

    for fname, item in list(existing_images.items()):
        mdate = item['date']
        if mdate not in structured_days:
            structured_days[mdate] = []
        rebuilt = f'"{item["hhmm"]}{item["idx_b36"]}UI0{fname}|{item["dims"]}|{item["desc"]}"'
        structured_days[mdate].append(rebuilt)

    sorted_dates = sorted([d for d in structured_days.keys() if d.isdigit() and len(d) == 8])
    rebuilt_normal_lines = []

    for d in sorted_dates:
        rebuilt_normal_lines.append(f'"D:{d}"')
        for log_line in structured_days[d]:
            rebuilt_normal_lines.append(log_line)

    return rebuilt_normal_lines

def perform_synthesis():
    base_path = Path(__file__).parent
    file_raw_logs = base_path / 'RAW_LOGS.txt'
    file_index = base_path / 'index.html'
    file_output = base_path / 'nrocps.github.io.html'

    if not file_raw_logs.exists() or not file_index.exists():
        return

    with open(file_raw_logs, 'r', encoding='utf-8') as f:
        raw_text = f.read().strip()

    prompt_content = ''
    if raw_text.startswith('<!--'):
        prompt_end = raw_text.find('-->')
        if prompt_end != -1:
            prompt_content = raw_text[:prompt_end + 3].strip()
            raw_text = raw_text[prompt_end + 3:].strip()

    normal_lines, tail_lines = parse_raw_logs_structure(raw_text)

    normal_lines = process_input_text_signals(base_path, normal_lines)
    normal_lines = sync_artifacts_and_logs(base_path, normal_lines)

    today_str = datetime.datetime.now().strftime('%Y%m%d')

    all_lines = normal_lines + [f'"D:{today_str}"'] + tail_lines
    final_logs_js = "const RAW_LOGS = [\n" + ",\n".join(all_lines) + "\n];"

    saved_raw_text = f"{prompt_content}\n{final_logs_js}" if prompt_content else final_logs_js
    with open(file_raw_logs, 'w', encoding='utf-8') as f:
        f.write(saved_raw_text)

    with open(file_index, 'r', encoding='utf-8') as f:
        html_markup = f.read()

    s_idx = html_markup.find('const RAW_LOGS = [')
    if s_idx != -1:
        e_idx = html_markup.find('];', s_idx)
        if e_idx != -1:
            e_idx += 2
            html_markup = html_markup[:s_idx] + final_logs_js + html_markup[e_idx:]
    else:
        html_markup = html_markup.replace('let RAW_DATA = [];', f'let RAW_DATA = [];\n{final_logs_js}')

    html_markup = compress_html_markup(html_markup)
    final_artifact = f"{prompt_content}\n{html_markup}" if prompt_content else html_markup

    with open(file_output, 'w', encoding='utf-8') as f:
        f.write(final_artifact)

if __name__ == '__main__':
    perform_synthesis()