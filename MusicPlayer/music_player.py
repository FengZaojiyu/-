#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import tkinter as tk
from tkinter import ttk, filedialog
import os, sys, json, random, tempfile, threading, time
from pathlib import Path
from io import BytesIO

import pygame
import numpy as np
import mutagen
from PIL import Image, ImageTk, ImageDraw

# ============ 主题 ============
THEMES = {
    'day': {
        'bg': '#f5f5f5', 'fg': '#333333', 'card': '#ffffff',
        'accent': '#4a90d9', 'highlight': '#357abd',
        'text_sec': '#888888', 'text_status': '#999999',
        'prog_bg': '#d0d0d0', 'prog_fg': '#4a90d9',
        'list_bg': '#ffffff', 'list_fg': '#333333',
        'list_sel_bg': '#4a90d9', 'list_sel_fg': '#ffffff',
        'btn_bg': '#e8e8e8', 'btn_hover': '#4a90d9',
    },
    'night': {
        'bg': '#1a1a2e', 'fg': '#e0e0e0', 'card': '#16213e',
        'accent': '#e94560', 'highlight': '#0f3460',
        'text_sec': '#888888', 'text_status': '#666666',
        'prog_bg': '#0f3460', 'prog_fg': '#e94560',
        'list_bg': '#16213e', 'list_fg': '#e0e0e0',
        'list_sel_bg': '#0f3460', 'list_sel_fg': '#e94560',
        'btn_bg': '#16213e', 'btn_hover': '#0f3460',
    },
    'dusty_rose': {
        'name': '烟粉玫瑰', 'bg': '#f5ecec', 'fg': '#5a4545', 'card': '#faf2f2',
        'accent': '#c88080', 'highlight': '#e0b0b0',
        'text_sec': '#9a7a7a', 'text_status': '#b89a9a',
        'prog_bg': '#e0c0c0', 'prog_fg': '#c88080',
        'list_bg': '#faf2f2', 'list_fg': '#5a4545',
        'list_sel_bg': '#e0b0b0', 'list_sel_fg': '#ffffff',
        'btn_bg': '#f0e0e0', 'btn_hover': '#e0b0b0',
    },
    'slate_blue': {
        'name': '雾蓝灰', 'bg': '#ececf0', 'fg': '#3a3a50', 'card': '#f5f5f8',
        'accent': '#7a7a9a', 'highlight': '#a0a0c0',
        'text_sec': '#7a7a8a', 'text_status': '#9a9aaa',
        'prog_bg': '#c0c0d8', 'prog_fg': '#7a7a9a',
        'list_bg': '#f5f5f8', 'list_fg': '#3a3a50',
        'list_sel_bg': '#a0a0c0', 'list_sel_fg': '#ffffff',
        'btn_bg': '#e8e8f0', 'btn_hover': '#a0a0c0',
    },
    'sage_green': {
        'name': '茶绿', 'bg': '#edf1ec', 'fg': '#3a4a3a', 'card': '#f5f8f4',
        'accent': '#7a9a7a', 'highlight': '#a0c0a0',
        'text_sec': '#7a8a7a', 'text_status': '#9aaa9a',
        'prog_bg': '#c0d8c0', 'prog_fg': '#7a9a7a',
        'list_bg': '#f5f8f4', 'list_fg': '#3a4a3a',
        'list_sel_bg': '#a0c0a0', 'list_sel_fg': '#ffffff',
        'btn_bg': '#e8f0e8', 'btn_hover': '#a0c0a0',
    },
    'warm_beige': {
        'name': '暖沙色', 'bg': '#f5f0ea', 'fg': '#4a4035', 'card': '#faf6f0',
        'accent': '#b09878', 'highlight': '#d0b898',
        'text_sec': '#8a7a6a', 'text_status': '#aa9a8a',
        'prog_bg': '#e0d0c0', 'prog_fg': '#b09878',
        'list_bg': '#faf6f0', 'list_fg': '#4a4035',
        'list_sel_bg': '#d0b898', 'list_sel_fg': '#ffffff',
        'btn_bg': '#f0e8e0', 'btn_hover': '#d0b898',
    },
    'soft_gray': {
        'name': '柔灰色', 'bg': '#eaeaea', 'fg': '#3a3a3a', 'card': '#f2f2f2',
        'accent': '#888888', 'highlight': '#b0b0b0',
        'text_sec': '#7a7a7a', 'text_status': '#9a9a9a',
        'prog_bg': '#c8c8c8', 'prog_fg': '#888888',
        'list_bg': '#f2f2f2', 'list_fg': '#3a3a3a',
        'list_sel_bg': '#b0b0b0', 'list_sel_fg': '#ffffff',
        'btn_bg': '#e0e0e0', 'btn_hover': '#b0b0b0',
    },
}

