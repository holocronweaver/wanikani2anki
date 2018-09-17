#! /usr/bin/env python3
import os
import subprocess
os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + ':genanki/genanki'
subprocess.run('python3 app/main.py', shell=True, check=True)
