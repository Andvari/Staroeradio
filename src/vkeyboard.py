# -*- coding: UTF-8 -*-
'''
Created on Nov 15, 2012

@author: nemo
'''

import gtk
import os
import pango
import gobject

MULT = 4

KB_COLS = 11
KB_ROWS = 4

buttons_ru = [ "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "BACKSP",
               "й", "ц", "у", "к", "е", "н", "г", "ш", "щ", "з", "x",
               "ф", "ы", "в", "а", "п", "р", "о", "л", "д", "ж", "GO",
               "SPACE", "я", "ч", "с", "м", "и", "т", "ь", "б", "ю", "э"] 


class vkeyboard(gtk.Window):
    
    def __init__(self):
        super(vkeyboard, self).__init__()
        
        self.flag = 0
        self.text = ""
        
        pangoFont = pango.FontDescription("Tahoma 40.2")

        try:
            gobject.signal_new("z_signal", self, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
        except:
            pass

        
        self.modify_font(pangoFont)
        
        self.set_title("Search...")
        
        self.tb = gtk.TextBuffer()
        self.tb.set_text("Type text to search...")
        
        self.set_default_size(MULT*160, MULT*90)

        self.tv = gtk.TextView(self.tb)
        self.tv.modify_font(pangoFont)
        
        self.tv.set_editable(False)
        self.tv.set_border_width(3)

        self.vbox  = gtk.VBox()
        self.vbox.add(self.tv)

        self.hbox = {}
        for i in range(KB_ROWS):
            self.hbox[i] = gtk.HBox()
            for j in range(KB_COLS):
                self.button = gtk.Button(label = buttons_ru[i*KB_COLS+j])
                self.button.connect("clicked", self.on_click, i*KB_COLS+j)
                self.hbox[i].add(self.button)
            self.vbox.add(self.hbox[i])

        self.add(self.vbox)
        self.set_position(gtk.WIN_POS_CENTER)
        
        #self.show_all()

    def on_click(self, e, prm):
        if(self.flag == 0):
            self.tb.delete(self.tb.get_start_iter(), self.tb.get_end_iter())
        
        if (buttons_ru[prm] == "BACKSP"):
            start = self.tb.get_end_iter()
            end   = self.tb.get_end_iter()
            start.backward_char()
            self.tb.delete(start, end)
            
        elif (buttons_ru[prm] == "GO"):
            self.flag = 0
            self.emit("z_signal")
        else:
            if(buttons_ru[prm] == "SPACE"):
                self.tb.insert(self.tb.get_end_iter(), " ")
            else:
                self.tb.insert(self.tb.get_end_iter(), buttons_ru[prm])
                    
            self.flag = 1
            
    def get_text_to_find(self):
        self.text = self.tb.get_text(self.tb.get_start_iter(), self.tb.get_end_iter())
        return self.text
    
    def on_destroy(self, e):
        self.hide()

'''
vk = vkeyboard()

gtk.gdk.threads_init()
gtk.main()

print "Bye"
    
os._exit(0)
'''
