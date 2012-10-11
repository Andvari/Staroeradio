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

for i in range(len(dates)):
    log.write(dates[i] + "\n")
    for j in range(len(links[i])):
        url = "http://staroeradio.ru" + links[i].pop() 
        req = urllib2.urlopen(url)
        page = req.read()
        
        id_list = re.compile('value="mp3ID=(.*?)"').findall(page)
        
        for id in id_list:
            url = "http://server.audiopedia.su:8888/getmp3parms.php?mp3id=" + id 
            req = urllib2.urlopen(url)
            page = req.read()
            log.write(page + "\n\n\n\n")
        
    
 
