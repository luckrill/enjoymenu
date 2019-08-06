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

# os.chdir("target dir")
# os.getcwd()

url = "https://mp.weixin.qq.com/s?src=11&timestamp=1564838047&ver=1768&signature=bgobUY*x59iFqbagdjg7f7XdxKQSsIW9irHRz1a3W9il9CFZzN5Vr9h5TeJuf4yMndRfypRCNeQ*mnF8ZoNRxizMIbYtp3zX2bnUhhv6jvo6P6imVyRg2bBmKJVB6Faz&new=1"
param = ""

class MarkdownFrame(wx.Frame):
    """Markdown Please class, sub window."""
    def __init__(self):
        """Create a Frame instance"""
        wx.Frame.__init__(self, None, title="Markdown Please", size=(1280, 800))
        #self.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)
        #self.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)
        self.Maximize(True)
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
        self.url_param_text = wx.TextCtrl(self, -1, "", size=(300, -1))
        radio_1 = wx.RadioButton(self, -1, "radio1", style=wx.RB_GROUP)
        radio_2 = wx.RadioButton(self, -1, "radio2")
        radio_3 = wx.RadioButton(self, -1, "radio3")

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio_1, radio_1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio_2, radio_2)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio_3, radio_3)

        vbox_cmd1 = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd1.Add(url_param_label, 0, wx.ALIGN_LEFT)
        vbox_cmd1.Add(self.url_param_text, 0, wx.ALIGN_LEFT)
        vbox_cmd1.Add((5, 5))
        vbox_cmd1.Add(radio_1, 0, wx.ALIGN_LEFT)
        vbox_cmd1.Add((5, 5))
        vbox_cmd1.Add(radio_2, 0, wx.ALIGN_LEFT)
        vbox_cmd1.Add((5, 5))
        vbox_cmd1.Add(radio_3, 0, wx.ALIGN_LEFT)


        # for vbox_cmd2
        url_label = wx.StaticText(self, -1, "URL:")
        self.url_text = wx.TextCtrl(self, -1, url, size=(650, -1))
        button_markdown = wx.Button(self, -1, label="Markdown")
        button_source = wx.Button(self, -1, label="Source")
        button_save = wx.Button(self, -1, label="Save")
        button_tellme = wx.Button(self, -1, label="TellMe")
        button_close = wx.Button(self, -1, label="Close")

        self.Bind(wx.EVT_BUTTON, self.OnMarkdown, button_markdown)
        self.Bind(wx.EVT_BUTTON, self.OnSource, button_source)
        self.Bind(wx.EVT_BUTTON, self.OnSave, button_save)
        self.Bind(wx.EVT_BUTTON, self.OnTellMe, button_tellme)
        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)

        vbox_cmd2 = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd2.Add(url_label, 0, wx.ALIGN_LEFT)
        vbox_cmd2.Add(self.url_text, 0, wx.ALIGN_LEFT)
        vbox_cmd2.Add((5, 5))
        vbox_cmd2.Add(button_markdown, 0, wx.ALIGN_LEFT)
        vbox_cmd2.Add((5, 5))
        vbox_cmd2.Add(button_source, 0, wx.ALIGN_LEFT)
        vbox_cmd2.Add((5, 5))
        vbox_cmd2.Add(button_save, 0, wx.ALIGN_LEFT)
        vbox_cmd2.Add((5, 5))
        vbox_cmd2.Add(button_tellme, 0, wx.ALIGN_LEFT)
        vbox_cmd2.Add((5, 5))
        vbox_cmd2.Add(button_close, 0, wx.ALIGN_LEFT)
        # for vbox_bottom
        # button_save2 = wx.Button(self, -1, label="Save2")
        # button_close = wx.Button(self, -1, label="Close")

        # vbox_bottom = wx.BoxSizer(wx.HORIZONTAL)
        # vbox_bottom.Add(button_save2, 0, wx.ALIGN_CENTER)
        # vbox_bottom.Add(button_close, 0, wx.ALIGN_CENTER)

        # for vbox_top
        self.text_multi_text = wx.TextCtrl(self, -1, "", size=(300, 200), style=wx.TE_MULTILINE)
        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_top.Add(vbox_cmd1, flag=wx.ALIGN_LEFT)
        vbox_top.Add((5, 5))
        vbox_top.Add(vbox_cmd2, flag=wx.ALIGN_LEFT)
        vbox_top.Add((5, 5))
        vbox_top.Add(self.text_multi_text, 1, wx.EXPAND)
        #vbox_top.Add(vbox_bottom, 0, flag=wx.ALIGN_LEFT)

        panel.SetSizer(vbox_top)
        panel.Layout()
        #sizer.Fit(self)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnMarkdown(self, event):
        self.text_multi_text.SetValue("on markdown")
        url = self.url_text.GetValue()
        result = self.html_to_md(url)
        self.text_multi_text.SetValue(result)

    def OnSource(self, event):
        self.text_multi_text.SetValue("on source")

    def OnRadio_1(self, event):
        self.url_param_text.SetValue("radio_1")

    def OnRadio_2(self, event):
        self.url_param_text.SetValue("radio_2")

    def OnRadio_3(self, event):
        self.url_param_text.SetValue("radio_3")

    def OnSave(self, event):
        self.text_multi_text.SetValue("on save")

        url = self.url_text.GetValue()
        asyncio.get_event_loop().run_until_complete(self.test(url))

        self.text_multi_text.SetValue("on test now")

    def OnTellMe(self, event):
        # self.text_multi_text.SetValue("on tellme")
        dlg = wx.TextEntryDialog(None, "TellMe Something:", caption='TellMe Please', style=wx.TE_MULTILINE | wx.OK | wx.CANCEL | wx.CENTRE)
        if dlg.ShowModal() == wx.ID_OK:
            message = dlg.GetValue()
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