MORANDI_THEMES = {'dusty_rose', 'slate_blue', 'sage_green', 'warm_beige', 'soft_gray'}

THEME_PREVIEW = {
    'day': ('#f5f5f5', '#4a90d9'), 'night': ('#1a1a2e', '#e94560'),
    'dusty_rose': ('#f5ecec', '#c88080'), 'slate_blue': ('#ececf0', '#7a7a9a'),
    'sage_green': ('#edf1ec', '#7a9a7a'), 'warm_beige': ('#f5f0ea', '#b09878'),
    'soft_gray': ('#eaeaea', '#888888'),
}

# ============ 配置 ============
SUPPORTED_EXTS = {'.mp3', '.flac', '.wav', '.aac', '.m4a', '.ogg',
                  '.wma', '.ape', '.aiff', '.dsf', '.dff', '.opus'}
ENCRYPTED_EXTS = {
    '.ncm',
    '.kgm', '.kgma',
}
ALL_AUDIO_EXTS = SUPPORTED_EXTS | ENCRYPTED_EXTS

DC_OUT_DIR = Path(sys.executable).parent / 'decrypted'

SPEEDS = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
CONFIG = Path.home() / '.music_player_config.json'
TEMP_DIR = Path(tempfile.gettempdir()) / 'thirteen_player'
TEMP_DIR.mkdir(exist_ok=True)

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
pygame.init()



def _decrypt_kgm(fp, stem):
    """Kugou .kgm / .kgma 解密"""
    KGM_MAGIC = bytes([0x7C, 0xD5, 0x32, 0xEB, 0x86, 0x02, 0x7F, 0x4B,
                       0xA8, 0xAF, 0xA6, 0x8E, 0x0F, 0xFF, 0x99, 0x14])
    KGM_HEADER_SIZE = 1024
    KGM_PUBKEY = bytes([
        0x6C, 0xA9, 0x45, 0x37, 0x0C, 0x15, 0x49, 0x29,
        0x5A, 0xBE, 0x91, 0x5B, 0x07, 0xDC, 0xBE, 0x04,
        0x60, 0x83, 0x30, 0xD2, 0x21, 0x0D, 0xBB, 0x05,
        0x4C, 0x7B, 0x72, 0x65, 0x82, 0x5D, 0xCA, 0x7C,
        0x1D, 0x74, 0xFC, 0x5A, 0xA1, 0xCF, 0x72, 0x40,
        0x6B, 0x22, 0xA7, 0x58, 0x0D, 0x05, 0x1D, 0x64,
        0x4E, 0xBA, 0x56, 0x6D, 0x9D, 0x11, 0xA1, 0x2A,
        0x54, 0x63, 0x94, 0x21, 0x9E, 0x1A, 0x5D, 0xAE,
        0x64, 0x89, 0xCF, 0x35, 0x4B, 0x3A, 0xD3, 0x42,
        0x34, 0x0A, 0xA5, 0xAA, 0x2C, 0x32, 0x88, 0x42,
        0x06, 0x56, 0x10, 0x7E, 0x07, 0xBF, 0xB7, 0x4B,
        0x9A, 0x6B, 0x7D, 0x51, 0x0D, 0xB0, 0xC3, 0xA8,
        0x64, 0x4E, 0x10, 0xD2, 0x31, 0x04, 0x41, 0x09,
        0x30, 0xAE, 0x00, 0x36, 0x46, 0x29, 0x9A, 0xAD,
        0x19, 0x3E, 0x14, 0x1F, 0x44, 0xFE, 0xD6, 0x7B,
        0xEE, 0x6B, 0x0B, 0x09, 0x88, 0xB8, 0xBF, 0x82,
        0xFC, 0x0E, 0x3A, 0x5C, 0xB0, 0x90, 0x4E, 0x57,
        0x3D, 0x3B, 0xDF, 0xA3, 0x5F, 0x42, 0x0D, 0xED,
        0x27, 0x19, 0xFB, 0xEB, 0x77, 0x92, 0x9B, 0x59,
        0x43, 0x86, 0xB5, 0x3E, 0xD5, 0x1E, 0x3D, 0x82,
        0xF4, 0x00, 0x73, 0x5B, 0x08, 0xDC, 0x5E, 0x2A,
        0xC0, 0x64, 0x70, 0x1B, 0x2C, 0xE3, 0x10, 0x42,
        0x48, 0x76, 0x60, 0x14, 0xB6, 0xC8, 0x22, 0x4C,
        0x7A, 0xDD, 0x3C, 0x09, 0x1A, 0x87, 0x84, 0x5A,
        0x87, 0x49, 0x17, 0xE7, 0x74, 0x98, 0xB0, 0x4E,
        0x1B, 0x6F, 0x4F, 0x4E, 0x4D, 0x05, 0x56, 0xD2,
        0x19, 0x0A, 0x9B, 0x00, 0xB4, 0x4B, 0x28, 0x49,
        0x86, 0xD6, 0x2A, 0x86, 0x5C, 0x93, 0xFC, 0x1D,
        0x5E, 0x0A, 0xD4, 0x65, 0x91, 0x07, 0x88, 0xAA,
        0x1E, 0x79, 0x12, 0x73, 0x8D, 0x63, 0xA2, 0xC8,
        0x32, 0xBC, 0x5E, 0xB6, 0x19, 0xF9, 0x68, 0x50,
        0x9F, 0xBF, 0xDB, 0x02, 0xBF, 0x3F, 0x16, 0xF2,
    ])
    KGM_MEND = bytes([0x5E, 0xAF, 0x93, 0xE3, 0x0E, 0x9E, 0x1F, 0x9E])
    with open(fp, 'rb') as f:
        raw = f.read()
    if len(raw) < KGM_HEADER_SIZE:
        raise ValueError("KGM file too small")
    header = raw[:KGM_HEADER_SIZE]
    ownkey = header[0x1C:0x1C+17]
    body = bytearray(raw[KGM_HEADER_SIZE:])
    for i in range(len(body)):
        idx = i % len(KGM_PUBKEY)
        m_idx = idx % len(KGM_MEND)
        body[i] = (body[i] ^ ownkey[i % len(ownkey)] ^ KGM_PUBKEY[idx] ^ KGM_MEND[m_idx]) & 0xFF
    body = bytes(body).rstrip(b'\x00')
    out = DC_OUT_DIR / f'{stem}.mp3'
    with open(out, 'wb') as f:
        f.write(body)
    return str(out)


