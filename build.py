#! /usr/bin/env python3
import os
import shutil
import subprocess
os.chdir('build')
subprocess.run('pyinstaller wanikani2anki_onedir.spec', shell=True, check=True)
# Remove extraneous files.
os.chdir('dist/wanikani2anki')
extraneous_files = [
    'libx265.so.146',
    'libfftw3.so.3',
    'libicudata.so.60',
    'libavcodec.so.57'
]
for file in extraneous_files: os.remove(file)
extraneous_dirs = [
    'gst_plugins',
    'share/icons',
    'share/themes'
]
for dir in extraneous_dirs: shutil.rmtree(dir)
# Create a compressed redistributable
os.chdir('..')
shutil.make_archive('wanikani2anki_os', 'zip', 'wanikani2anki')
