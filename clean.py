#! /usr/bin/env python3
import shutil
dirty_dirs = [
    'build/build',
    'build/dist',
]
for dir in dirty_dirs: shutil.rmtree(dir)
