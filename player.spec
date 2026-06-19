# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['music_player.py'],
    pathex=[],
    binaries=[],
    datas=[('app_icon.ico', '.')],
    hiddenimports=['ncmdump', 'ncmdump.crypto', 'Crypto', 'Crypto.Cipher', 'Crypto.Hash', 'Crypto.Util', 'rich', 'pygments'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'IPython', 'jedi', 'nbformat', 'matplotlib', 'notebook', 'qtconsole',
        'nbconvert', 'nbclient', 'jupyter_client', 'jupyter_core',
        'prompt_toolkit', 'wcwidth',
        'traitlets', 'parso', 'jsonschema', 'lark', 'zmq',
        'setuptools._vendor', 'setuptools.extern',
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='小十三音乐播放器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico'
)
