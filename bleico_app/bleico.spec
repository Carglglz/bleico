# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['bleico_app.py'],
             pathex=['.'],
             binaries=[],
             datas=[('../bleico/icons/*.png', 'icons'),
                    ('../bleico/sounds/*.wav', 'sounds'),
                    ('credits.txt', '.'),
                    ('/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages/bleak_sigspec/characteristics_xml/*.xml', 'bleak_sigspec/characteristics_xml/')],
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
          console=False , icon='bleico.icns')
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
             icon='bleico.icns',
             bundle_identifier=None,
             info_plist={'CFBundleShortVersionString': '0.0.1',
            'NSPrincipalClass': 'NSApplication',
            'LSUIElement': '1',
          	'NSHighResolutionCapable': 'True'})
