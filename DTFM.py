#!/usr/bin/python
import sources
import re
from sh import tail
import os
import subprocess
with open("/home/pi/monitor/DTFM.txt", 'r+') as f:
    f.truncate(0)
with open("/home/pi/monitor/DTFM.log", 'r+') as f:
    f.truncate(0)
#dtfmLog = open('DTFM.log', 'w')
for line in tail("-f", "/home/pi/monitor/DTFM.txt", _iter=True):
    num = line[-2]
    dtfmLog = open('DTFM.log', 'a')
    dtfmLog.writelines(num)
    dtfmLog.close