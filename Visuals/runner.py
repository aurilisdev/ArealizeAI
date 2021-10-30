import os
import time


for i in range(0,20):
    os.system("python3 main.py")
    time.sleep(1)
    os.system("^c")
    os.system("python3 main.py")
