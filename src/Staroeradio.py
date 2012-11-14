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
import urllib
import threading
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import time

class StaroeRadio(dbus.service.Object):

    def __init__(self):
        DBusGMainLoop(set_as_default=True)
        self.db = dbus.SessionBus()
            
        self.ind = appindicator.Indicator("hello world client", "", appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status (appindicator.STATUS_ACTIVE)
        
        self.ind.set_icon_theme_path("home/nemo/workspace/Staroeradio/src/images")
        #self.ind.set_icon("staroeradio")
        self.ind.set_icon("radioretro5")

        self.flag = 0
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
        
        
        self.tb = gtk.TextBuffer()
        self.tb.set_text("Type text to search...")
        self.tb.connect("begin-user-action", self.on_begin_user_action)
        self.tb.connect("changed", self.on_changed)
        self.tv = gtk.TextView(self.tb)
        
        self.tv.set_border_window_size(gtk.TEXT_WINDOW_LEFT,   2)        
        self.tv.set_border_window_size(gtk.TEXT_WINDOW_RIGHT,  2)        
        self.tv.set_border_window_size(gtk.TEXT_WINDOW_TOP,    2)        
        self.tv.set_border_window_size(gtk.TEXT_WINDOW_BOTTOM, 2)
                
        self.wnd = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.wnd.set_default_size(100,20)
        self.wnd.add(self.tv)
        self.wnd.set_position(gtk.WIN_POS_CENTER)
        
        self.makeMenu()
            
    def on_next_day(self, e):
        self.tb.set_text("Type text to search...")
        self.wnd.hide()
        self.wnd.resize(100, 20)
        
        if(self.day < self.total_days-1 ):
            self.day += 1
        self.makeMenu()
    
    def on_prev_day(self, e):
        self.tb.set_text("Type text to search...")
        self.wnd.hide()
        self.wnd.resize(100, 20)
        
        if(self.day > 0 ):
            self.day -= 1
        self.makeMenu()
            
    def on_play_pause(self, e):
        self.tb.set_text("Type text to search...")
        self.wnd.hide()
        self.wnd.resize(100, 20)
        
        try:
            self.iface.PlayPause()
        except:
            pass

    def on_stop(self, e):
        self.tb.set_text("Type text to search...")
        self.wnd.hide()
        self.wnd.resize(100, 20)
        
        try:
            self.iface.Stop()
        except:
            pass

    def on_name(self, e, param):
        self.tb.set_text("Type text to search...")
        self.wnd.hide()
        self.wnd.resize(100, 20)
        
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
        
    def getPlaylistSearch(self):
        hdr = {"User-Agent": "Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405"}
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
            
    def makeMenu(self):
        self.menu = gtk.Menu()
       
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
            
        item = gtk.SeparatorMenuItem()
        self.menu.append(item)
        item.show()
        
        item_quit = gtk.MenuItem()
        item_quit.add(gtk.Label("Quit"))
        self.menu.append(item_quit)
        item_quit.show()
        
        item_quit.connect("activate", self.on_quit)

        self.ind.set_menu(self.menu)
        
    def on_quit(self, e):
        try:
            self.iface2.Quit()
        except:
            pass
        gtk.main_quit()
        
    def on_search(self, e):
        self.wnd.show_all()
        
    def on_begin_user_action(self, e):
        if(self.flag == 0):
            start = self.tb.get_start_iter()
            end   = self.tb.get_end_iter()
            self.tb.select_range(start, end)
        self.flag = 1
        
    def on_changed(self, e):
        self.text = self.tb.get_text(self.tb.get_start_iter(), self.tb.get_end_iter())
        if(len(self.text) > 0 ):
            if (self.text[len(self.text)-1] == "\n"):
                self.flag = 0
                self.getPlaylistSearch()
                self.makeMenu()
                self.tb.set_text("Type text to search...")
                self.wnd.hide()
                self.wnd.resize(100, 20)
                
        
        
sr = StaroeRadio()
gtk.gdk.threads_init()
gtk.main()
    
os._exit(0)

