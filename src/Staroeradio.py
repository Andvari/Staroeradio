'''
Created on Oct 10, 2012

@author: nemo
'''

import os
import urllib2, re

log = open("staroeradio.log", "wb")
url = "http://staroeradio.ru/program"

print "Opening URL"
req = urllib2.urlopen(url)
print "Start reading"
page = req.read()
print "Page is read\n"

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


tcUrl       =   'rtmp://server.audiopedia.su/vod'
app         =   'vod'
flashVer    =   'LNX 11,2,202,243'
swfUrl      =   'http://staroeradio.ru/sr-player32.swf'
pageUrl     =   'http://staroeradio.ru'

for item in track_list:
    date = item [ : item.find('<')]
    dates[i] = date
    links[i] = re.compile("<a href=\"(.*?)\"").findall(item)
    times[i] = re.compile("time\">(.*?)<").findall(item)
    names[i] = re.compile("mp3name\">(.*?)<").findall(item)
    i+=1

for i in range(len(dates)):
    print dates[i]
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

            lowqualitydir      = page[page.find('<lowqualitydir>') + 15 : page.find('</lowqualitydir>')]
            dir      = page[page.find('<dir>') + 5 : page.find('</dir>')]
            name     = page[page.find('<fname>') + 7 : page.find('.mp3</fname>')]
            filename = "mp3:" + dir + "/" + name
            
            print name
            
            filename = filename.replace('"', "'")
            filename = filename.replace("'", "\'")
        
            
            cmd  = 'rtmpdump'            
            cmd += ' -r ' + tcUrl
            cmd += ' -a ' + app
            cmd += ' -f ' + flashVer
            cmd += ' -W ' + swfUrl
            cmd += ' -p ' + pageUrl
            cmd += ' -y ' + '"' + filename + '"'
            cmd += ' -q --live'
            cmd += ' | cvlc -\n'
            
            os.system(cmd)
            
            log.write(page + "\n")
        
    
 
