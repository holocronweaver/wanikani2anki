import os
import platform
import subprocess

def open_file_in_default_app(path):
    """Open file in default application. Cross-desktop.
    Source: https://stackoverflow.com/a/16204023/376497"""
    if platform.system() == 'Windows':
        os.startfile(path)
    elif platform.system() == 'Darwin':
        subprocess.Popen(['open', path])
    else: # Linux
        subprocess.Popen(['xdg-open', path])