def decrypt_file(fp):
    """Decrypt encrypted music file, return playable path"""
    ext = Path(fp).suffix.lower()
    stem = Path(fp).stem
    DC_OUT_DIR.mkdir(parents=True, exist_ok=True)
    for e in ['.mp3', '.flac', '.wav', '.ogg']:
        c = DC_OUT_DIR / f'{stem}{e}'
        if c.exists():
            return str(c)
    if ext == '.ncm':
        from ncmdump import NeteaseCloudMusicFile
        ncm_file = NeteaseCloudMusicFile(fp)
        ncm_file.decrypt()
        out = DC_OUT_DIR / f'{stem}.mp3'
        ncm_file.dump_music(str(out))
        return str(out)

    elif ext in ('.kgm', '.kgma'):
        return _decrypt_kgm(fp, stem)
    return fp


def fmt(t):
    if t < 0:
        return "00:00"
    return f"{int(t//60):02d}:{int(t%60):02d}"


def make_cover(s=250):
    img = Image.new('RGBA', (s, s), (22, 33, 62, 255))
    d = ImageDraw.Draw(img)
    c = s // 2
    r = s // 2 - 10
    d.ellipse([c-r, c-r, c+r, c+r], outline='#0f3460', width=2)
    d.ellipse([c-30, c-30, c+30, c+30], outline='#e94560', width=3)
    d.text((c-5, c-7), chr(9835), fill='#e94560')
    return img


def get_meta(fp):
    info = {'title': Path(fp).stem, 'artist': '未知', 'album': '未知', 'dur': 0, 'cover': None}
    try:
        a = mutagen.File(fp)
        if not a:
            return info
        info['dur'] = int(getattr(getattr(a, 'info', None), 'length', 0))
        t = getattr(a, 'tags', None) or {}
        for k in ['TIT2', '\xa9nam', 'title']:
            if k in t:
                info['title'] = str(t[k][0] if isinstance(t[k], list) else t[k])
                break
        for k in ['TPE1', '\xa9ART', 'artist']:
            if k in t:
                info['artist'] = str(t[k][0] if isinstance(t[k], list) else t[k])
                break
        for k in ['TALB', '\xa9alb', 'album']:
            if k in t:
                info['album'] = str(t[k][0] if isinstance(t[k], list) else t[k])
                break
        cd = None
        if hasattr(a, 'pictures') and a.pictures:
            cd = a.pictures[0].data
        elif t:
            for k in t:
                if 'APIC' in k or 'COVER' in k:
                    d = t[k]
                    cd = d.data if hasattr(d, 'data') else (d if isinstance(d, bytes) else None)
                    break
        if cd:
            try:
                im = Image.open(BytesIO(cd))
                im.thumbnail((250, 250))
                buf = BytesIO()
                im.save(buf, format='PNG')
                info['cover'] = buf.getvalue()
            except:
                pass
    except:
        pass
    return info


class PlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("小十三音乐播放器")
        self.root.geometry("500x740")
        self.root.minsize(420, 620)
        self.root.configure(bg='#1a1a2e')
        self.playlist = []
        self.cur = -1
        self.mode = 0
        self.speed_idx = 2
        self.playing = False
        self.paused = False
        self.dur = 0
        self._seek_base = 0.0
        self._seek_clock = 0.0
        self._decrypted_fp = None
        self._timer_id = None
        self._speed_file = None
        self._decrypting = False  # 是否正在解密
        self._theme_mode = 'day' if 6 <= time.localtime().tm_hour < 18 else 'night'
        self.C = THEMES[self._theme_mode].copy()
        self._auto_theme = True
        self._build_ui()
        self._load_cfg()
        self._init_media_keys()

    def _init_media_keys(self):
        try:
            import keyboard
            keyboard.add_hotkey('play/pause media', self._on_media_play_pause, suppress=False)
            keyboard.add_hotkey('next track', self._on_media_next, suppress=False)
            keyboard.add_hotkey('previous track', self._on_media_prev, suppress=False)
            keyboard.add_hotkey('stop media', self._on_media_stop, suppress=False)
        except Exception:
            pass

    def _on_media_play_pause(self):
        self.root.after(0, self.toggle)

    def _on_media_next(self):
        self.root.after(0, self.next)

    def _on_media_prev(self):
        self.root.after(0, self.prev)

    def _on_media_stop(self):
        self.root.after(0, self.stop)

    def _build_ui(self):
        C = self.C
        self.root.configure(bg=C['bg'])
        self.cover_lbl = tk.Label(self.root, bg=C['card'])
        self.cover_lbl.pack(pady=(12, 4))
        self._set_cover(make_cover())
        self.title_lbl = tk.Label(self.root, text="小十三音乐播放器",
            font=('Microsoft YaHei UI', 16, 'bold'), fg=C['fg'], bg=C['bg'])
        self.title_lbl.pack(pady=(2, 0))
        self.artist_lbl = tk.Label(self.root, text="点击打开音乐",
            font=('Microsoft YaHei UI', 11), fg=C['text_sec'], bg=C['bg'])
        self.artist_lbl.pack(pady=(0, 6))
        self.pf = tk.Frame(self.root, bg=C['bg'])
        self.pf.pack(fill='x', padx=20, pady=(2, 2))
        self.time_cur = tk.Label(self.pf, text="00:00", font=('Consolas', 9), fg=C['text_sec'], bg=C['bg'])
        self.time_cur.pack(side='left')
        self.prog = ttk.Progressbar(self.pf, length=300, mode='determinate')
        self.prog.pack(side='left', fill='x', expand=True, padx=6)
        self.prog.bind('<Button-1>', self._seek)
        self.time_total = tk.Label(self.pf, text="00:00", font=('Consolas', 9), fg=C['text_sec'], bg=C['bg'])
        self.time_total.pack(side='right')
        self.sf = tk.Frame(self.root, bg=C['bg'])
        self.sf.pack(pady=(4, 2))
        tk.Label(self.sf, text="倍速", font=('Microsoft YaHei UI', 9), fg=C['text_sec'], bg=C['bg']).pack(side='left', padx=(0, 4))
        self.speed_btn = tk.Button(self.sf, text="1.0x", font=('Microsoft YaHei UI', 10, 'bold'),
            fg=C['fg'], bg=C['btn_bg'], bd=0, padx=12, pady=2,
            activebackground=C['highlight'], activeforeground=C['accent'],
            cursor='hand2', command=self._cycle_speed)
        self.speed_btn.pack(side='left')
        self.cf = tk.Frame(self.root, bg=C['bg'])
        self.cf.pack(pady=(8, 4))
        self.mode_btn = self._btn(self.cf, chr(128257), self._cycle_mode, 36)
        self.mode_btn.pack(side='left', padx=5)
        self._btn(self.cf, chr(9198), self.prev, 40).pack(side='left', padx=5)
        self.play_btn = self._btn(self.cf, chr(9654), self.toggle, 52, 16)
        self.play_btn.pack(side='left', padx=5)
        self._btn(self.cf, chr(9197), self.next, 40).pack(side='left', padx=5)
        self.bf = tk.Frame(self.root, bg=C['bg'])
        self.bf.pack(pady=(4, 4))
        self._btn(self.bf, "打开文件", self.open_files, padx=14).pack(side='left', padx=4)
        self._btn(self.bf, "打开文件夹", self.open_folder, padx=14).pack(side='left', padx=4)
        self.theme_btn = self._btn(self.bf, chr(127774) if self._theme_mode == 'day' else chr(127769), self._toggle_theme, 36)
        self.theme_btn.pack(side='left', padx=4)
        self.auto_btn = self._btn(self.bf, chr(9200), self._toggle_auto_theme, 36)
        self.auto_btn.pack(side='left', padx=4)
        self._update_auto_btn_ui()
        self.listbox = tk.Listbox(self.root, bg=C['list_bg'], fg=C['list_fg'],
            selectbackground=C['list_sel_bg'], selectforeground=C['list_sel_fg'],
            relief='flat', bd=0, highlightthickness=0,
            font=('Microsoft YaHei UI', 10), activestyle='none')
        self.listbox.pack(fill='both', expand=True, padx=16, pady=(2, 2))
        sb = tk.Scrollbar(self.listbox)
        sb.pack(side='right', fill='y')
        self.listbox.config(yscrollcommand=sb.set)
        sb.config(command=self.listbox.yview)
        self.listbox.bind('<Double-Button-1>', lambda e: self._sel() if self.listbox.curselection() else None)
        self.vf = tk.Frame(self.root, bg=C['bg'])
        self.vf.pack(fill='x', padx=20, pady=(2, 8))
        self.vol_lbl = tk.Label(self.vf, text=chr(128266), font=('Segoe UI', 10), fg=C['text_sec'], bg=C['bg'])
        self.vol_lbl.pack(side='left')
        self.vol = ttk.Scale(self.vf, from_=0, to=100, orient='horizontal', command=self._set_vol)
        self.vol.set(60)
        self.vol.pack(side='left', fill='x', expand=True, padx=6)
        pygame.mixer.music.set_volume(0.6)
        self.status = tk.Label(self.root, text="就绪", font=('Microsoft YaHei UI', 9), fg=C['text_status'], bg=C['bg'])
        self.status.pack(pady=(0, 2))
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self._apply_style()
        self._tick()
        self._theme_check()

    def _apply_style(self):
        s = ttk.Style()
        s.theme_use('clam')
        s.configure('TProgressbar', background=self.C['prog_fg'], troughcolor=self.C['prog_bg'], bordercolor=self.C['bg'])
        s.configure('TScale', background=self.C['bg'], troughcolor=self.C['prog_bg'])

    def _set_theme(self, theme_id):
        self._theme_mode = theme_id
        self.C = THEMES[theme_id].copy()
        self._apply_full_theme()
        if theme_id in MORANDI_THEMES:
            self._auto_theme = False
        self._update_auto_btn_ui()

    def _open_theme_selector(self):
        top = tk.Toplevel(self.root)
        top.title("选择主题")
        top.configure(bg=self.C['card'])
        top.resizable(False, False)
        top.transient(self.root)
        top.grab_set()
        f = tk.Frame(top, bg=self.C['card'], padx=16, pady=12)
        f.pack()
        tk.Label(f, text="选择主题", font=('Microsoft YaHei UI', 13, 'bold'), fg=self.C['fg'], bg=self.C['card']).pack(anchor='w', pady=(0, 10))
        grid = tk.Frame(f, bg=self.C['card'])
        grid.pack()
        themes_ui = [('day', chr(127774), THEME_PREVIEW['day']), ('night', chr(127769), THEME_PREVIEW['night'])]
        for tid, tinfo in THEMES.items():
            if tid not in ('day', 'night'):
                themes_ui.append((tid, tinfo.get('name', tid), THEME_PREVIEW[tid]))
        for i, (tid, tname, (bg_c, ac_c)) in enumerate(themes_ui):
            row, col = divmod(i, 4)
            cell = tk.Frame(grid, bg=self.C['card'], padx=4, pady=4)
            cell.grid(row=row, column=col)
            swatch = tk.Canvas(cell, width=56, height=44, bd=0, highlightthickness=0, bg=self.C['card'])
            swatch.pack()
            swatch.create_rectangle(0, 0, 56, 44, fill=bg_c, outline=ac_c, width=2)
            swatch.create_rectangle(4, 4, 52, 40, fill=bg_c, outline='')
            swatch.create_oval(20, 8, 36, 24, fill=ac_c, outline='')
            if tid == self._theme_mode:
                swatch.create_rectangle(0, 0, 56, 44, outline='#e94560' if self.C['bg'] == '#1a1a2e' else '#333', width=3)
            swatch.bind('<Button-1>', lambda e, t=tid: self._on_theme_selected(top, t))
            name_lbl = tk.Label(cell, text=tname, font=('Microsoft YaHei UI', 8), fg=self.C['text_sec'], bg=self.C['card'])
            name_lbl.pack()
            name_lbl.bind('<Button-1>', lambda e, t=tid: self._on_theme_selected(top, t))
        top.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - top.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - top.winfo_height()) // 2
        top.geometry(f"+{x}+{y}")

    def _on_theme_selected(self, window, theme_id):
        self._set_theme(theme_id)
        window.destroy()

    def _toggle_theme(self):
        self._open_theme_selector()

    def _toggle_auto_theme(self):
        if self._theme_mode in MORANDI_THEMES:
            return
        self._auto_theme = not self._auto_theme
        if self._auto_theme:
            h = time.localtime().tm_hour
            expected = 'day' if 6 <= h < 18 else 'night'
            if expected != self._theme_mode:
                self._set_theme(expected)
        self._update_auto_btn_ui()

    def _update_auto_btn_ui(self):
        if self._theme_mode in MORANDI_THEMES:
            self.auto_btn.config(text=chr(128683), state='disabled')
        elif self._auto_theme:
            self.auto_btn.config(text=chr(9200), state='normal')
        else:
            self.auto_btn.config(text=chr(128347), state='normal')

    def _apply_full_theme(self):
        C = self.C
        self.root.configure(bg=C['bg'])
        self.cover_lbl.configure(bg=C['card'])
        self.title_lbl.configure(fg=C['fg'], bg=C['bg'])
        self.artist_lbl.configure(fg=C['text_sec'], bg=C['bg'])
        self.pf.configure(bg=C['bg'])
        self.time_cur.configure(fg=C['text_sec'], bg=C['bg'])
        self.time_total.configure(fg=C['text_sec'], bg=C['bg'])
        self.sf.configure(bg=C['bg'])
        for w in self.sf.winfo_children():
            if isinstance(w, tk.Label):
                w.configure(fg=C['text_sec'], bg=C['bg'])
            if isinstance(w, tk.Button):
                w.configure(fg=C['fg'], bg=C['btn_bg'], activebackground=C['highlight'], activeforeground=C['accent'])
        self.cf.configure(bg=C['bg'])
        self.bf.configure(bg=C['bg'])
        for w in list(self.cf.winfo_children()) + list(self.bf.winfo_children()):
            if isinstance(w, tk.Button):
                w.configure(fg=C['fg'], bg=C['btn_bg'], activebackground=C['highlight'], activeforeground=C['accent'])
        self.listbox.configure(bg=C['list_bg'], fg=C['list_fg'], selectbackground=C['list_sel_bg'], selectforeground=C['list_sel_fg'])
        self.vf.configure(bg=C['bg'])
        self.vol_lbl.configure(fg=C['text_sec'], bg=C['bg'])
        self.status.configure(fg=C['text_status'], bg=C['bg'])
        self._apply_style()

    def _theme_check(self):
        if self._theme_mode in MORANDI_THEMES or not self._auto_theme:
            self.root.after(3600000, self._theme_check)
            return
        h = time.localtime().tm_hour
        expected = 'day' if 6 <= h < 18 else 'night'
        if expected != self._theme_mode:
            self._theme_mode = expected
            self.C = THEMES[self._theme_mode].copy()
            self._apply_full_theme()
            self._update_auto_btn_ui()
        self.root.after(3600000, self._theme_check)

    def _btn(self, p, t, c, w=0, fs=13, padx=10):
        kw = {'text': t, 'font': ('Microsoft YaHei UI', fs), 'fg': self.C['fg'], 'bg': self.C['btn_bg'],
              'activebackground': self.C['highlight'], 'activeforeground': self.C['accent'],
              'bd': 0, 'relief': 'flat', 'cursor': 'hand2', 'command': c, 'padx': padx}
        if w:
            kw['width'] = w // 10
        return tk.Button(p, **kw)

    def _set_cover(self, img):
        self._cover = ImageTk.PhotoImage(img)
        self.cover_lbl.config(image=self._cover)

    def _sel(self):
        self.cur = self.listbox.curselection()[0]
        self._play()

    def _play(self):
        """播放音乐 — 加密文件在后台线程解密，不卡UI"""
        if self.cur < 0 or self.cur >= len(self.playlist):
            return
        if self._decrypting:
            return  # 正在解密中，忽略重复请求
        fp = self.playlist[self.cur]
        self._decrypted_fp = None
        self._clean_speed()
        ext = Path(fp).suffix.lower()

        if ext in ENCRYPTED_EXTS:
            self._decrypting = True
            self.status.config(text="解密中... %s" % Path(fp).name)
            # 进度条改为不确定模式(跑马灯)，表示正在处理
            self.prog.config(mode='indeterminate')
            self.prog.start(15)
            self.root.update()

            def _decrypt_thread():
                try:
                    decrypted = decrypt_file(fp)
                    self.root.after(0, _decrypt_done, decrypted)
                except Exception as de:
                    self.root.after(0, _decrypt_failed, str(de))

            def _decrypt_done(decrypted):
                self._decrypting = False
                self.prog.stop()
                self.prog.config(mode='determinate')
                self._decrypted_fp = decrypted
                self._play_decrypted(decrypted)

            def _decrypt_failed(err):
                self._decrypting = False
                self.prog.stop()
                self.prog.config(mode='determinate')
                self.status.config(text="解密失败: %s" % err)

            threading.Thread(target=_decrypt_thread, daemon=True).start()
        else:
            # 普通文件直接播放
            self._play_decrypted(fp)

    def _play_decrypted(self, fp):
        """加载并播放已解密的文件（在主线程执行）"""
        try:
            speed = SPEEDS[self.speed_idx]
            try:
                if speed == 1.0:
                    pygame.mixer.music.load(fp)
                    pygame.mixer.music.play()
                else:
                    self._play_with_speed(fp, speed)
            except pygame.error:
                try:
                    from pydub import AudioSegment
                    wav = str(TEMP_DIR / (Path(fp).stem + ".wav"))
                    AudioSegment.from_file(fp).export(wav, format="wav")
                    pygame.mixer.music.load(wav)
                    pygame.mixer.music.play()
                except Exception:
                    pass
            self._seek_base = 0.0
            self._seek_clock = time.time()
            self.playing = True
            self.paused = False
            self.play_btn.config(text=chr(9208))
            self._show_meta(fp)
            self.listbox.selection_clear(0, 'end')
            self.listbox.selection_set(self.cur)
            self.listbox.see(self.cur)
            self.status.config(text=Path(fp).name)
        except Exception as e:
            self.status.config(text="播放失败: %s" % e)

    def _play_with_speed(self, fp, speed):
        from pydub import AudioSegment
        audio = AudioSegment.from_file(fp)
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
        if audio.channels == 2:
            samples = samples.reshape(-1, 2)
        new_len = int(len(samples) / speed)
        if new_len < 100:
            return
        from scipy import signal as sp_signal
        if samples.ndim == 1:
            resampled = sp_signal.resample(samples, new_len)
        else:
            resampled = np.column_stack([sp_signal.resample(samples[:, c], new_len) for c in range(samples.shape[1])])
        resampled = np.clip(resampled, -32768, 32767).astype(np.int16)
        out = TEMP_DIR / ("s%d_%d.wav" % (id(fp), int(speed*100)))
        import wave
        with wave.open(str(out), 'w') as wf:
            wf.setnchannels(audio.channels)
            wf.setsampwidth(2)
            wf.setframerate(audio.frame_rate)
            wf.writeframes(resampled.tobytes())
        self._speed_file = out
        pygame.mixer.music.load(str(out))
        pygame.mixer.music.play()

    def _clean_speed(self):
        if self._speed_file and self._speed_file.exists():
            try:
                self._speed_file.unlink()
            except:
                pass
            self._speed_file = None

    def toggle(self):
        if not self.playlist:
            self.open_files()
            return
        if self.cur < 0:
            self.cur = 0
            self._play()
            return
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.paused = True
            self.play_btn.config(text=chr(9654))
            self.status.config(text="暂停")
        else:
            pygame.mixer.music.unpause()
            self.paused = False
            self.play_btn.config(text=chr(9208))
            self.status.config(text="继续")

    def prev(self):
        if not self.playlist:
            return
        if pygame.mixer.music.get_pos() > 3000:
            pygame.mixer.music.rewind()
            return
        if self.mode == 2:
            self.cur = random.randint(0, len(self.playlist)-1)
        else:
            self.cur = (self.cur - 1) % len(self.playlist)
        self._play()

    def next(self):
        if not self.playlist:
            return
        if self._decrypting:
            return  # 解密中不切歌
        if self.mode == 1:
            self._play()
            return
        if self.mode == 2:
            self.cur = random.randint(0, len(self.playlist)-1)
        else:
            self.cur = (self.cur + 1) % len(self.playlist)
        self._play()

    def _seek(self, ev):
        w = ev.widget.winfo_width()
        if w <= 0:
            return
        pct = ev.x / w
        if self.dur > 0 and self.cur >= 0:
            target = pct * self.dur
            seek_fp = self._decrypted_fp if self._decrypted_fp else self.playlist[self.cur]
            try:
                pygame.mixer.music.load(seek_fp)
                pygame.mixer.music.play(start=target)
                if self.paused:
                    pygame.mixer.music.pause()
            except:
                pass
            self._seek_base = target
            self._seek_clock = time.time()
            self.prog['value'] = pct * 100
            self.time_cur.config(text=fmt(target))

    def _cycle_speed(self):
        self.speed_idx = (self.speed_idx + 1) % len(SPEEDS)
        s = SPEEDS[self.speed_idx]
        txt = ("%.2f" % s).rstrip('0').rstrip('.') + 'x'
        self.speed_btn.config(text=txt)

    def _cycle_mode(self):
        self.mode = (self.mode + 1) % 3
        self.mode_btn.config(text=[chr(128257), chr(128258), chr(128256)][self.mode])

    def _set_vol(self, v):
        v = int(float(v))
        pygame.mixer.music.set_volume(v / 100)
        self.vol_lbl.config(text=chr(128263) if v == 0 else chr(128265) if v < 50 else chr(128266))

    def _show_meta(self, fp):
        m = get_meta(fp)
        self.title_lbl.config(text=m['title'])
        self.artist_lbl.config(text="%s - %s" % (m['artist'], m['album']))
        self.dur = m['dur']
        self.time_total.config(text=fmt(m['dur']))
        if m['cover']:
            try:
                self._set_cover(Image.open(BytesIO(m['cover'])))
            except:
                self._set_cover(make_cover())
        else:
            self._set_cover(make_cover())

    def _tick(self):
        if pygame.mixer.music.get_busy():
            elapsed = time.time() - self._seek_clock
            pos = self._seek_base + elapsed
            if pos > self.dur:
                pos = self.dur
            if self.dur > 0:
                self.prog['value'] = min(pos / self.dur * 100, 100)
                self.time_cur.config(text=fmt(pos))
        elif self.playing and not self.paused and self.cur >= 0:
            if not self._decrypting:  # 解密中不自动切歌
                self.next()
        self._timer_id = self.root.after(300, self._tick)

    def open_files(self):
        fs = filedialog.askopenfilenames(title="选择音乐文件", filetypes=[
            ("所有音频", " ".join("*%s" % e for e in ALL_AUDIO_EXTS)),
            ("加密文件", "*.ncm *.kgm *.kgma"),
            ("普通音频", " ".join("*%s" % e for e in SUPPORTED_EXTS)),
            ("全部", "*.*")])
        if fs:
            n = 0
            for f in fs:
                if f not in self.playlist:
                    self.playlist.append(f)
                    name = Path(f).stem
                    if Path(f).suffix.lower() in ENCRYPTED_EXTS:
                        name = "[E] " + name
                    self.listbox.insert('end', name)
                    n += 1
            if n > 0 and self.cur < 0:
                self.cur = 0
                self._play()
            self.status.config(text="添加 %d 首" % n)

    def open_folder(self):
        d = filedialog.askdirectory(title="选择文件夹")
        if d:
            n = 0
            for r, _, fs in os.walk(d):
                for f in sorted(fs):
                    if Path(f).suffix.lower() in ALL_AUDIO_EXTS:
                        full = os.path.join(r, f)
                        if full not in self.playlist:
                            self.playlist.append(full)
                            name = Path(f).stem
                            if Path(f).suffix.lower() in ENCRYPTED_EXTS:
                                name = "[E] " + name
                            self.listbox.insert('end', name)
                            n += 1
            if n > 0 and self.cur < 0:
                self.cur = 0
                self._play()
            self.status.config(text="添加 %d 首" % n)

    def _save_cfg(self):
        try:
            d = {'vol': int(self.vol.get()), 'mode': self.mode, 'speed': self.speed_idx,
                 'pl': self.playlist[:100], 'idx': self.cur,
                 'theme': self._theme_mode, 'auto_theme': self._auto_theme}
            CONFIG.write_text(json.dumps(d), encoding='utf-8')
        except:
            pass

    def _load_cfg(self):
        try:
            if CONFIG.exists():
                d = json.loads(CONFIG.read_text(encoding='utf-8'))
                self.vol.set(d.get('vol', 60))
                pygame.mixer.music.set_volume(d.get('vol', 60) / 100)
                self.mode = d.get('mode', 0)
                self.mode_btn.config(text=[chr(128257), chr(128258), chr(128256)][self.mode])
                self.speed_idx = d.get('speed', 2)
                self.speed_btn.config(text="1.0x")
                saved_theme = d.get('theme', self._theme_mode)
                if saved_theme in THEMES:
                    self._theme_mode = saved_theme
                    self.C = THEMES[saved_theme].copy()
                    self._apply_full_theme()
                self._auto_theme = d.get('auto_theme', self._auto_theme)
                self._update_auto_btn_ui()
                for f in d.get('pl', []):
                    if os.path.isfile(f):
                        self.playlist.append(f)
                        self.listbox.insert('end', Path(f).stem)
                idx = d.get('idx', -1)
                if 0 <= idx < len(self.playlist):
                    self.cur = idx
                    self._play()
        except:
            pass

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False
        self.play_btn.config(text=chr(9654))
        self.prog['value'] = 0
        self.time_cur.config(text="00:00")
        self.status.config(text="已停止")

    def _close(self):
        try:
            import keyboard
            keyboard.unhook_all()
        except:
            pass
        self._save_cfg()
        pygame.mixer.music.stop()
        self._clean_speed()
        if self._timer_id:
            self.root.after_cancel(self._timer_id)
        self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = PlayerApp(root)
    root.mainloop()
