# -*- mode: python -*-

block_cipher = None


a = Analysis(['../app/main.py'],
             pathex=['./'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='wanikani2anki',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               # Tree('/home/jesse/nextcloud/projects/wanikani/wanikani2anki/app/'),
               Tree('../app/'),
               a.binaries,
               a.zipfiles,
               a.datas,
               name='wanikani2anki',
               strip=False,
               upx=True )
