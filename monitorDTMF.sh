#!/bin/bash
rtl_fm -t raw -p 1 -g 32 -f 462.6875M -s 22050  |  multimon-ng -e -u -t raw -f auto -a DTMF - > /home/pi/monitor/DTMF.txt

