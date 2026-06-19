# 🔢 小十三音乐播放器 v1.0

一个用 Python 写的桌面音乐播放器，支持主流音频格式、加密格式解密、倍速播放、主题切换。

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 功能一览

| 功能 | 说明 |
|------|------|
| 🎵 格式支持 | MP3 / FLAC / WAV / AAC / M4A / OGG / OPUS |
| 🔐 加密解密 | 网易云 .ncm、酷狗 .kgm / .kgma |
| ⏱ 倍速控制 | 0.5x ~ 2.5x 无级变速 |
| 🎨 双主题 | 日间 / 夜间，支持随系统时段自动切换 |
| 🖼 专辑封面 | 自动读取并显示内嵌封面 |
| 🔁 播放模式 | 顺序 / 单曲循环 / 随机 / 列表循环 |
| ⚡ 后台解密 | 加密文件在后台线程解密，不卡界面 |
| 📦 免安装 | 提供打包好的 exe，开箱即用 |

---

## 下载

前往 [Releases](https://github.com/FengZaojiyu/-/releases) 下载最新版。

**Windows 用户**：下载 `小十三音乐播放器.exe` 直接运行，无需安装 Python。

---

## 运行（开发者）

```bash
# 克隆
git clone https://github.com/FengZaojiyu/-.git
cd 仓库名

# 装依赖
pip install -r requirements.txt

# 跑起来
python music_player.py
```

### 依赖清单

```text
pygame~=2.6.0
mutagen~=1.47
Pillow>=10.0.0
scipy>=1.10.0
numpy>=1.24.0
pydub>=0.25.0
ncmdump-py>=1.1.6
pycryptodome>=3.20.0
```

### 打包成 exe

```bash
pip install pyinstaller
pyinstaller player.spec --noconfirm
```

---

## 使用方法

1. 打开软件，点击 **📂 打开文件夹** 或 **📁 选择文件** 添加音乐
2. 双击列表中的歌曲播放
3. 使用底部控制栏：播放/暂停、上下曲、音量、播放模式
4. 点击 **速度** 按钮切换倍速（0.5x → 1.0x → 1.5x → 2.0x → 2.5x）
5. 点击 **主题** 按钮切换日间/夜间主题
6. 加密文件（.ncm / .kgm / .kgma）自动解密后播放，首次加载需等待片刻

---

## 技术架构

```
┌─────────────────────────────────────┐
│          tkinter UI 层              │
│  (播放列表 / 控制栏 / 封面 / 进度条) │
├─────────────────────────────────────┤
│         pygame 音频引擎             │
│   (SDL2 后端，支持多格式播放)        │
├──────────────────┬──────────────────┤
│  scipy 倍速重采样  │  后台解密线程    │
│  (numpy + signal) │ (ncmdump/kgm)   │
├──────────────────┴──────────────────┤
│   底层：mutagen / pydub / PIL        │
│   (元数据 / 格式转换 / 封面处理)     │
└─────────────────────────────────────┘
```




---

## 许可证

MIT License

Copyright (c) 2026 小十三 🔢

---

## 致谢

- [ncmdump-py](https://github.com/yourkaixin/ncmdump-py) — .ncm 文件解密
- [pygame](https://www.pygame.org/) — 音频播放引擎
- [mutagen](https://mutagen.readthedocs.io/) — 音频元数据读写
