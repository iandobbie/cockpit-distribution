# -*- mode: python ; coding: utf-8 -*-
# Copyright (C) 2021 David Miguel Susano Pinto <david.pinto@bioch.ox.ac.uk>
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

# The import of cockpit.devices is configuration dependent and the
# import of many cockpit.gui modules happens with importlib.  We also
# may want to have other cockpit modules available only for when using
# the Python shell from cockpit.  Because of this we need to add them
# manually.
hidden_imports = [m.name for m in pkgutil.walk_packages([cockpit_pkg_path])]

resources = PyInstaller.utils.hooks.collect_data_files('cockpit',
                                                       subdir='resources')
resources.append(('cockpit_sim.depot','cockpit'))
resources.append(('merged-zaber-rgb.tif','cockpit'))

cdll = []

# The script is named 'cockpit_main.py' because otherwise 'import
# cockpit' will import itself rather than the cockpit package.


a = Analysis(['cockpit_sim.py'],
             pathex=[cockpit_pkg_path],
             binaries=cdll,
             datas=resources,
             hiddenimports=hidden_imports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='cockpit_sim',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='cockpit/cockpit/resources/bitmaps/cockpit.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='cockpit_sim')
app = BUNDLE(coll,
             name='cockpit_sim.app',
             icon='cockpit.icns',
             bundle_identifier='com.micronoxford')
