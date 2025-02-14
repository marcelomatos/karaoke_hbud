#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib, Gst

class Player():
    def __init__(self, video_widget):
        self.url = {"audio":None, "video":None}
        self.id = -1
        self.nowIn = None
        self.resume = False
        self.playing = False
        self.engines = {"audio":Gst.ElementFactory.make("playbin3"), "video":Gst.ElementFactory.make("playbin3")}
        Gst.util_set_object_arg(self.engines["video"], "flags", "video+audio+deinterlace+soft-colorbalance+buffering+enable-last-sample+native-audio")
        Gst.util_set_object_arg(self.engines["audio"], "flags", "audio+soft-volume")
        sink = Gst.ElementFactory.make("gtk4paintablesink", "sink")
        paintable = sink.get_property("paintable")
        video_sink = Gst.ElementFactory.make("glsinkbin", "video-sink")
        video_sink.set_property("sink", sink)
        self.engines["video"].set_property("video-sink", video_sink)
        video_widget.set_paintable(paintable)

class Tools():
    def __init__(self):
        self.seekBack = False
        print("Tools inited")

    def themer(self, provider, window, c, w=""):
            ca = c.replace(")", ",0.3)").replace("rgb", "rgba")
            css = """image {
                border-radius: 10px;
            }
            #_background {
                border-radius: 0px;
                filter: blur(%spx) saturate(2) brightness(0.9);
            }
            #_flap_background {
                background: @window_bg_color;
            }
            #videosink {
                background: black;
            }
            entry.search {
                outline-color: %s;
            }
            switch:checked, highlight, menuitem:hover{
                background-color: %s;
            }
            #trackbox_%s, #playlistbox_%s{
                background: %s;
                color: %s;
                border-radius: 10px;
            }
            .trackrow:hover {
                background: %s;
                border-radius: 10px;
            }
            scale slider {
                min-height: 16px;
                min-width: 16px;
            }
            scale mark indicator {
                min-height: 7px;
                color: %s;
            }
            scale marks.top {
                margin-top: 6px;
            }
            highlight {
                min-height: 16px;
            }
            #overlay_box, #hub_box {
                background-color: rgba(0,0,0,%s);
                border-radius: 10px;
            }
            #hub_menu contents, #hub_menu arrow {
                background-color: rgba(0,0,0,%s);
            }""" % (self.b,c,c,w,self.plnum,c,self.color,ca,c,self.o,self.o)
            css = css.encode()
            provider.load_from_data(css)
            GLib.idle_add(window.get_style_context().add_provider_for_display, Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            # provider.load_from_data(css, -1)
            # GLib.idle_add(window.get_style_context().add_provider_for_display, Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def get_lyric(self, title, artist, DAPI):
        DAPI.title, DAPI.artist = title, artist
        try: result = DAPI.getLyrics()
        except: result = 0
        return result

    def slideShow(self, subtitle):
        self.lenlist = len(subtitle)-1
        while not self.stopKar:
            self.line1, self.line2, self.line3, self.buffer = [], [], [], []
            self.hav1, self.hav2, self.hav3, self.where = False, False, False, -1
            for word in subtitle:
                if '#' in word.content:
                    self.buffer.append(word)
                    if not self.hav1: self.to1()
                    elif not self.hav2: self.to2()
                    else: self.to3()
                else: self.buffer.append(word)
                if self.stopKar or self.seekBack: break
                self.where += 1
            if not self.seekBack:
                self.to2()
                self.to1()
                self.line2 = []
                self.sync()
                self.stopKar = True
            else: self.seekBack = False

    def to1(self):
        if self.hav2: self.line1 = self.line2
        else:
            self.line1 = self.buffer
            self.buffer = []
        self.hav1 = True

    def to2(self):
        if self.where+1 <= self.lenlist:
            if self.hav3: self.line2 = self.line3
            else:
                self.line2 = self.buffer
                self.buffer = []
            self.hav2 = True
        else:
            if self.hav1 and not self.hav3: self.to1()
            self.line2 = self.line3
            self.line3 = []
            self.sync()

    def to3(self):
        if self.where+2 <= self.lenlist:
            if self.hav1 and self.hav3: self.to1()
            if self.hav2 and self.hav3: self.to2()
            self.line3 = self.buffer
            self.buffer, self.hav3 = [], True
        else:
            if self.hav1: self.to1()
            if self.hav2: self.to2()
            self.line3 = self.buffer
            self.buffer, self.hav3 = [], False
        self.sync()

    def sync(self):
        simpl2, simpl3 = "", ""
        if self.line2 != []:
            for z in self.line2:
                if self.stopKar or self.seekBack: break
                simpl2 += f"{z.content.replace('#', '')} "
        else: simpl2 = ""
        if self.line3 != []:
            for z in self.line3:
                if self.stopKar or self.seekBack: break
                simpl3 += f"{z.content.replace('#', '')} "
        else: simpl3 = ""
        GLib.idle_add(self.label2.set_markup, f"<span size='{int(self.size2)}'>{simpl2}</span>")
        GLib.idle_add(self.label3.set_markup, f"<span size='{int(self.size2)}'>{simpl3}</span>")
        done, tmpline, first, tl1, it = "", self.line1[:], True, self.line1, 1
        tl1.insert(0, "")
        maxit = len(tl1)-1
        for xy in tl1:
            if self.stopKar or self.seekBack: break
            if first: first = False
            else: tmpline = tmpline[1:]
            leftover = ""
            for y in tmpline:
                if self.stopKar or self.seekBack: break
                leftover += f"{y.content.replace('#', '')} "
            if done == "":
                try:
                    xy == ""
                    GLib.idle_add(self.label1.set_markup, f"<span size='{self.size}'>{leftover.strip()}</span>")
                except: GLib.idle_add(self.label1.set_markup, f"<span size='{self.size}' color='green'>{xy.content.replace('#', '')}</span><span size='{self.size}'> {leftover.strip()}</span>")
            if leftover == "" and done != "": GLib.idle_add(self.label1.set_markup, f"<span size='{self.size}' color='green'>{done.strip()} </span><span size='{self.size}' color='green'>{xy.content.replace('#', '')}</span>")
            elif done != "": GLib.idle_add(self.label1.set_markup, f"<span size='{self.size}' color='green'>{done.strip()} </span><span size='{self.size}' color='green'>{xy.content.replace('#', '')}</span><span size='{self.size}'> {leftover.strip()}</span>")
            while not self.stopKar:
                GLib.usleep(10000)
                if it > maxit:
                    if self.position >= xy.end.total_seconds()+self.offset/1000 and self.position >= 0.5: break
                else:
                    xz = tl1[it]
                    if self.position >= xz.start.total_seconds()+self.offset/1000 and self.position >= 0.5: break
                if self.seekBack: break
            it += 1
            try:
                if done == "": done += f"{xy.content.replace('#', '')}"
                else: done += f" {xy.content.replace('#', '')}"
            except: pass