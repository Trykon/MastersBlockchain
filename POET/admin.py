import time
import subprocess

minercount = 10
s = subprocess.Popen("server.py", shell=True)
time.sleep(0.2)
for i in range(0, minercount):
    print(i)
    m = subprocess.Popen("miner.py", shell=True)
    print(i)
s.wait()
time.sleep(100)
