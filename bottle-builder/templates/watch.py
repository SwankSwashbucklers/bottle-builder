from sys import argv, exit
from signal import signal, SIGTERM, SIGINT
from shutil import rmtree
from subprocess import Popen
from inspect import getframeinfo, currentframe
from os.path import dirname, abspath, isdir, isfile
from os import chdir, remove

def signal_term_handler(signal, frame):
    if not p is None: p.kill()
    if isfile("_all.scss"): remove("_all.scss")
    if isdir(".sass-cache"): rmtree(".sass-cache")
    print(argv[0])
    remove("watch.py") # argv[0] contains full path
    exit(0)

p = None
signal(SIGTERM, signal_term_handler)
signal(SIGINT, signal_term_handler)
chdir(dirname(abspath(getframeinfo(currentframe()).filename)))

command = "sass --watch"
for x in range(1, len(argv)):
    command += " {0}.scss:../../www/static/css/{0}.css".format(argv[x])
p = Popen(command, shell=True)
p.wait()
