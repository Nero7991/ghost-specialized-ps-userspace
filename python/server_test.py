import requests
from requests.api import request
import subprocess
import os
import signal
import sys
import time
from time import sleep, perf_counter
from threading import Thread


files_strs = ["1k","2k","4k","10k","50k","100k","500k","1m","2m","4m"]
file_text_bufs = ["", "", "", "", "", "", "", "", "", ""]

x = requests.get('http://localhost:8081/file_1k.txt')


text_buf = ""
start_time = 0
duration = 20
counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 

def task(id):
    global start_time, counts, files_strs, duration, text_buf
    while(time.time() - start_time < duration):
        time1 = perf_counter()
        requestTime=time.time()
        x = requests.get('http://localhost:8081/file_' + files_strs[id%10] + '.txt')
        if(x.status_code == 200):
            file_text_bufs[id%10] += str(requestTime)+","+ files_strs[id%10] + "," + str(perf_counter() - time1) + "\n"
            counts[id%10] += 1
         


# create and start 10 threads
start_time = time.time()
threads = []
for n in range(0, 40):
    t = Thread(target=task, args=(n,))
    threads.append(t)
    t.start()

# wait for the threads to complete
for t in threads:
    t.join()

for n in range(0, 9):
    text_buf += file_text_bufs[n]
    text_buf += "total_count," + files_strs[n] + "," + str(counts[n]) + "\n"
print(text_buf)