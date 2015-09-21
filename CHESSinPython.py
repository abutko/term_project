#CHESSinPython.py

import os
import subprocess

pwd = os.getcwd() # current working directory
path = os.path.join(pwd, 'load_screen.py') # filename
subprocess.Popen("python %s" % path, shell=True) # run file