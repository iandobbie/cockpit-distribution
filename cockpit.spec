#!/usr/bin/env python

# Copyright (C) 2019 David Miguel Susano Pinto <david.pinto@bioch.ox.ac.uk>
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.

# Configuration file for PyInstaller.

import pkgutil
import sys

import PyInstaller.utils.hooks


# Location where the cockpit package is, so the location of the
# cockpit repository.
cockpit_pkg_path = 'cockpit'

# We manually modify sys.path instead of using the Analysis' pathex
# argument because the PyInstaller hooks that we use to collect
# submodules and data files are called first and they also need to be
# able to find the cockpit package.
sys.path.append(cockpit_pkg_path)

# The import of cockpit.devices and cockpit.handlers modules is
# configuration dependent so they need to be added "manually".  We
# just add all cockpit modules.
hidden_imports = [m.name for m in pkgutil.walk_packages([cockpit_pkg_path])]

resources = PyInstaller.utils.hooks.collect_data_files('cockpit',
                                                       subdir='resources')

# The script is named 'cockpit_main.py' because otherwise 'import
# cockpit' will import itself rather than the cockpit package.
a = Analysis(['cockpit_main.py'],
             pathex=[cockpit_pkg_path],
             binaries=resources,
             datas=[],
             hiddenimports=hidden_imports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data)

# The executable name is named cockpit_main because if it was called
# cockpit it will conflict with the cockpit directory where the pkg
# resources will be.
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='cockpit_main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Cockpit',
               icon='cockpit/cockpit/resources/bitmaps/cockpit.ico')
