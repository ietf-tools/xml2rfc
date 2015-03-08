# -*- mode: python -*-
a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'xml2rfc-gui.py'],
             pathex=['xml2rfc_gui', 'Z:\\work\\proj\\ietf\\deploy-gui'])
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\xml2rfc-gui', 'xml2rfc-gui.exe'),
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon='assets/xml2rfc.ico')

templates = [
    (os.path.join('templates', file), os.path.join('xml2rfc/templates', file), 'DATA') \
    for file in os.listdir('xml2rfc/templates')
]

coll = COLLECT( exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               templates,
               strip=False,
               upx=True,
               name=os.path.join('dist', 'xml2rfc-gui'))
