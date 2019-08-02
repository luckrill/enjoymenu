#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import os

class MarkdownFrame(wx.Frame):
    """MarkdownFrame class, sub window."""
    def __init__(self):
        """Create a Frame instance"""
        wx.Frame.__init__(self, None, title="MarkdownFrame", size=(1024, 800))
        # self.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)
        self.Centre()

        #self.main_frame = mainframe
        #self.current_index = 0

        panel = wx.Panel(self, size=self.GetSize())

        sizer = wx.BoxSizer()

        # self.sizer.Add(self.appPanel, 0, wx.EXPAND)
        # self.sizer.Add(wx.StaticLine(self), flag=wx.EXPAND)



        # HORIZONTAL 水平

        # for vbox_cmd1
        url_param_label = wx.StaticText(self, -1, "Param:")
        url_param_text = wx.TextCtrl(self, -1, "", size=(300, -1))
        radio_1 = wx.RadioButton(self, -1, "radio1", style=wx.RB_GROUP)
        radio_2 = wx.RadioButton(self, -1, "radio2")
        radio_3 = wx.RadioButton(self, -1, "radio3")

        vbox_cmd1 = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd1.Add(url_param_label, 0, wx.ALIGN_LEFT)
        vbox_cmd1.Add(url_param_text, 0, wx.ALIGN_LEFT)
        vbox_cmd1.Add((5, 5))
        vbox_cmd1.Add(radio_1, 0, wx.ALIGN_LEFT)
        vbox_cmd1.Add((5, 5))
        vbox_cmd1.Add(radio_2, 0, wx.ALIGN_LEFT)
        vbox_cmd1.Add((5, 5))
        vbox_cmd1.Add(radio_3, 0, wx.ALIGN_LEFT)


        # for vbox_cmd2
        url_label = wx.StaticText(self, -1, "URL:")
        url_text = wx.TextCtrl(self, -1, "", size=(450, -1))
        button_markdown = wx.Button(self, -1, label="Markdown")
        button_source = wx.Button(self, -1, label="Source")
        button_save = wx.Button(self, -1, label="Save")

        vbox_cmd2 = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd2.Add(url_label, 0, wx.ALIGN_LEFT)
        vbox_cmd2.Add(url_text, 0, wx.ALIGN_LEFT)
        vbox_cmd2.Add((5, 5))
        vbox_cmd2.Add(button_markdown, 0, wx.ALIGN_LEFT)
        vbox_cmd2.Add((5, 5))
        vbox_cmd2.Add(button_source, 0, wx.ALIGN_LEFT)
        vbox_cmd2.Add((5, 5))
        vbox_cmd2.Add(button_save, 0, wx.ALIGN_LEFT)

        # for vbox_bottom
        # button_save2 = wx.Button(self, -1, label="Save2")
        # button_close = wx.Button(self, -1, label="Close")

        # vbox_bottom = wx.BoxSizer(wx.HORIZONTAL)
        # vbox_bottom.Add(button_save2, 0, wx.ALIGN_CENTER)
        # vbox_bottom.Add(button_close, 0, wx.ALIGN_CENTER)

        # for vbox_top
        text_multi_text = wx.TextCtrl(self, -1, "", size=(300, 200), style=wx.TE_MULTILINE)
        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_top.Add(vbox_cmd1, flag=wx.ALIGN_LEFT)
        vbox_top.Add((5, 5))
        vbox_top.Add(vbox_cmd2, flag=wx.ALIGN_LEFT)
        vbox_top.Add((5, 5))
        vbox_top.Add(text_multi_text, 1, wx.EXPAND)
        #vbox_top.Add(vbox_bottom, 0, flag=wx.ALIGN_LEFT)

        panel.SetSizer(vbox_top)
        panel.Layout()
        #sizer.Fit(self)

        self.Bind(wx.EVT_CLOSE, self.OnClose)


    def OnClose(self, event):
        pass
        self.Destroy()

    def SetMessageValue(self, text, last=False):
        if (dbmenus.global_help_enable == False):
            return

class App(wx.App):
    """Application class."""
    def OnInit(self):
        self.frame = MarkdownFrame()
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True

def main():
    app = App()
    app.MainLoop()

if __name__ == '__main__':
    main()
