# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['BI-Tech.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
'plyer.platforms.win.notification',
 'paho.mqtt.client',
    'psutil',
    'threading',
    'datetime',
    'csv',
    'json',
    'pandas',
    'numpy',
    'sklearn.ensemble',
    'sklearn.preprocessing',
    'sklearn.model_selection',
    'requests',
    'time',
    'pynput.mouse',
    'pynput.keyboard',
    'os',
    'win32api',
    'pycaw.pycaw',
    'paho.mqtt.client',
    'plyer'
],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='BI-Tech',
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
    icon=['B.ico'],
)
