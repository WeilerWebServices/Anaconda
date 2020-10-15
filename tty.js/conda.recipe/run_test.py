# 
# Note that we don't import print_function, but the conda framework will 
# import it.  This file will not run under 2.7 by hand, but it will when conda build runs
# 

import os, time 
import sys
import subprocess

home = os.path.expanduser('~')
os.chdir(home)
flag = False

try:
    print('starting server')
    p = subprocess.call('tty.js &',shell=True)
    url = "localhost:8080" 

    #wait for tty.js to come up
    time.sleep(1.5)

    c = subprocess.Popen("curl -o /dev/null --silent --head --write-out '%{http_code}\n' "+url,shell=True,stdout=subprocess.PIPE)
    status=c.communicate()[0].strip()
    print('the status: ', status)

    if status == '200':
        print('a-o-k')
        flag = True
    else:
        flag = False

finally:
    print('Cleaning up tty.js server')
    grep = subprocess.Popen("ps aux | grep tty.js",shell=True,stdout=subprocess.PIPE)
    grep = grep.communicate()[0].strip()
    for line in grep.split('\n'):
        if 'grep' in line:
            pass
        elif 'python' in line:
            pass
        else:
            pid = line.split()[1]
            print('killing: ', line)
            subprocess.call('kill -9 '+pid,shell=True)

#test failed exit!
if not flag:
    print('Failed test!')
    sys.exit(9)

