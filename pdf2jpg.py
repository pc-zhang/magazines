import subprocess
from os import listdir

for f in listdir('.'):
    if f.endswith('.pdf'):
        command = 'convert -resize 300x480 "{}" "{}"'.format(f + '[0]', f[:-4] + '.jpg')
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

