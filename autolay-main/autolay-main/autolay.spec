# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['autolay/__main__.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('autolay/tkgm/idler.json', 'tkgm'),
    ],
    hiddenimports=[
        'win32com',
        'win32com.client',
        'win32com.server',
        'pythoncom',
        'win32api',
        'win32con',
        'pywintypes',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'requests',
        'autolay.core.baglanti',
        'autolay.core.hatalar',
        'autolay.core.autocad_bulucu',
        'autolay.cizim.shapes',
        'autolay.cizim.layers',
        'autolay.tkgm.okuyucu',
        'autolay.gui.parsel_dialog',
        'autolay.utils.konsol',
        'autolay.utils.logger',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['playwright', 'pytest', 'numpy', 'pandas'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AutoLay',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,       # Konsol penceresi açılmaz
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
