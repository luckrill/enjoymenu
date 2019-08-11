#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need
from email.message import EmailMessage
from selenium import webdriver
import html2text
import asyncio
from pyppeteer import launch
import datetime
import os

year = datetime.datetime.now().year
month = datetime.datetime.now().month
day = datetime.datetime.now().day
# A = 65 Z=90, a = 97 z=122, chr(num), ord('chr')
# 主人名字 + 日 + a; 一天最多四十几篇，足够了。

url = ""
param = ""

class MarkdownFrame(wx.Frame):
    """Markdown Please class, sub window."""
    def __init__(self):
        """Create a Frame instance"""
        wx.Frame.__init__(self, None, title="Markdown Please", size=(900, 800), style=wx.DEFAULT_FRAME_STYLE)
        # wx.Panel.__init__(self)
        # self.Maximize(True)
        self.Centre()

        #self.main_frame = mainframe
        #self.current_index = 0

        panel = wx.Panel(self, size=self.GetSize())
        # panel = wx.Panel(self, -1)


        # for vbox_cmd1
        url_param_label = wx.StaticText(panel, -1, "Param:")
        self.url_param_text = wx.TextCtrl(panel, -1, "", size=(300, -1))

        self.button_markdown = wx.Button(panel, -1, label="Markdown")
        self.button_markdown.SetDefault()
        # self.button_markdown.SetSize(button_markdown.GetBestSize())
        # self.button_markdown.SetToolTip("This is a Hello button...")
        self.button_reset = wx.Button(panel, -1, label="Reset")
        # button_reset.SetDefault()
        button_tellme = wx.Button(panel, -1, label="TellMe")
        button_tellme.SetToolTip("TellMe Something ... Please")
        button_close = wx.Button(panel, -1, label="Close")

        vbox_cmd1 = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd1.Add(url_param_label, 0, wx.ALIGN_LEFT)
        vbox_cmd1.Add(self.url_param_text, 0, wx.ALIGN_LEFT)
        vbox_cmd1.Add((5, 5))
        vbox_cmd1.Add(self.button_markdown, 0, wx.ALIGN_LEFT)
        vbox_cmd1.Add((5, 5))
        vbox_cmd1.Add(self.button_reset, 0, wx.ALIGN_LEFT)
        vbox_cmd1.Add((5, 5))
        vbox_cmd1.Add(button_tellme, 0, wx.ALIGN_LEFT)
        vbox_cmd1.Add((5, 5))
        vbox_cmd1.Add(button_close, 0, wx.ALIGN_LEFT)

        self.Bind(wx.EVT_BUTTON, self.OnMarkdown, self.button_markdown)
        self.Bind(wx.EVT_BUTTON, self.OnReset, self.button_reset)
        self.Bind(wx.EVT_BUTTON, self.OnTellMe, button_tellme)
        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)

        # for vbox_cmd2
        url_label = wx.StaticText(panel, -1, "    URL:")
        self.url_text = wx.TextCtrl(panel, -1, url, size=(850, -1))

        vbox_cmd2 = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd2.Add(url_label, 0, wx.ALIGN_LEFT)
        vbox_cmd2.Add(self.url_text, 0, wx.ALIGN_LEFT)

        # for vbox_top
        self.text_multi_text = wx.TextCtrl(panel, -1, "", size=(300, 200), style=wx.TE_MULTILINE)

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_top.Add(vbox_cmd1, flag=wx.ALIGN_LEFT)
        vbox_top.Add((5, 5))
        vbox_top.Add(vbox_cmd2, flag=wx.ALIGN_LEFT)
        vbox_top.Add((5, 5))
        vbox_top.Add(self.text_multi_text, 1, wx.EXPAND)



        panel.SetSizer(vbox_top)
        panel.Layout()

        self.url_text.SetFocus()

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnMarkdown(self, event):
        # self.text_multi_text.SetValue("on markdown")
        url = self.url_text.GetValue()
        if url:
            result = self.html_to_md(url)
            self.text_multi_text.SetValue(result)
            self.button_reset.SetDefault()
            self.text_multi_text.SetFocus()

    def OnReset(self, event):
        self.text_multi_text.SetValue("")
        self.button_markdown.SetDefault()
        self.url_text.SetFocus()


    def OnTellMe(self, event):
        # dlg = wx.TextEntryDialog(None, "TellMe Something:", caption='TellMe Please', style=wx.TE_MULTILINE | wx.OK | wx.CANCEL | wx.CENTRE)
        dlg = wx.TextEntryDialog(self, "TellMe Something:", caption='TellMe Please', style=wx.TE_MULTILINE | wx.OK  |  wx.CANCEL  |  wx.CENTRE, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            message = dlg.GetValue()
            if message:
                print(message)
                self.send_email(message)
        dlg.Destroy()


    def OnClose(self, event):
        self.Destroy()


    def send_email(self, message):
        msg = EmailMessage()
        msg.set_content(message)

        # me == the sender's email address
        # you == the recipient's email address
        msg['Subject'] = 'Markdown tellme'
        msg['From'] = "luckrill@163.com"
        msg['To'] = "luckrill@163.com"

        # Send the message via our own SMTP server.
        s = smtplib.SMTP_SSL("smtp.163.com", 465)
        s.login("luckrill", "jiangzx123456")
        s.send_message(msg)
        s.quit()
        pass

    def html_to_md(self, url, param=None):
        driver = webdriver.PhantomJS()

        driver.get(url)
        driver.implicitly_wait(5)
        html = driver.page_source
        # driver.close()
        driver.quit()

        print(param)
        if param:
            li = param.split(" ")
            soup = BeautifulSoup(html, 'lxml')
            if len(li) > 1:
                name = li[0]
                lili = li[1].split("=")
                if len(lili) > 1:
                    attrs1 = lili[0]
                    attrs2 = lili[1].strip("\"")
                    select_html = soup.find(name, attrs={attrs1, attrs2})
                    md = html2text.html2text(str(select_html))
                    return md
            else:
                name = param
                select_html = soup.find(name)
                md = html2text.html2text(str(select_html))
                return md

        md = html2text.html2text(html)
        return md

    async def test(self, url):
        browser = await launch()
        page = await browser.newPage()
        await page.goto("https://www.readmorejoy.com")
        await page.screenshot({'path':'readmorejoy.png'})
        await browser.close()


class App(wx.App):
    """Application class."""
    def OnInit(self):
        self.frame = MarkdownFrame()
        self.frame.Show(True)
        #self.frame.Maximize(True)
        #self.SetTopWindow(self.frame)
        return True

def main():
    app = App()
    app.MainLoop()

if __name__ == '__main__':
    main()
