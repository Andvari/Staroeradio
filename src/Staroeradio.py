#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on Oct 10, 2012

@author: nemo
'''

import os
import gtk
import urllib2, re
import httplib
import appindicator
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import time
import vkeyboard

STOPPED = 0
PLAYED  = 1
PAUSED  = 2

class StaroeRadio(dbus.service.Object):

    def __init__(self):
        DBusGMainLoop(set_as_default=True)
        self.db = dbus.SessionBus()
            
        self.state = STOPPED
            
        self.ind = appindicator.Indicator("hello world client", "", appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status (appindicator.STATUS_ACTIVE)
        
        self.ind.set_icon_theme_path("home/nemo/workspace/Staroeradio/src/images")
        self.ind.set_icon("radio_off")

        self.kb = vkeyboard.vkeyboard()
        self.kb.connect("z_signal", self.on_z_signal)

        self.day = 0
        self.dates = {}
        self.links = {}
        self.times = {}
        self.names = {}

        self.getPlaylist()
        self.total_days = len(self.links)
        while(self.total_days == 0):
            time.sleep(10)
            self.getPlaylist()
            self.total_days = len(self.links)
            pass
        
        self.makeMenu()
            
    def on_next_day(self, e):
        if(self.day < self.total_days-1 ):
            self.day += 1
        self.makeMenu()
    
    def on_prev_day(self, e):
        if(self.day > 0 ):
            self.day -= 1
        self.makeMenu()
            
    def on_play_pause(self, e):
        try:
            self.iface.PlayPause()
            if (self.state == STOPPED):
                self.ind.set_icon("radio_on")
                self.state = PLAYED
            elif (self.state == PAUSED):
                self.ind.set_icon("radio_on")
                self.state = PLAYED
            else:
                self.ind.set_icon("radio_paused")
                self.state = PAUSED
        except:
            pass

    def on_stop(self, e):
        try:
            self.iface.Stop()
        except:
            pass
        self.ind.set_icon("radio_off")
        self.state = STOPPED

    def on_name(self, e, param):
        try:
            self.iface2.Quit()
        except:
            pass
        
        os.system("cvlc --daemon --control dbus" + " http://server.audiopedia.su:8888/get_mp3_32.php?id=" + param[param.rfind('/') + 1 : ])
        time.sleep(1)
        self.db = dbus.SessionBus()
        self.db_proxy = self.db.get_object('org.mpris.MediaPlayer2.vlc', '/org/mpris/MediaPlayer2')
        self.iface = dbus.Interface(self.db_proxy, 'org.mpris.MediaPlayer2.Player')
        self.iface2 = dbus.Interface(self.db_proxy, 'org.mpris.MediaPlayer2')
        self.state = PLAYED
        self.ind.set_icon("radio_on")
        
    def getPlaylist(self):
        try:
            req = urllib2.urlopen("http://staroeradio.ru/program")
            page = req.read()

            page = page [ page.find('mp3list') : ]
            page = page [ : page.find('program/full')]

            page = page.replace('\x09', '')
            page = page.replace('\x0A', '')

            track_list = re.compile("date\">(.*?)</a><div").findall(page)

            i=0
            for item in track_list:
                date = item [ : item.find('<')]
                self.dates[i] = date
                self.links[i] = re.compile("<a href=\"(.*?)\"").findall(item)
                self.times[i] = re.compile("time\">(.*?)<").findall(item)
                self.names[i] = re.compile("mp3name\">(.*?)<").findall(item)
                i+=1
        except:
            pass
            
    def makeMenu(self):
        self.menu = gtk.Menu()
       
        textbu = gtk.TextBuffer()
        textbu.set_text("Type text to search...")
        
        item = gtk.MenuItem()
        textview = gtk.TextView(textbu)
        item.add(textview)
        self.menu.append(item)
        item.show()
       
        item = gtk.MenuItem()
        item.add(gtk.Label(self.dates[self.day]))
        self.menu.append(item)
        item.show()

        item_next_day = gtk.MenuItem()
        item_next_day.add(gtk.Label("Next day"))
        self.menu.append(item_next_day)
        item_next_day.show()
        item_next_day.connect("activate", self.on_next_day)
            
        item_prev_day = gtk.MenuItem()
        item_prev_day.add(gtk.Label("Prev day"))
        self.menu.append(item_prev_day)
        item_prev_day.show()
        item_prev_day.connect("activate", self.on_prev_day)
            
        item_search = gtk.MenuItem()
        item_search.add(gtk.Label("Search"))
        self.menu.append(item_search)
        item_search.show()
        item_search.connect("activate", self.on_search)
            
        item = gtk.SeparatorMenuItem()
        self.menu.append(item)
        item.show()
        
        item_play_pause = gtk.MenuItem()
        item_play_pause.add(gtk.Label("Play/Pause"))
        self.menu.append(item_play_pause)
        item_play_pause.show()
        item_play_pause.connect("activate", self.on_play_pause)
            
        item_stop = gtk.MenuItem()
        item_stop.add(gtk.Label("Stop"))
        self.menu.append(item_stop)
        item_stop.show()
        item_stop.connect("activate", self.on_stop)
            
        item_quit = gtk.MenuItem()
        item_quit.add(gtk.Label("Quit"))
        self.menu.append(item_quit)
        item_quit.show()
        
        item = gtk.SeparatorMenuItem()
        self.menu.append(item)
        item.show()
        
        links = self.links[self.day]
        i=0
        for name in self.names[self.day]:
            item_name = gtk.MenuItem()
            item_name.add(gtk.Label(name))
            self.menu.append(item_name)
            item_name.show()
            item_name.connect("activate", self.on_name, links[i])
            i+=1
            
        item_quit.connect("activate", self.on_quit)

        self.ind.set_menu(self.menu)
        
    def on_quit(self, e):
        try:
            self.iface2.Quit()
        except:
            pass
        gtk.main_quit()
        
    def on_search(self, e):
        self.kb.show_all()
        
    def on_z_signal(self, e):
        self.text = self.kb.get_text_to_find()
        self.kb.hide()
        
        try:
            self.text = self.text.replace("\n", "")
            conn = httplib.HTTPConnection("staroeradio.ru")
            conn.request("GET", "/search?q=" + self.text + "&_=0")
            response = conn.getresponse()

            track_list = response.read()
            conn.close()
            
            track_list = track_list.replace("<b>", "")
            track_list = track_list.replace("</b>", "")
            
            self.links[0] = re.compile("<a href=\"(.*?)\"").findall(track_list)
            self.names[0] = re.compile("mp3name\">(.*?)</div").findall(track_list)
            self.day = 0
            self.total_days = 1
        except:
            pass
        
        self.makeMenu()
        
sr = StaroeRadio()
gtk.gdk.threads_init()
gtk.main()
    
os._exit(0)

