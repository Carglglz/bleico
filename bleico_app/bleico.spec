# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['bleico_app.py'],
             pathex=['/Users/carlosgilgonzalez/Desktop/IBM_PROJECTS/MICROPYTHON/TOOLS/UTILS/bleico/bleico_app'],
             binaries=[],
             datas=[('HID_DIGITAL_PEN.png', '.'), ('bleicon.icns', '.'), ('bleico_dark.png', '.'), ('UNKNOWN.png', '.'), ('UNKNOWN_dark.png', '.'), ('HID_DIGITAL_PEN_dark.png', '.'), ('GENERIC_THERMOMETER_dark.png', '.'),
 ('Bluelogo.png', '.'), ('Bluelogo_dark.png', '.'), ('GENERIC_THERMOMETER.png', '.'), ('BlueL.png', '.'), ('bleico.png', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='bleico',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='bleicon.icns')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='bleico')
app = BUNDLE(coll,
             name='bleico.app',
             icon='bleicon.icns',
             bundle_identifier=None)
