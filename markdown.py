#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import os

class MarkdownFrame(wx.Frame):
    """MarkdownFrame class, sub window."""
    def __init__(self, mainframe):
        """Create a Frame instance"""
        wx.Frame.__init__(self, None, title=_("MarkdownFrame"), size=(800, 650))
        # self.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)
        self.Centre()

        #self.main_frame = mainframe
        #self.current_index = 0

        panel = wx.Panel(self, size=self.GetSize())

        sizer = wx.BoxSizer()

        self.sizer.Add(self.appPanel, 0, wx.EXPAND)
        self.sizer.Add(wx.StaticLine(self), flag=wx.EXPAND)

        panel.SetSizer(sizer)
        panel.Layout()
        #sizer.Fit(self)
        button_close = wx.Button(self, -1, label=_("Close"))

        vbox_cmd = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd.Add(button_close, 0, wx.ALIGN_CENTER)

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_top.Add((5, 5))
        vbox_top.Add(self.text_multi_text, 1, wx.EXPAND)
        vbox_top.Add((5, 5))
        vbox_top.Add(vbox_cmd, 0, flag=wx.ALIGN_CENTER)


        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.messagetimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnMessageTimer, self.messagetimer)

    def SetMessageValue(self, text, last=False):
        if (dbmenus.global_help_enable == False):
            return
