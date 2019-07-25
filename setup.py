from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [], include_files = ['mdoc', 'pdoc', 'menus.ico', 'ding.mp3'])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('newmenus.py', base=base, compress = True, icon = "menus.ico"), 
    Executable('runnewmenus.py', base=base, compress = True, icon = "menus.ico"),
    Executable('newimages.py', base=base, compress = True, icon = "menus.ico"),
    Executable('update.py', base=base, compress = True)
]
# Executable('newimages.py', base=base, compress = True, icon = "newimages.ico"), Executable('update.py', base=base, compress = True)
# Executable('newimages.py', base=base,compress = True, icon = "newimages.ico")
setup(name='NewMenus',
      version = '2.0',
      description = 'A new menus program',
      author = 'Face2group.com',
      author_email = 'luckrill@163.com',	  
      options = dict(build_exe = buildOptions),
      executables = executables)
