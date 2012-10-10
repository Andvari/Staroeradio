'''
Created on Oct 10, 2012

@author: nemo
'''

import urllib2, re

log = open("staroeradio.log", "wb")
url = "http://staroeradio.ru/program"

req = urllib2.urlopen(url)
page = req.read()

page = page [ page.find('mp3list') : ]
page = page [ : page.find('program/full')]

page = page.replace('\x09', '')
page = page.replace('\x0A', '')
log.write(page)

log = open("staroeradio2.log", "wb")

track_list = re.compile("date\">(.*?)</a><div").findall(page)

dates = {}
links = {}
times = {}
names = {}
i=0
for item in track_list:
    date = item [ : item.find('<')]
    dates[i] = date
    links[i] = re.compile("<a href=\"(.*?)\"").findall(item)
    times[i] = re.compile("time\">(.*?)<").findall(item)
    names[i] = re.compile("mp3name\">(.*?)<").findall(item)
    i+=1

i=0
for date in dates:
    log.write(str(dates[i]))
    log.write("\n")
    for link in links[i]:
        log.write(link)
        log.write("\n")
    log.write("\n")
    
    for time in times[i]:
        log.write(time)
        log.write("\n")
    log.write("\n")

    for name in names[i]:
        log.write(name)
        log.write("\n")
    log.write("\n")
        
    log.write('\n===========\n')
    i+=1

