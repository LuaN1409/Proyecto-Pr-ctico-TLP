# -*- mode: python -*-
# Configuración PyInstaller Ejecutable 

block_cipher = None

# Analiza los archivos fuente y dependencias
a = Analysis(['motor_runtime.py'],
             pathex=['C:\\Users\\Luan\\Documents\\GitHub\\Proyecto-Pr-ctico-TLP'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

# Empaqueta los módulos en un solo archivo
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Genera el ejecutable final
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='motor_runtime',
          debug=False,
          strip=False,
          upx=True,
          console=False)
