#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import os
import sys
import subprocess
#import codecs
import shutil
import random
import zipfile
import urllib.request, urllib.error, urllib.parse
import platform
import wx.media
import webbrowser
#import winshell
import importlib
import markdown

# if platform.system() == "Windows":
#     import win32con

importlib.reload(sys)
#sys.setdefaultencoding("utf-8")

L = wx.Locale()
_ = wx.GetTranslation

CONTENT_ITEM_TAG = "@__file_content_item__@"

def check_path():
    basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
    if os.path.exists(os.path.join(basepath, "newmenus", "mdoc", "doc", "Config")):
        basepath = os.path.abspath(os.path.join(basepath, "newmenus"))

    config_file = os.path.join(basepath, "mdoc", "doc", "Config")

    try:
        open(config_file, 'a+')
    except IOError as e:
        # app_path = os.environ['APPDATA']
        app_path = os.environ['PROGRAMDATA']
        root_newmenus = app_path+os.sep+"newmenus"
        if not os.path.exists(root_newmenus):
            os.mkdir(root_newmenus)
        if not os.path.exists(root_newmenus+os.sep+"doc"):
            shutil.copytree(basepath+os.sep+"doc", root_newmenus+os.sep+"doc")
            shutil.copytree(basepath+os.sep+"locale", root_newmenus+os.sep+"locale")
        basepath = root_newmenus

    return basepath

class DBmenus():
    menus = []

    global_help_enable = False
    # global_message_enable = False
    global_timer_enable = False

    big_font = None
    sys_color = 0

    basepath = check_path()
    basepath_doc = os.path.join(basepath, "mdoc", "doc")
    config_file = os.path.join(basepath_doc, "Config")
    version_file = os.path.join(basepath_doc, "Version")
    quickmenu_filename = os.path.join(basepath_doc, "quickmenu.txt")
    text_file = os.path.join(basepath_doc, "content.txt")
    todo_file = os.path.join(basepath_doc, "todo.txt")
    famous_file = os.path.join(basepath_doc, "famous.txt")
    message_file = os.path.join(basepath_doc, "message.html")

    current = {"lang":"English", "timer_timeout": 60, "timer_enable":1, "help_enable":1, "nb":0, "text_size": 3 }


    def __init__(self):
        self.text_multi_text = None
        self.mainframe = None
        self.middlepanel = None

        self.controlDown = False
        self.continue_mode = False
        self.continue_start = -1
        self.continue_line = 0
        self.continue_col = 0

        pass
        #os.environ['APPDATA']
        # self.basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
        # self.config_file = os.path.join(self.basepath, "Config")
        # try:
        #     open(self.config_file, 'w')
        # except IOError as e:
        #     app_path = os.environ['APPDATA']
        #     shutil.copytree(apppath+os.sep+"newmenus")
        #     shutil.copytree(self.basepath+os.sep+"doc", app_path+os.sep+"newmenus")
        #     shutil.copytree(self.basepath+os.sep+"locale", app_path+os.sep+"newmenus")
        #     self.basepath = app_path

    # def CheckStartup(self):
    #     path = os.path.join(winshell.startup(), "NewMenus.lnk")
    #     if os.path.exists(path):
    #         return True
    #     else:
    #         return False

    def Startup(self):
        startup = winshell.startup()
        #print startup
        path = os.path.join(startup, "NewMenus.lnk")
        winshell.CreateShortcut (
            Path = path,
            Target = sys.executable,
            Icon = (sys.executable, 0),
            Description = "NewMenus"
        )

    def Desktop(self):
        desktop = winshell.desktop()
        #print desktop
        path = os.path.join(desktop, "NewMenus.lnk")
        winshell.CreateShortcut (
            Path = path,
            Target = sys.executable,
            Icon = (sys.executable, 0),
            Description = "NewMenus"
        )

    def ConfigLoad(self):
        """load config info into current dict from config file"""
        if not os.path.exists(dbmenus.config_file):
            return

        #import chardet
        # from chardet.universaldetector import UniversalDetector
        # print("test")
        # detector = UniversalDetector()
        # detector.reset()
        # for line in file(dbmenus.config_file, 'rb'):
        #     detector.feed(line)
        #     if detector.done: break
        # detector.close()
        # print(detector.result)

        # f = open(dbmenus.config_file, 'rb')
        # detector.feed(f)
        # print(detector.result)
        #print(dbmenus.config_file)
        fd = open(dbmenus.config_file, mode='rt', encoding="utf-8")

        while True:
            line = fd.readline()
            #print(line)
            if not line:
                break
            line = line.strip()
            if (line.startswith("#")):
                continue
            li = line.split("=")
            li = [x.strip() for x in li]
            if li[0] == "lang":
                dbmenus.current["lang"] = li[1]
            elif li[0] == "timer_timeout":
                num = int(li[1])
                if num > 0:
                    dbmenus.current["timer_timeout"] = num
                else:
                    dbmenus.current["timer_timeout"] = 60
            elif li[0] == "timer_enable":
                dbmenus.current["timer_enable"] = int(li[1])
            elif li[0] == "help_enable":
                dbmenus.current["help_enable"] = int(li[1])
            # elif li[0] == "message_enable":
            #     dbmenus.current["message_enable"] = int(li[1])
            elif li[0] == "nb":
                dbmenus.current["nb"] = int(li[1])
            elif li[0] == "text_size":
                dbmenus.current["text_size"] = int(li[1])

        fd.close()
        if dbmenus.current["help_enable"] == 1:
            dbmenus.global_help_enable = True
        else:
            dbmenus.global_help_enable = False

        # if dbmenus.current["message_enable"] == 1:
        #     dbmenus.global_message_enable = True
        # else:
        #     dbmenus.global_message_enable = False

        if dbmenus.current["timer_enable"] == 1:
            dbmenus.global_timer_enable = True
        else:
            dbmenus.global_timer_enable = False

    def ConfigSave(self):
        """save window config info to current dict and config file"""
        #print "Config Save"
        fd = open(dbmenus.config_file, 'w', encoding="utf-8")
        for key in list(dbmenus.current.keys()):
            fd.write(str(key) + " = " + str(dbmenus.current[key]) + "\n")
        fd.close()

    def quickmenu_write(self):
        fd = open(dbmenus.quickmenu_filename, 'w', encoding="utf-8")
        for li in dbmenus.menus:
            line = "::".join(ele for ele in li) + "\n"
            fd.write(line)
        fd.close()

    def get_text_total_num(self, filename):
        fd = open(filename, mode='rt', encoding="utf-8")
        item_num = 0
        while True:
            line = fd.readline()
            if not line:
                break
            if (line.find(CONTENT_ITEM_TAG) != -1):
                item_num = item_num + 1

        return item_num

    def append_text_to_file(self, filename, text):
        if (text) and len(text) > 0:
            fd = open(filename, mode='a')
            fd.write(CONTENT_ITEM_TAG+"\n")
            fd.write(text)
            fd.close()

    def get_text_by_index(self, filename, index):
        text = ""
        if (index < 1):
            return text
        # fd = codecs.open(dbmenus.famous_file, mode='r', encoding="utf-8")
        print(filename)
        fd = open(filename, mode='rt', encoding="utf-8")
        item_num = 0
        found_item = False
        while True:
            line = fd.readline()
            if not line:
                break
            if (line.find(CONTENT_ITEM_TAG) != -1):
                item_num = item_num + 1
                if (item_num == index):
                    found_item = True
                    continue
                if (found_item == True):
                    break
            else:
                if (found_item == True):
                    text = text + line

        fd.close()
        ##text = text.decode("utf-8")

        return text;

    def get_url_file(self, url):
        #dbmenus.basepath, "doc"
        #filename = os.path.basename(url)
        filename = os.path.join(dbmenus.basepath_doc, os.path.basename(url))
        try:
            u = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            # print e.fp.read()
            return False

        f = open(filename, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])

        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                # print "not buffer"
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            # print status
        f.close()
        u.close()
        return True
        # self.text_url_update.SetValue(self.url_update)

    def SetTextCtrl(self, mainframe, middlepanel, textctl):
        self.mainframe = mainframe
        self.middlepanel = middlepanel
        self.text_multi_text = textctl

    def HandleKey(self, event):
        key = event.GetKeyCode()
        #print key
        self.controlDown = event.CmdDown()
        if (key == wx.WXK_TAB):
            # tab insert 4 space
            self.text_multi_text.WriteText("    ")
            return
        elif (key == 45):
            # - :font size -
            #print self.controlDown
            if self.controlDown:
                if dbmenus.current["text_size"] > -3:
                    dbmenus.current["text_size"] -= 1
                    dbmenus.big_font.SetPointSize(dbmenus.big_font.GetPointSize() - 1)
                    #self.text_size_changed = True
                    #self.GetParent().GetParent().UpdateTextSize()
                    self.middlepanel.UpdateTextSize()
            return
        elif (key == 43 or key == 61):
            # + : font size +
            if self.controlDown:
                if dbmenus.current["text_size"] < 30:
                    dbmenus.current["text_size"] += 1
                    dbmenus.big_font.SetPointSize(dbmenus.big_font.GetPointSize() + 1)
                    #self.text_size_changed = True
                    #self.GetParent().GetParent().UpdateTextSize()
                    self.middlepanel.UpdateTextSize()
            return
        elif (key == 65):
            # "Ctrl a"
            #self.text_multi_text.SetSelection(-1, -1)
            if self.controlDown:
                curPos = self.text_multi_text.GetInsertionPoint()
                col, line = self.text_multi_text.PositionToXY(curPos)
                length = self.text_multi_text.GetLineLength(line)
                setPos = self.text_multi_text.XYToPosition(0, line)
                self.text_multi_text.SetInsertionPoint(setPos)
            return
        elif (key == 69):
            # "Ctrl e"
            if self.controlDown:
                curPos = self.text_multi_text.GetInsertionPoint()
                col, line = self.text_multi_text.PositionToXY(curPos)
                length = self.text_multi_text.GetLineLength(line)
                #print length
                setPos = self.text_multi_text.XYToPosition(length, line)
                self.text_multi_text.SetInsertionPoint(setPos)
            return
        elif (key == 72):
            # Ctrl h
            #print self.controlDown
            if self.controlDown:
                self.text_multi_text.SetSelection(-1, -1)
            return
        elif (key == 75):
            # ctrl_k delete after or current line
            if self.controlDown:
                self.KillAfterLine()
            return
        elif (key == 76):
            # Ctrl l
            if self.controlDown:
                self.SetCurrentLine()
            return
        elif (key == 84):
            # Ctrl t
            #self.GetTopLevelParent().Timer_OnOff()
            if self.controlDown:
                self.mainframe.Timer_OnOff()
            return
        elif (key == 89):
            # Ctrl y
            if self.controlDown:
                self.KillCurrentLine()
            return
        elif (key == 82):
            # Ctrl r
            if self.controlDown:
                if self.text_multi_text.CanRedo():
                    self.text_multi_text.Redo()
            return
        elif (key == 90):
            # Ctrl z
            if self.controlDown:
                if self.text_multi_text.CanUndo():
                    self.text_multi_text.Undo()
            return
        # elif (key == 314):
        #     #
        #     #self.SetNewCol(False)
        #     return
        # elif (key == 316):
        #     #
        #     #self.SetNewCol(True)
        #     return
        # elif (key == 315):
        #     # >
        #     #self.SetNewLine(False)
        #     return
        # elif (key == 317):
        #     # <
        #     #self.SetNewLine(True)
        #     return
        elif (key == 380):
            # Page up
            self.QuickSkipLine(False)
            return
        elif (key == 381):
            # Page down
            self.QuickSkipLine(True)
            return
        elif (key == 375):
            # Home
            self.text_multi_text.SetInsertionPoint(0)
            return
        elif (key == 382):
            # End
            # self.text_multi_text.SetInsertionPoint(-1)
            self.text_multi_text.SetInsertionPointEnd()
            return
        elif (key > 339) and (key < 353):
            # Ctrl F1 -- Ctrl F12
            if (self.controlDown == True):
                #self.GetParent().GetParent().KeyRunApp(key)
                self.middlepanel.KeyRunApp(key)
                return
        elif (key == 308):
            # Ctrl
            if (self.continue_mode == True):
                self.continue_start = -1
                self.continue_mode = False
                self.continue_line = 0
                self.continue_col = 0
            return
        else:
            pass

    def SetCurrentLine(self):
        curPos = self.text_multi_text.GetInsertionPoint()
        col, line = self.text_multi_text.PositionToXY(curPos)
        length = self.text_multi_text.GetLineLength(line)
        startPos = self.text_multi_text.XYToPosition(0, line)
        endPos = self.text_multi_text.XYToPosition(length, line)

        self.text_multi_text.SetSelection(startPos, endPos)
        string = self.text_multi_text.GetRange(startPos, endPos)
        # if len(string) > 0:
        #     self.ClipCopyTo(string)

    def SetNewLine(self, updown = True):
        if (self.controlDown) and (self.continue_mode == False):
            self.continue_start = self.text_multi_text.GetInsertionPoint()
            self.continue_col, self.continue_line = self.text_multi_text.PositionToXY(self.continue_start)
            self.continue_mode = True
        if (self.continue_start == -1):
            return
        maxnum = self.text_multi_text.GetNumberOfLines()
        if (updown == True):
            self.continue_line += 1
            if self.continue_line > maxnum:
                self.continue_line = maxnum
        else:
            self.continue_line -= 1
            if self.continue_line < 0:
                self.continue_line = 0
        newPos = self.text_multi_text.XYToPosition(self.continue_col, self.continue_line)
        self.text_multi_text.SetSelection(self.continue_start, newPos)
        #self.text_multi_text.SetInsertionPoint(newPos)
        # string = self.text_multi_text.GetRange(startPos, endPos)
        # if len(string) > 0:
        #     self.ClipCopyTo(string)

    def SetNewCol(self, updown = True):
        if (self.controlDown) and (self.continue_mode == False):
            self.continue_start = self.text_multi_text.GetInsertionPoint()
            self.continue_col, self.continue_line = self.text_multi_text.PositionToXY(self.continue_start)
            self.continue_mode = True
        if (self.continue_start == -1):
            return
        length = self.text_multi_text.GetLineLength(self.continue_line)
        if (updown == True):
            self.continue_col += 1
            if self.continue_col > length:
                self.continue_col = length
        else:
            self.continue_col -= 1
            if self.continue_col < 0:
                self.continue_col = 0
        newPos = self.text_multi_text.XYToPosition(self.continue_col, self.continue_line)
        self.text_multi_text.SetSelection(self.continue_start, newPos)

    def QuickSkipLine(self, updown=True):
        curPos = self.text_multi_text.GetInsertionPoint()
        col, line = self.text_multi_text.PositionToXY(curPos)
        length = self.text_multi_text.GetLineLength(line)
        maxnum = self.text_multi_text.GetNumberOfLines()
        newline = line
        # Don't know have to get page line, so use 8 line for page up/down
        if (updown == True):
            newline += 8
            if newline > maxnum:
                newline = maxnum
        else:
            newline -= 8
            if newline < 0:
                newline = 0
        newPos = self.text_multi_text.XYToPosition(col, newline)
        self.text_multi_text.SetInsertionPoint(newPos)

    def KillAfterLine(self):
        curPos = self.text_multi_text.GetInsertionPoint()
        col, line = self.text_multi_text.PositionToXY(curPos)
        length = self.text_multi_text.GetLineLength(line)
        endPos = self.text_multi_text.XYToPosition(length, line)

        string = self.text_multi_text.GetRange(curPos, endPos)
        if len(string) > 0:
            self.ClipCopyTo(string)

        if col == 0 and length == 0:
            self.text_multi_text.Remove(curPos, endPos+1)
        else:
            self.text_multi_text.Remove(curPos, endPos)

    def KillCurrentLine(self):
        curPos = self.text_multi_text.GetInsertionPoint()
        col, line = self.text_multi_text.PositionToXY(curPos)
        length = self.text_multi_text.GetLineLength(line)
        startPos = self.text_multi_text.XYToPosition(0, line)
        endPos = self.text_multi_text.XYToPosition(length, line)

        string = self.text_multi_text.GetRange(startPos, endPos).strip()
        len_string = len(string)
        if len_string > 0:
            self.ClipCopyTo(string)

        if len_string == 0:
            self.text_multi_text.Remove(startPos, endPos+1)
            self.text_multi_text.SetInsertionPoint(curPos+1)
        else:
            self.text_multi_text.Remove(startPos, endPos)
            self.text_multi_text.SetInsertionPoint(startPos)

    def ClipCopyTo(self, string):
        if not wx.TheClipboard.IsOpened():  # may crash, otherwiseWR.LBJTNJJKL
            data = wx.TextDataObject(string)
            wx.TheClipboard.Open()
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()
            #self.GetTopLevelParent().RSetMessageValue(_("Copy to ClipCopy"))
            self.mainframe.SetMessageValue(_("Copy to ClipCopy"))

    def ClipCopyGetData(self):
        if not wx.TheClipboard.IsOpened():  # may crash, otherwise
            data = wx.TextDataObject()
            wx.TheClipboard.Open()
            wx.TheClipboard.GetData(data)
            text = data.GetText()
            wx.TheClipboard.Close()
            return text


class AppPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.number_of_command = 0
        self.subs = []
        self.addApp()

    def addApp(self):
        for app in self.subs:
            app.Destroy()
        self.subs = []

        self.sizer = wx.GridSizer(cols=8, hgap=2, vgap=10)

        self.quickmenu_read()
        for li in dbmenus.menus:
            self.number_of_command += 1
            ##name = li[0].decode("utf-8")
            name = li[0]
            button_cmd = wx.Button(self, label=name, name=name, size=(90 , 30))
            self.subs.append(button_cmd)
            button_cmd.name = name
            self.sizer.Add(button_cmd, 0, wx.ALIGN_CENTER)
            button_cmd.Bind(wx.EVT_BUTTON, self.OnCommand)

        # add Markdown
        button_markdown = wx.Button(self, label="Markdown", size=(90 , 30))
        self.subs.append(button_markdown)
        self.sizer.Add(button_markdown, 0, wx.ALIGN_CENTER)
        button_cmd.Bind(wx.EVT_BUTTON, self.OnMarkdown)

        #self.Refresh()
        self.SetSizer(self.sizer)
        self.Layout()

    def OnMarkdown(self, event):
        pass

    def OnCommand(self, event):
        name = event.GetEventObject().name
        for li in dbmenus.menus:
            if name == li[0]:
                cmd = "".join(li[1:])
                if cmd == "newimages.exe":
                    li[1] = os.path.join(dbmenus.basepath, cmd)
                    cmd = "".join(li[1:])
                    dbmenus.quickmenu_write()

                #process = subprocess.Popen(cmd.encode("gbk"), shell=True)
                process = subprocess.Popen(cmd, shell=True)
                self.GetTopLevelParent().SetMessageValue(_("Start App: ") + cmd)

                # process = subprocess.Popen(cmd.encode("gbk"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # (stdout, stderr) = process.communicate()
                # if stderr and (cmd == "newimages.exe"):
                #     li[1] = os.path.join(dbmenus.basepath, cmd)
                #     dbmenus.quickmenu_write()
                #     cmd = "".join(li[1:])
                #     process = subprocess.Popen(cmd.encode("gbk"), shell=True)

                #print stdoutput.decode("gbk")
                #print erroutput.decode("gbk")


        # self.GetTopLevelParent().middlePanel.MultiTextSetFocus()

    def quickmenu_read(self):
        if os.path.isfile(dbmenus.quickmenu_filename):
            # fd = open(dbmenus.quickmenu_filename, 'r')
            fd = open(dbmenus.quickmenu_filename, mode='r', encoding="utf-8")

            del dbmenus.menus[:]
            while True:
                line = fd.readline().strip()
                if not line:
                    break
                li = line.split("::")
                li = [str.strip() for str in li]
                if line[0] != '#':
                    ##li[0] = li[0].decode("utf-8")
                    ##li[1] = li[1].decode("utf-8")
                    # print li
                    dbmenus.menus.append(li)
            fd.close()

    def AddNewApp(self, string):
        # parse string
        filename = os.path.basename(string)
        li = filename.split('.')
        name = li[0]
        li = [name, string]

        # add to menudb
        dbmenus.menus.append(li)

        # add to UI
        self.number_of_command += 1
        button_cmd = wx.Button(self, label=name, name=name, size=(100, -1))
        self.subs.append(button_cmd)
        button_cmd.name = name
        self.sizer.Add(button_cmd, 0, wx.ALIGN_CENTER)
        button_cmd.Bind(wx.EVT_BUTTON, self.OnCommand)

        self.SetSizer(self.sizer)
        self.Layout()
        self.GetTopLevelParent().Layout()

        # add to file
        line = "::".join(ele for ele in li) + "\n"
        fd = open(dbmenus.quickmenu_filename, 'a')
        fd.write(line)
        fd.close()

class TextPage(wx.Panel):
    """this software auto update"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.text_multi_text = wx.TextCtrl(self, -1, "", size=(700, 500), style=wx.TE_MULTILINE)
        self.text_multi_text.SetFont(dbmenus.big_font)
        self.text_multi_text.SetBackgroundColour(dbmenus.sys_color)
        #self.text_multi_text.SetForegroundColour(wx.WHITE)
        #self.text_multi_text.SetBackgroundColour("DARK GREY")

        button_close = wx.Button(self, -1, label=_("Close"))
        button_save = wx.Button(self, -1, label=_("Save"))

        vbox_cmd = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd.Add(button_save, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((5, 5))
        vbox_cmd.Add(button_close, 0, wx.ALIGN_CENTER)



        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_top.Add((5, 5))
        vbox_top.Add(self.text_multi_text, 1, wx.EXPAND)
        vbox_top.Add((5, 5))
        vbox_top.Add(vbox_cmd, 0, flag=wx.ALIGN_CENTER)

        self.SetSizer(vbox_top)
        self.Layout()
        #vbox_top.Fit(self)

        #dbmenus.SetTextCtrl(self.text_multi_text)

        #print "text init and settextctrl"

        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)
        self.Bind(wx.EVT_BUTTON, self.OnSave, button_save)
        #self.text_multi_text.Bind(wx.EVT_CHAR, self.OnChar)
        self.text_multi_text.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        # mouse, win leftup have bug
        # self.text_multi_text.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        # self.text_multi_text.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.text_multi_text.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseLeftDClick)

        if os.path.exists(dbmenus.text_file):
            self.text_multi_text.LoadFile(dbmenus.text_file)
            # fd = codecs.open(dbmenus.text_file, mode='r', encoding="utf-8")
            # content = fd.read()
            # self.text_multi_text.SetValue(content)
            # fd.close()
            # del content

    def OnKeyUp(self, event):
        # onkeyup work fine
        #print "onkeyup"
        dbmenus.HandleKey(event)
        event.Skip()

    def OnMouseLeftDown(self, event):
        #print "mouse left down"
        pass

    def OnMouseLeftUp(self, event):
        #print "mouse left up"
        pass
        # string = self.text_multi_text.GetStringSelection()
        # if len(string) > 0:
        #     self.ClipCopyTo(string)

    def OnMouseLeftDClick(self, event):
        self.SetCurrentLine()
        # string = self.text_multi_text.GetStringSelection()
        # if len(string) > 0:
        #     self.ClipCopyTo(string)

    def SetCurrentLine(self):
        curPos = self.text_multi_text.GetInsertionPoint()
        col, line = self.text_multi_text.PositionToXY(curPos)
        length = self.text_multi_text.GetLineLength(line)
        startPos = self.text_multi_text.XYToPosition(0, line)
        endPos = self.text_multi_text.XYToPosition(length, line)

        self.text_multi_text.SetSelection(startPos, endPos)

    def OnSave(self, event):
        self.text_multi_text.SaveFile(self.text_file)

    def OnClose(self, event):
        self.GetTopLevelParent().OnClose(event)
        # self.GetTopLevelParent().SaveContent()
        # self.GetParent().GetParent().SaveContent()
        # self.text_multi_text.SaveFile(self.text_file)

class TodoPage(wx.Panel):
    """this software auto update"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        #self.controlDown = False

        self.todo_list = []
        self.mark = ','
        # self.SetBackgroundColour(dbmenus.sys_color)

        self.text_multi_text = wx.TextCtrl(self, -1, "", size=(700, 500), style=wx.TE_MULTILINE)
        self.text_multi_text.SetFont(dbmenus.big_font)
        self.text_multi_text.SetBackgroundColour(dbmenus.sys_color)
        button_sort = wx.Button(self, -1, label=_("Sort"))
        button_close = wx.Button(self, -1, label=_("Close"))

        vbox_cmd = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd.Add(button_sort, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((5, 5))
        vbox_cmd.Add(button_close, 0, wx.ALIGN_CENTER)

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_top.Add((5, 5))
        vbox_top.Add(self.text_multi_text, 1, wx.EXPAND) #, 0, wx.ALIGN_CENTER)
        vbox_top.Add((5, 5))
        vbox_top.Add(vbox_cmd, 0, flag=wx.ALIGN_CENTER)

        self.SetSizer(vbox_top)
        self.Layout()
        #vbox_top.Fit(self)

        #dbmenus.SetTextCtrl(self.text_multi_text)
        #dbmenus.SetTextCtrl(self.GetTopLevelParent(), self.GetParent().GetParent(), self.text_multi_text)
        #print "todo init and settextctrl"

        self.Bind(wx.EVT_BUTTON, self.OnSort, button_sort)
        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)
        self.text_multi_text.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        #self.text_multi_text.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        #self.text_multi_text.Bind(wx.EVT_CHAR, self.OnChar)
        # win leftup have bug
        # self.text_multi_text.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.text_multi_text.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseLeftDClick)

        if os.path.exists(dbmenus.todo_file):
            self.text_multi_text.LoadFile(dbmenus.todo_file)
            # fd = codecs.open(dbmenus.todo_file, mode='r', encoding="utf-8")
            # content = fd.read()
            # self.text_multi_text.SetValue(content)
            # fd.close()
            # del content

    def OnSort(self, event):
        self.text_multi_text.SetFocus()
        if self.text_multi_text.IsEmpty():
            return

        totals = self.text_multi_text.GetNumberOfLines()
        del self.todo_list[:]
        for i in range(totals):
            string = self.text_multi_text.GetLineText(i).strip()
            if string and len(string) > 0:
                num, text = self.parse_line(string)
                if len(text) > 0:
                    self.todo_list.append([num, text])

        self.todo_list.sort(key=lambda x:x[0])
        self.text_multi_text.Clear()
        for li in self.todo_list:
            line = str(li[0]) + self.mark + ' ' + li[1] + "\n"
            self.text_multi_text.AppendText(line)

        self.GetTopLevelParent().SetMessageValue(_("Todo list sorted"))

    def parse_line(self, string):
        index = string.find(' ')
        num = 0
        text = ""
        #print ("len(string): %s, index: %d"% (len(string), index))
        if (index > 0):
            num_string = string[:index].strip()
            text = string[index:].strip()
            if len(num_string) < 1:
                return
            if (num_string[0] == '-' and num_string[1:] or num_string).isdigit():
                num = int(num_string)
            else:
                self.mark = num_string[-1]
                num_string = num_string[:-1]
                if (num_string[0] == '-' and num_string[1:] or num_string).isdigit():
                    num = int(num_string)
                else:
                    self.mark = ','
                    return num, string

        return num, text

    def OnMouseLeftUp(self, event):
        pass
        # string = self.text_multi_text.GetStringSelection()
        # if len(string) > 0:
        #     self.ClipCopyTo(string)

    def OnMouseLeftDClick(self, event):
        self.SetCurrentLine()
        string = self.text_multi_text.GetStringSelection()
        # if len(string) > 0:
        #     self.ClipCopyTo(string)

    def OnClose(self, event):
        self.GetTopLevelParent().OnClose(event)
        # self.GetParent().GetParent().SaveContent()
        # self.text_multi_text.SaveFile(self.todo_file)

    def OnKeyUp(self, event):
        # key = event.GetKeyCode()
        # PageUp 366; PageDown 367
        # (27, 32, 314, 315, 316, 317)
        dbmenus.HandleKey(event)
        event.Skip()

class FamousPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.total_item = 0
        # self.SetBackgroundColour(dbmenus.sys_color)
        self.continue_mode = False
        self.continue_start = -1
        self.continue_line = 0
        self.continue_col = 0

        self.text_multi_text = wx.TextCtrl(self, -1, "", size=(700, 500), style=wx.TE_MULTILINE)
        self.text_multi_text.SetFont(dbmenus.big_font)
        self.text_multi_text.SetBackgroundColour(dbmenus.sys_color)
        button_new = wx.Button(self, -1, label=_("Another"))
        button_close = wx.Button(self, -1, label=_("Close"))

        vbox_cmd = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd.Add(button_new, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((5, 5))
        vbox_cmd.Add(button_close, 0, wx.ALIGN_CENTER)

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_top.Add((5, 5))
        vbox_top.Add(self.text_multi_text, 1, wx.EXPAND) #, 0, wx.ALIGN_CENTER)
        vbox_top.Add((5, 5))
        vbox_top.Add(vbox_cmd, 0, flag=wx.ALIGN_CENTER)

        self.SetSizer(vbox_top)
        self.Layout()
        #vbox_top.Fit(self)

        #dbmenus.SetTextCtrl(self.GetTopLevelParent(), self.GetParent().GetParent(), self.text_multi_text)
        #print "famous init and settextctrl"

        self.Bind(wx.EVT_BUTTON, self.OnNew, button_new)
        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)
        #self.text_multi_text.Bind(wx.EVT_CHAR, self.OnChar)
        self.text_multi_text.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        #self.text_multi_text.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        # self.text_multi_text.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.text_multi_text.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseLeftDClick)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        if os.path.exists(dbmenus.famous_file):
            self.parse_famous_file_header()
            self.GetFamous()

    def OnNew(self, event):
        self.text_multi_text.SetFocus()
        self.GetFamous()

    def GetFamous(self):
        if self.total_item == 0:
            return

        item_id = random.randint(1, self.total_item)
        value = dbmenus.get_text_by_index(dbmenus.famous_file, item_id)
        self.text_multi_text.SetValue(value)
        pass

    def parse_famous_file_header(self):
        fd = open(dbmenus.famous_file, 'r',encoding='utf-8')
        found_header = False
        num = 0
        while True:
            line = fd.readline()
            if not line:
                break
            line = line.strip()
            if (line.startswith("index")):
                li = line.split(":")
                if li[1].strip().isdigit():
                    val = int(li[1])
                    self.total_item = val
            elif (line.strip().startswith("#")):
                continue
            num = num + 1
            if num > 100:
                break
        fd.close()

    # def get_text_by_index(self, index):
    #     famous_text = ""
    #     if (index < 1):
    #         return famous_text
    #     fd = open(dbmenus.famous_file, mode='r')
    #     item_num = 0
    #     found_item = False
    #     while True:
    #         line = fd.readline()
    #         if not line:
    #             break
    #         if (line.find(CONTENT_ITEM_TAG) != 1):
    #             item_num = item_num + 1
    #             if (item_num == index):
    #                 found_item = True
    #                 continue
    #             if (found_item == True):
    #                 break
    #         else:
    #             if (found_item == True):
    #                 famous_text = famous_text + line

    #     famous_text = famous_text.decode("utf-8")
    #     return famous_text;

    def OnMouseLeftUp(self, event):
        pass

    def OnMouseLeftDClick(self, event):
        pass
        # self.SetCurrentLine()

    def OnClose(self, event):
        self.GetTopLevelParent().OnClose(event)
        # self.GetParent().GetParent().SaveContent()
        # self.text_multi_text.SaveFile(self.famous_file)

    def OnKeyUp(self, event):
        #dbmenus.HandleKey(event)
        key = event.GetKeyCode()
        #print key
        self.controlDown = event.CmdDown()
        if (key == 45):
            # - :font size -
            if self.controlDown:
                if dbmenus.current["text_size"] > -3:
                    dbmenus.current["text_size"] -= 1
                    dbmenus.big_font.SetPointSize(dbmenus.big_font.GetPointSize() - 1)
                    #self.text_size_changed = True
                    self.GetParent().GetParent().UpdateTextSize()
            return
        elif (key == 43 or key == 61):
            # + : font size +
            if self.controlDown:
                if dbmenus.current["text_size"] < 30:
                    dbmenus.current["text_size"] += 1
                    dbmenus.big_font.SetPointSize(dbmenus.big_font.GetPointSize() + 1)
                    #self.text_size_changed = True
                    self.GetParent().GetParent().UpdateTextSize()
            return
        elif (key == 84):
            # Ctrl t
            #self.GetTopLevelParent().Timer_OnOff()
            if self.controlDown:
                self.GetTopLevelParent().Timer_OnOff()
            return
        elif (key == 380):
            # Page up
            self.OnNew(event)
            return
        elif (key == 381):
            # Page down
            self.OnNew(event)
            return
        elif (key == 314) or (key == 315):
            if self.controlDown:
                self.OnNew(event)
            return
        elif (key == 316) or (key == 317):
            if self.controlDown:
                self.OnNew(event)
            return
        else:
            pass

        event.Skip()

class MessagePage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.total_item = 0
        self.total_index = 0
        self.list_saved = []
        # self.SetBackgroundColour(dbmenus.sys_color)
        # →←
        #self.text_multi_text = wx.TextCtrl(self, -1, "", size=(700, 500), style=wx.TE_MULTILINE|wx.TE_RICH2|wx.TE_AUTO_URL)
        self.text_multi_text = wx.TextCtrl(self, -1, "", size=(700, 500), style=wx.TE_MULTILINE)
        self.text_multi_text.SetFont(dbmenus.big_font)
        self.text_multi_text.SetBackgroundColour(dbmenus.sys_color)
        self.label_num = wx.StaticText(self, -1, "")
        button_update = wx.Button(self, -1, label="↓↓", size=(40, -1))
        button_first = wx.Button(self, -1, label="|＜", size=(40, -1))
        button_last = wx.Button(self, -1, label="＞|", size=(40, -1))
        button_up = wx.Button(self, -1, label="＜", size=(40, -1))
        button_next = wx.Button(self, -1, label="＞", size=(40, -1))
        button_save = wx.Button(self, -1, label=_("Save"))
        button_share = wx.Button(self, -1, label=_("Share"))
        button_close = wx.Button(self, -1, label=_("Close"))

        vbox_cmd = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd.Add(self.label_num, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((15, 5))
        vbox_cmd.Add(button_update, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((5, 5))
        vbox_cmd.Add(button_first, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((5, 5))
        vbox_cmd.Add(button_up, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((5, 5))
        vbox_cmd.Add(button_next, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((5, 5))
        vbox_cmd.Add(button_last, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((5, 5))
        vbox_cmd.Add(button_save, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((5, 5))
        vbox_cmd.Add(button_share, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((5, 5))
        vbox_cmd.Add(button_close, 0, wx.ALIGN_CENTER)

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_top.Add((5, 5))
        vbox_top.Add(self.text_multi_text, 1, wx.EXPAND) #, 0, wx.ALIGN_CENTER)
        vbox_top.Add((5, 5))
        vbox_top.Add(vbox_cmd, 0, flag=wx.ALIGN_CENTER)

        self.SetSizer(vbox_top)
        self.Layout()

        #print "message init and settextctrl"

        self.Bind(wx.EVT_BUTTON, self.OnUp, button_up)
        self.Bind(wx.EVT_BUTTON, self.OnNext, button_next)
        self.Bind(wx.EVT_BUTTON, self.OnFirst, button_first)
        self.Bind(wx.EVT_BUTTON, self.OnLast, button_last)
        self.Bind(wx.EVT_BUTTON, self.OnUpdate, button_update)
        self.Bind(wx.EVT_BUTTON, self.OnSave, button_save)
        self.Bind(wx.EVT_BUTTON, self.OnShare, button_share)
        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)
        #self.text_multi_text.Bind(wx.EVT_TEXT_URL, self.OnClickUrl)
        self.text_multi_text.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        # self.text_multi_text.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        #self.text_multi_text.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseLeftDClick)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        if os.path.exists(dbmenus.message_file):
            self.total_item = dbmenus.get_text_total_num(dbmenus.message_file)
            if self.total_item > 0:
                self.total_index = 1
                self.UpdateNumDisplay()
                value = dbmenus.get_text_by_index(dbmenus.message_file, self.total_index)
                self.text_multi_text.SetValue(value)

    def OnClickUrl(self, event):
        #print event.GetString()
        pass

    def UpdateNumDisplay(self):
        self.label_num.SetLabel(str(self.total_index) + "/" + str(self.total_item))

    def OnFirst(self, event):
        self.total_index = 1
        self.UpdateNumDisplay()
        value = dbmenus.get_text_by_index(dbmenus.message_file, self.total_index)
        self.text_multi_text.SetValue(value)

    def OnLast(self, event):
        self.total_index = self.total_item
        self.UpdateNumDisplay()
        value = dbmenus.get_text_by_index(dbmenus.message_file, self.total_index)
        self.text_multi_text.SetValue(value)

    def OnUp(self, event):
        self.text_multi_text.SetFocus()
        if (self.total_index > 1):
            self.total_index -= 1
            self.UpdateNumDisplay()
            value = dbmenus.get_text_by_index(dbmenus.message_file, self.total_index)
            self.text_multi_text.SetValue(value)

    def OnNext(self, event):
        self.text_multi_text.SetFocus()
        if (self.total_index < self.total_item):
            self.total_index += 1
            self.UpdateNumDisplay()
            value = dbmenus.get_text_by_index(dbmenus.message_file, self.total_index)
            self.text_multi_text.SetValue(value)

    def OnUpdate(self, event):
        url = "http://www.facegroup.cn/pub/message.html"
        if dbmenus.get_url_file(url):
            self.GetTopLevelParent().SetMessageValue(_("Sync message succeed."))
            self.total_item = dbmenus.get_text_total_num(dbmenus.message_file)
            if self.total_item > 0:
                self.total_index = 1
                self.UpdateNumDisplay()
                value = dbmenus.get_text_by_index(dbmenus.message_file, 1)
                self.text_multi_text.SetValue(value)

    def OnSave(self, event):
        if self.total_index not in self.list_saved:
            value = dbmenus.get_text_by_index(dbmenus.message_file, self.total_index)
            dbmenus.append_text_to_file(dbmenus.famous_file, value)
            self.list_saved.append(self.total_index)
        else:
            self.GetTopLevelParent().SetMessageValue(_("Have saved this item"))

    def OnShare(self, event):
        url = "http://share.facegroup.cn/newmenusshare"
        webbrowser.open(url)

    def OnMouseLeftUp(self, event):
        pass

    def OnMouseLeftDClick(self, event):
        pass
        # self.SetCurrentLine()

    def OnClose(self, event):
        self.GetTopLevelParent().OnClose(event)
        # self.GetParent().GetParent().SaveContent()
        # self.text_multi_text.SaveFile(self.famous_file)

    def OnKeyUp(self, event):
        #dbmenus.HandleKey(event)
        key = event.GetKeyCode()
        #print key
        self.controlDown = event.CmdDown()
        if (key == 45):
            # - :font size -
            if self.controlDown:
                if dbmenus.current["text_size"] > -3:
                    dbmenus.current["text_size"] -= 1
                    dbmenus.big_font.SetPointSize(dbmenus.big_font.GetPointSize() - 1)
                    #self.text_size_changed = True
                    self.GetParent().GetParent().UpdateTextSize()
            return
        elif (key == 43 or key == 61):
            # + : font size +
            if self.controlDown:
                if dbmenus.current["text_size"] < 30:
                    dbmenus.current["text_size"] += 1
                    dbmenus.big_font.SetPointSize(dbmenus.big_font.GetPointSize() + 1)
                    #self.text_size_changed = True
                    self.GetParent().GetParent().UpdateTextSize()
            return
        elif (key == 84):
            # Ctrl t
            #self.GetTopLevelParent().Timer_OnOff()
            if self.controlDown:
                self.GetTopLevelParent().Timer_OnOff()
            return
        elif (key == 380):
            # Page up
            self.OnUp(event)
            return
        elif (key == 381):
            # Page down
            self.OnNext(event)
            return
        elif (key == 375):
            # Home
            self.OnFirst(event)
            return
        elif (key == 382):
            # End
            self.OnLast(event)
            return
        elif (key == 314) or (key == 315):
            if self.controlDown:
                self.OnUp(event)
            return
        elif (key == 316) or (key == 317):
            if self.controlDown:
                self.OnNext(event)
            return

        else:
            pass

        event.Skip()

class MiddlePanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.shutdown_timeout = 0
        self.shutdown_or_restart = True
        self.autokey_state = False
        self.shutdown_state = False
        self.system_setup_frame = None
        # if not os.path.exists("doc"):
        #     os.mkdir("doc")

        if dbmenus.sys_color == 0:
            dbmenus.sys_color = self.GetBackgroundColour()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(10*60*1000) # 10 minutes

        # ‖ 〉
        self.timer_state = wx.StaticText(self, -1, "〉 ")
        button_shutdown = wx.Button(self, label=_("Shutdown"), size=(-1, 30))
        button_restart = wx.Button(self, label=_("Restart"), size=(-1, 30))
        button_lock = wx.Button(self, label=_("Lock"), size=(-1, 30))
        self.text_shutdown_time = wx.TextCtrl(self, -1, "0", size=(50, 30))
        label_units = wx.StaticText(self, -1, "m/h")
        button_setup = wx.Button(self, label=_("Setup"), size=(-1, 30))

        vbox_cmd = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd.Add(self.timer_state, 0, flag=wx.ALIGN_CENTER)
        vbox_cmd.Add(button_shutdown, 0, flag=wx.ALIGN_CENTER)
        vbox_cmd.Add((10, 10))
        vbox_cmd.Add(button_restart, 0, flag=wx.ALIGN_CENTER)
        vbox_cmd.Add((10, 10))
        vbox_cmd.Add(button_lock, 0, flag=wx.ALIGN_CENTER)
        vbox_cmd.Add((10, 10))
        vbox_cmd.Add(self.text_shutdown_time, 0, flag=wx.ALIGN_RIGHT)
        vbox_cmd.Add(label_units, 0, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER)
        vbox_cmd.Add((10, 10))
        vbox_cmd.Add(button_setup, 0, flag=wx.ALIGN_CENTER)
        vbox_cmd.Add((10, 10))

        self.nb = wx.Notebook(self)
        self.text_page = TextPage(self.nb)
        self.todo_page = TodoPage(self.nb)
        self.famous_page = FamousPage(self.nb)
        self.message_page = MessagePage(self.nb)

        self.nb.SetPadding((25,-1))

        self.nb.AddPage(self.text_page, "Note")
        self.nb.AddPage(self.todo_page, "Todo")
        self.nb.AddPage(self.famous_page, "Famous")
        self.nb.AddPage(self.message_page, "Message")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(vbox_cmd, 0, flag=wx.ALIGN_RIGHT)
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Layout()

        #self.nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnChanged)
        self.nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnChanged)
        self.Bind(wx.EVT_BUTTON, self.OnShutdown, button_shutdown)
        self.Bind(wx.EVT_BUTTON, self.OnRestart, button_restart)
        self.Bind(wx.EVT_BUTTON, self.OnLock, button_lock)
        self.Bind(wx.EVT_BUTTON, self.OnSetup, button_setup)

        if dbmenus.global_timer_enable:
            self.timer_state.SetLabel("〉 ")
        else:
            self.timer_state.SetLabel("‖ ")

        index = dbmenus.current["nb"]
        self.nb.SetSelection(index)
        #dbmenus.SetTextCtrl(self.GetTopLevelParent(), self.GetParent().GetParent(), self.text_multi_text)
        if index == 0:
            dbmenus.SetTextCtrl(self.GetTopLevelParent(), self, self.text_page.text_multi_text)
        elif index == 1:
            dbmenus.SetTextCtrl(self.GetTopLevelParent(), self, self.todo_page.text_multi_text)
        # elif index == 2:
        #     dbmenus.SetTextCtrl(self.GetTopLevelParent(), self, self.famous_page.text_multi_text)
        # elif index == 3:
        #     dbmenus.SetTextCtrl(self.GetTopLevelParent(), self, self.message_page.text_multi_text)

    # def File_Content_Read_Write(filename, string = "", state = True):
    #     if state == True:
    #         fd = codecs.open(filename, mode='r', encoding="utf-8")
    #         content = fd.readlines()
    #         return content
    #     if state == False:
    #         fd = open(filename, 'w')
    #         fd.write(string)
    #         fd.close()

    def OnTimer(self, event):
        if dbmenus.global_timer_enable:
            self.timer.Stop()
            self.SaveContent()
            self.timer.Start(10*60*1000)

    def UpdateTextSize(self):
        self.text_page.text_multi_text.SetFont(dbmenus.big_font)
        self.todo_page.text_multi_text.SetFont(dbmenus.big_font)
        self.famous_page.text_multi_text.SetFont(dbmenus.big_font)
        self.message_page.text_multi_text.SetFont(dbmenus.big_font)

    def MultiTextSetFocus(self):
        index = self.nb.GetSelection()
        if index == 0:
            self.text_page.text_multi_text.SetFocus()
        elif index == 1:
            self.todo_page.text_multi_text.SetFocus()
        elif index == 2:
            self.famous_page.text_multi_text.SetFocus()
        elif index == 3:
            self.message_page.text_multi_text.SetFocus()

    def KeyRunApp(self, key):
        # Ctrl F1 -- Ctrl F12
        length = len(dbmenus.menus)
        if ((key > 339) and (key < 353)):
            index = key - 340
            if index < length:
                menu = dbmenus.menus[index]
                cmd = "".join(menu[1:])
                subprocess.Popen(cmd.encode("gbk"), shell=True)
                self.GetTopLevelParent().SetMessageValue(_("Start App: ") + cmd)

        # if (key == 340):
        #     index = key - 340
        #     if index < length:
        #         menu = dbmenus.menus[index]
        #         cmd = "".join(menu[1:])
        #         subprocess.Popen(cmd.encode("gbk"), shell=True)
        #         self.GetTopLevelParent().SetMessageValue(_("Start App: ") + cmd)
        # elif (key == 341):
        #     index = key - 340
        #     if index < length:
        #         menu = dbmenus.menus[index]
        #         cmd = "".join(menu[1:])
        #         subprocess.Popen(cmd.encode("gbk"), shell=True)
        #         self.GetTopLevelParent().SetMessageValue(_("Start App: ") + cmd)
        # elif (key == 342):
        #     index = key - 340
        #     if index < length:
        #         menu = dbmenus.menus[index]
        #         cmd = "".join(menu[1:])
        #         subprocess.Popen(cmd.encode("gbk"), shell=True)
        #         self.GetTopLevelParent().SetMessageValue(_("Start App: ") + cmd)
        # elif (key == 343):
        #     index = key - 340
        #     if index < length:
        #         menu = dbmenus.menus[index]
        #         cmd = "".join(menu[1:])
        #         subprocess.Popen(cmd.encode("gbk"), shell=True)
        #         self.GetTopLevelParent().SetMessageValue(_("Start App: ") + cmd)
        # elif (key == 344):
        #     index = key - 340
        #     if index < length:
        #         menu = dbmenus.menus[index]
        #         cmd = "".join(menu[1:])
        #         subprocess.Popen(cmd.encode("gbk"), shell=True)
        #         self.GetTopLevelParent().SetMessageValue(_("Start App: ") + cmd)
        # elif (key == 345):
        #     index = key - 340
        #     if index < length:
        #         menu = dbmenus.menus[index]
        #         cmd = "".join(menu[1:])
        #         subprocess.Popen(cmd.encode("gbk"), shell=True)
        #         self.GetTopLevelParent().SetMessageValue(_("Start App: ") + cmd)
        # elif (key == 346):
        #     index = key - 340
        #     if index < length:
        #         menu = dbmenus.menus[index]
        #         cmd = "".join(menu[1:])
        #         subprocess.Popen(cmd.encode("gbk"), shell=True)
        #         self.GetTopLevelParent().SetMessageValue(_("Start App: ") + cmd)
        # elif (key == 347):
        #     index = key - 340
        #     if index < length:
        #         menu = dbmenus.menus[index]
        #         cmd = "".join(menu[1:])
        #         subprocess.Popen(cmd.encode("gbk"), shell=True)
        #         self.GetTopLevelParent().SetMessageValue(_("Start App: ") + cmd)
        # elif (key == 348):
        #     index = key - 340
        #     if index < length:
        #         menu = dbmenus.menus[index]
        #         cmd = "".join(menu[1:])
        #         subprocess.Popen(cmd.encode("gbk"), shell=True)
        #         self.GetTopLevelParent().SetMessageValue(_("Start App: ") + cmd)
        # elif (key == 349):
        #     index = key - 340
        #     if index < length:
        #         menu = dbmenus.menus[index]
        #         cmd = "".join(menu[1:])
        #         subprocess.Popen(cmd.encode("gbk"), shell=True)
        #         self.GetTopLevelParent().SetMessageValue(_("Start App: ") + cmd)
        # elif (key == 350):
        #     index = key - 340
        #     if index < length:
        #         menu = dbmenus.menus[index]
        #         cmd = "".join(menu[1:])
        #         subprocess.Popen(cmd.encode("gbk"), shell=True)
        #         self.GetTopLevelParent().SetMessageValue(_("Start App: ") + cmd)
        # elif (key == 351):
        #     index = key - 340
        #     if index < length:
        #         menu = dbmenus.menus[index]
        #         cmd = "".join(menu[1:])
        #         subprocess.Popen(cmd.encode("gbk"), shell=True)
        #         self.GetTopLevelParent().SetMessageValue(_("Start App: ") + cmd)
        # elif (key == 352):
        #     index = key - 340
        #     if index < length:
        #         menu = dbmenus.menus[index]
        #         cmd = "".join(menu[1:])
        #         subprocess.Popen(cmd.encode("gbk"), shell=True)
        #         self.GetTopLevelParent().SetMessageValue(_("Start App: ") + cmd)

    def OnSetup(self, event):
        #self.MultiTextSetFocus()
        self.system_setup_frame = SetupFrame(self.GetTopLevelParent())
        self.system_setup_frame.Show(True)

    def parse_shutdown_string(self):
        input_string = self.text_shutdown_time.GetValue().strip()
        if input_string.find('.') > -1:
            try:
                num = float(input_string)
            except:
                num = 0.0
            self.shutdown_timeout = int(num * 60 * 60)
        else:
            if input_string.isdigit():
                num = int(input_string)
                self.shutdown_timeout = int(num * 60)

    def OnShutdown(self, event):
        self.parse_shutdown_string()
        cmd = "shutdown /s -t " + str(self.shutdown_timeout)
        subprocess.Popen(cmd.encode("gbk"), shell=True)
        self.GetTopLevelParent().OnClose(event)

    def OnRestart(self, event):
        self.parse_shutdown_string()
        cmd = "shutdown /r -t " + str(self.shutdown_timeout)
        subprocess.Popen(cmd.encode("gbk"), shell=True)
        self.GetTopLevelParent().OnClose(event)

    def OnLock(self, event):
        cmd = "rundll32.exe user32.dll,LockWorkStation"
        subprocess.Popen(cmd.encode("gbk"), shell=True)

    def OnChanged(self, event):
        #print "onchanged"
        self.MultiTextSetFocus()
        index = self.nb.GetSelection()
        dbmenus.current["nb"] = index
        #dbmenus.SetTextCtrl(self.GetTopLevelParent(), self.GetParent().GetParent(), self.text_multi_text)
        if index == 0:
            dbmenus.SetTextCtrl(self.GetTopLevelParent(), self, self.text_page.text_multi_text)
        elif index == 1:
            dbmenus.SetTextCtrl(self.GetTopLevelParent(), self, self.todo_page.text_multi_text)
        # elif index == 2:
        #     dbmenus.SetTextCtrl(self.GetTopLevelParent(), self, self.famous_page.text_multi_text)
        # elif index == 3:
        #     dbmenus.SetTextCtrl(self.GetTopLevelParent(), self, self.message_page.text_multi_text)

    def SaveContent(self):
        dbmenus.ConfigSave()
        # wxPython 2.9.5 + winXP, TextCtrl->SaveFile() have bug
        self.text_page.text_multi_text.SaveFile(dbmenus.text_file)
        self.todo_page.text_multi_text.SaveFile(dbmenus.todo_file)
        # self.famous_page.text_multi_text.SaveFile( self.famous_page.famous_file)
        # content = self.text_page.text_multi_text.GetValue()
        # fd = open(dbmenus.text_file, 'w')
        # fd.write(content)
        # fd.close()
        # content = self.todo_page.text_multi_text.GetValue()
        # fd = open(dbmenus.todo_file, 'w')
        # fd.write(content)
        # fd.close()
        # del content


# class TaskBarIcon(wx.TaskBarIcon):
#     ID_Hello = wx.NewId()
#     def __init__(self, frame):
#         wx.TaskBarIcon.__init__(self)
#         self.frame = frame
#         self.SetIcon(wx.Icon(name='menus.ico', type=wx.BITMAP_TYPE_ICO), 'NewMenus')

#         self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDClick)

#     def OnTaskBarLeftDClick(self, event):
#         if self.frame.IsIconized():
#             self.frame.Iconize(False)
#         if not self.frame.IsShown():
#             self.frame.Show(True)
#         self.frame.Raise()

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "New Menus", size=(900, 700))
        self.SetIcon(wx.Icon('menus.ico', wx.BITMAP_TYPE_ICO))

        self.Center()
        self.system = platform.system()
        self.timer_current_value = 0
        # panel = wx.Panel(self)

        # dbmenus.sys_color = self.GetBackgroundColour()
        dbmenus.big_font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        dbmenus.big_font.SetPointSize(dbmenus.big_font.GetPointSize() + dbmenus.current["text_size"])

        # drop target
        dt = FileDropTarget(self)
        self.SetDropTarget(dt)

        if (dbmenus.global_help_enable == False):
            self.statusBar = None
        else:
            self.statusBar = self.CreateStatusBar()

        self.middlePanel = MiddlePanel(self)
        self.appPanel = AppPanel(self)

        self.mediaPlayer = wx.media.MediaCtrl(self.middlePanel, style=wx.SIMPLE_BORDER)
        ding = os.path.join(dbmenus.basepath, "ding.mp3")
        if os.path.exists(ding):
            if not self.mediaPlayer.Load(ding):
                wx.MessageBox("Unable to load %s: Unsupported format?" % "ding.mp3", "ERROR", wx.OK)
            else:
                self.mediaPlayer.SetInitialSize()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.appPanel, 0, wx.EXPAND)
        self.sizer.Add(wx.StaticLine(self), flag=wx.EXPAND)
        self.sizer.Add(self.middlePanel, 1, wx.EXPAND)

        self.SetSizer(self.sizer)
        self.Layout()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

        self.messagetimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnMessageTimer, self.messagetimer)

        if dbmenus.global_timer_enable:
            value = dbmenus.current["timer_timeout"]*60*1000
            self.timer.Start(value)
            self.timer_current_value = value
            # self.timer.Start(dbmenus.current["timer_timeout"]*60*1000)

        # self.taskBarIcon = TaskBarIcon(self)
        # self.Bind(wx.EVT_ICONIZE, self.OnIconfiy)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # self.regHotKey()
        # if self.system == "Windows":
        #     self.Bind(wx.EVT_HOTKEY, self.handleHotKeyF1, id=self.hotKeyIdF1)
        #     self.Bind(wx.EVT_HOTKEY, self.handleHotKeyF2, id=self.hotKeyIdF2)
        #     self.Bind(wx.EVT_HOTKEY, self.handleHotKeyF3, id=self.hotKeyIdF3)
        #     self.Bind(wx.EVT_HOTKEY, self.handleHotKeyF4, id=self.hotKeyIdF4)
        #     self.Bind(wx.EVT_HOTKEY, self.handleHotKeyF5, id=self.hotKeyIdF5)
        #     self.Bind(wx.EVT_HOTKEY, self.handleHotKeyF6, id=self.hotKeyIdF6)
        #     self.Bind(wx.EVT_HOTKEY, self.handleHotKeyF7, id=self.hotKeyIdF7)
        #     self.Bind(wx.EVT_HOTKEY, self.handleHotKeyF8, id=self.hotKeyIdF8)
        #     self.Bind(wx.EVT_HOTKEY, self.handleHotKeyF9, id=self.hotKeyIdF9)
        #     self.Bind(wx.EVT_HOTKEY, self.handleHotKeyF10, id=self.hotKeyIdF10)
        #     self.Bind(wx.EVT_HOTKEY, self.handleHotKeyF11, id=self.hotKeyIdF11)
        #     self.Bind(wx.EVT_HOTKEY, self.handleHotKeyF12, id=self.hotKeyIdF12)

        # set focus on multitext
        self.middlePanel.MultiTextSetFocus()

    # def regHotKey(self):
    #     # This function registers the hotkey Alt+F1 with id=100
    #     if self.system == "Windows":
    #         faild_key = ""
    #         self.hotKeyIdF1 = 100
    #         result = self.RegisterHotKey(
    #             self.hotKeyIdF1,
    #             win32con.MOD_CONTROL | win32con.MOD_ALT,
    #             win32con.VK_F1)
    #         if not result:
    #             faild_key += "F1 "
    #         self.hotKeyIdF2 = 101
    #         result = self.RegisterHotKey(
    #             self.hotKeyIdF2,
    #             win32con.MOD_CONTROL | win32con.MOD_ALT,
    #             win32con.VK_F2)
    #         if not result:
    #             faild_key += "F2 "

    #         self.hotKeyIdF3 = 102
    #         result = self.RegisterHotKey(
    #             self.hotKeyIdF3,
    #             win32con.MOD_CONTROL | win32con.MOD_ALT,
    #             win32con.VK_F3)
    #         if not result:
    #             faild_key += "F3 "

    #         self.hotKeyIdF4 = 103
    #         result = self.RegisterHotKey(
    #             self.hotKeyIdF4,
    #             win32con.MOD_CONTROL | win32con.MOD_ALT,
    #             win32con.VK_F4)
    #         if not result:
    #             faild_key += "F4 "

    #         self.hotKeyIdF5 = 104
    #         result = self.RegisterHotKey(
    #             self.hotKeyIdF5,
    #             win32con.MOD_CONTROL | win32con.MOD_ALT,
    #             win32con.VK_F5)
    #         if not result:
    #             faild_key += "F5 "

    #         result = self.hotKeyIdF6 = 105
    #         self.RegisterHotKey(
    #             self.hotKeyIdF6,
    #             win32con.MOD_CONTROL | win32con.MOD_ALT,
    #             win32con.VK_F6)
    #         if not result:
    #             faild_key += "F6 "

    #         self.hotKeyIdF7 = 106
    #         result = self.RegisterHotKey(
    #             self.hotKeyIdF7,
    #             win32con.MOD_CONTROL | win32con.MOD_ALT,
    #             win32con.VK_F7)
    #         if not result:
    #             faild_key += "F7 "

    #         self.hotKeyIdF8 = 107
    #         result = self.RegisterHotKey(
    #             self.hotKeyIdF8,
    #             win32con.MOD_CONTROL | win32con.MOD_ALT,
    #             win32con.VK_F8)
    #         if not result:
    #             faild_key += "F8 "

    #         self.hotKeyIdF9 = 109
    #         result = self.RegisterHotKey(
    #             self.hotKeyIdF9,
    #             win32con.MOD_CONTROL | win32con.MOD_ALT,
    #             win32con.VK_F9)
    #         if not result:
    #             faild_key += "F9 "

    #         self.hotKeyIdF10 = 109
    #         result = self.RegisterHotKey(
    #             self.hotKeyIdF10,
    #             win32con.MOD_CONTROL | win32con.MOD_ALT,
    #             win32con.VK_F10)
    #         if not result:
    #             faild_key += "F10 "

    #         self.hotKeyIdF11 = 110
    #         result = self.RegisterHotKey(
    #             self.hotKeyIdF11,
    #             win32con.MOD_CONTROL | win32con.MOD_ALT,
    #             win32con.VK_F11)
    #         if not result:
    #             faild_key += "F11 "

    #         self.hotKeyIdF12 = 111
    #         result = self.RegisterHotKey(
    #             self.hotKeyIdF12,
    #             win32con.MOD_CONTROL | win32con.MOD_ALT,
    #             win32con.VK_F12)
    #         if not result:
    #             faild_key += "F12 "

    #         if faild_key:
    #             self.SetMessageValue(_("Rigister global hotkey faild, Ctrl Alt: ") + faild_key)

    # def handleHotKeyF1(self, evt):
    #     len = dbmenus.menus
    #     index = 0
    #     if len > 0:
    #         menu = dbmenus.menus[index]
    #         cmd = "".join(menu[1:])
    #         subprocess.Popen(cmd.encode("gbk"), shell=True)

    # def handleHotKeyF2(self, evt):
    #     len = dbmenus.menus
    #     index = 1
    #     if len > 1:
    #         menu = dbmenus.menus[index]
    #         cmd = "".join(menu[1:])
    #         subprocess.Popen(cmd.encode("gbk"), shell=True)

    # def handleHotKeyF3(self, evt):
    #     len = dbmenus.menus
    #     index = 2
    #     if len > 2:
    #         menu = dbmenus.menus[index]
    #         cmd = "".join(menu[1:])
    #         subprocess.Popen(cmd.encode("gbk"), shell=True)

    # def handleHotKeyF4(self, evt):
    #     len = dbmenus.menus
    #     index = 3
    #     if len > 3:
    #         menu = dbmenus.menus[index]
    #         cmd = "".join(menu[1:])
    #         subprocess.Popen(cmd.encode("gbk"), shell=True)

    # def handleHotKeyF5(self, evt):
    #     len = dbmenus.menus
    #     index = 4
    #     if len > 4:
    #         menu = dbmenus.menus[index]
    #         cmd = "".join(menu[1:])
    #         subprocess.Popen(cmd.encode("gbk"), shell=True)

    # def handleHotKeyF6(self, evt):
    #     len = dbmenus.menus
    #     index = 5
    #     if len > 5:
    #         menu = dbmenus.menus[index]
    #         cmd = "".join(menu[1:])
    #         subprocess.Popen(cmd.encode("gbk"), shell=True)

    # def handleHotKeyF7(self, evt):
    #     len = dbmenus.menus
    #     index = 6
    #     if len > 6:
    #         menu = dbmenus.menus[index]
    #         cmd = "".join(menu[1:])
    #         subprocess.Popen(cmd.encode("gbk"), shell=True)

    # def handleHotKeyF8(self, evt):
    #     len = dbmenus.menus
    #     index = 7
    #     if len > 7:
    #         menu = dbmenus.menus[index]
    #         cmd = "".join(menu[1:])
    #         subprocess.Popen(cmd.encode("gbk"), shell=True)

    # def handleHotKeyF9(self, evt):
    #     len = dbmenus.menus
    #     index = 8
    #     if len > 8:
    #         menu = dbmenus.menus[index]
    #         cmd = "".join(menu[1:])
    #         subprocess.Popen(cmd.encode("gbk"), shell=True)

    # def handleHotKeyF10(self, evt):
    #     len = dbmenus.menus
    #     index = 9
    #     if len > 9:
    #         menu = dbmenus.menus[index]
    #         cmd = "".join(menu[1:])
    #         subprocess.Popen(cmd.encode("gbk"), shell=True)

    # def handleHotKeyF11(self, evt):
    #     len = dbmenus.menus
    #     index = 10
    #     if len > 10:
    #         menu = dbmenus.menus[index]
    #         cmd = "".join(menu[1:])
    #         subprocess.Popen(cmd.encode("gbk"), shell=True)

    # def handleHotKeyF12(self, evt):
    #     if self.IsShown():
    #         self.Show(False)
    #     else:
    #         self.Show(True)

        # len = dbmenus.menus
        # index = 11
        # if len > 11:
        #     menu = dbmenus.menus[index]
        #     cmd = "".join(menu[1:])
        #     subprocess.Popen(cmd.encode("gbk"), shell=True)

    def OnIconfiy(self, event):
        self.Hide()

    def playMusic(self, path):
        self.mediaPlayer.Play()

    def OnTimer(self, event):
        if dbmenus.global_timer_enable:
            self.timer.Stop()
            self.mediaPlayer.Play()
            # wx.MessageBox(_("Have a rest for yourself ......"), caption=_("Message"), style=wx.OK)
            value = dbmenus.current["timer_timeout"]*60*1000

            self.timer.Start(value)
            self.timer_current_value = value

    def Timer_OnOff(self):
        if dbmenus.global_timer_enable:
            if self.timer.IsRunning():
                self.timer.Stop()
                self.middlePanel.timer_state.SetLabel("‖ ")
                self.SetMessageValue(_("Timer stop"))
            else:
                value = dbmenus.current["timer_timeout"]*60*1000
                self.timer.Start(value)
                self.timer_current_value = value
                # self.timer.Start(dbmenus.current["timer_timeout"]*60*1000)
                self.middlePanel.timer_state.SetLabel("〉 ")
                self.SetMessageValue(_("Timer start"))
        else:
            if self.timer.IsRunning():
                self.timer.Stop()
                self.middlePanel.timer_state.SetLabel("‖ ")
                self.SetMessageValue(_("Timer stop"))

    def Timer_Restart(self):
        if dbmenus.global_timer_enable:
            value = dbmenus.current["timer_timeout"]*60*1000
            if value != self.timer_current_value:
                if self.timer.IsRunning():
                    self.timer.Stop()
                    self.timer.Start(value)
                    self.timer_current_value = value
                    self.middlePanel.timer_state.SetLabel("〉 ")
                    self.SetMessageValue(_("Timer start"))

    def SetMessageValue(self, text, last=False):
        if (dbmenus.global_help_enable == False):
            return

        self.messagetimer.Stop()
        if self.statusBar:
            self.statusBar.SetStatusText(text)

        if last == False:
            self.messagetimer.Start(5000)

    def OnMessageTimer(self, event):
        self.messagetimer.Stop()
        if self.statusBar:
            self.statusBar.SetStatusText("")

    def addApp(self):
        self.appPanel.addApp()
        self.SetSizer(self.sizer)
        self.sizer.Layout()

    def OnCommand(self, event):
        self.appPanel.addApp()
        self.SetSizer(self.sizer)
        self.sizer.Layout()

    def OnClose(self, event):
        self.middlePanel.SaveContent()
        self.Destroy()
        # self.taskBarIcon.Destroy()
        if self.middlePanel.system_setup_frame:
            self.middlePanel.system_setup_frame.Destroy()
        #event.Skip()

    def OnExit(self, event):
        #self.Close()
        self.Destroy()
        event.Skip()

class SetupPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetupContentChanged = False

        label_title = wx.StaticText(self, -1, _("Quick Menu Setup"))
        label_title.SetFont(dbmenus.big_font)
        self.listbox = wx.ListBox(self, -1, (20, 20), (230, 420), [], wx.LB_SINGLE)
        list_up = wx.Button(self, -1, label="↑")
        list_down = wx.Button(self, -1, label="↓")
        list_app_delete = wx.Button(self, -1, label=_("Del"))
        list_app_save = wx.Button(self, -1, label=_("Save"))
        list_app_clear = wx.Button(self, -1, label=_("Clear"))
        list_app_add = wx.Button(self, -1, label=_("Add"))

        label_cmd_name = wx.StaticText(self, -1, _("Name"))
        label_cmd_command = wx.StaticText(self, -1, _("Command"))
        self.cmd_name = wx.TextCtrl(self, 0, "", size=(160, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
        self.cmd_command = wx.TextCtrl(self, 0, "", size=(400, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);

        cmd_backup = wx.Button(self, -1, label=_("Backup"))
        label_backup = wx.StaticText(self, -1, _("Data protection is the most important"))
        cmd_startup = wx.Button(self, -1, label=_("Startup"))
        label_startup = wx.StaticText(self, -1, _("Create Startup Shortcut"))
        cmd_desktop = wx.Button(self, -1, label=_("Desktop"))
        label_desktop = wx.StaticText(self, -1, _("Create Desktop Shortcut"))
        cmd_close = wx.Button(self, -1, label=_("Close"))

        label_lang = wx.StaticText(self, -1, _("Language"))
        self.radio_zh = wx.RadioButton(self, -1, "中文", style=wx.RB_GROUP)
        self.radio_en = wx.RadioButton(self, -1, "English")
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioLanguage, self.radio_zh)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioLanguage, self.radio_en)

        label_timer_time = wx.StaticText(self, -1, _("Timer time"))
        self.text_timer_time = wx.TextCtrl(self, -1, "60", size=(60, -1))
        self.text_timer_time.Bind(wx.EVT_TEXT, self.OnInputText)
        self.timer_checkbox = wx.CheckBox(self, -1, _("Enable"), (20, 20), (150, 20))

        self.help_checkbox = wx.CheckBox(self, -1, _("Help"), (20, 20), (150, 20))
        #self.message_checkbox = wx.CheckBox(self, -1, _("Message"), (20, 20), (150, 20))

        # start layout
        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_list = wx.BoxSizer(wx.HORIZONTAL)
        vbox_list_cmd = wx.BoxSizer(wx.VERTICAL)
        # vbox_list_cmd.Add(list_app_add, 0, flag=wx.ALIGN_LEFT)
        # vbox_list_cmd.Add((15, 15))
        vbox_list_cmd.Add((15, 15))
        vbox_list_cmd.Add(list_app_add, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15, 15))
        vbox_list_cmd.Add(list_app_save, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15, 15))
        vbox_list_cmd.Add(list_app_clear, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15, 15))
        vbox_list_cmd.Add(list_app_delete, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15, 15))
        vbox_list_cmd.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_list_cmd.Add((15, 15))
        vbox_list_cmd.Add(list_up, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15, 15))
        vbox_list_cmd.Add(list_down, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15, 15))

        # vbox_app = wx.BoxSizer(wx.HORIZONTAL)
        # vbox_app.Add(label_cmd_name, 0, flag=wx.ALIGN_LEFT)

        vbox_timer = wx.BoxSizer(wx.HORIZONTAL)
        vbox_timer.Add(label_timer_time, 0, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER)
        vbox_timer.Add((5, 5))
        vbox_timer.Add(self.text_timer_time, 0, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER)
        vbox_timer.Add((10, 10))
        vbox_timer.Add(self.timer_checkbox, 0, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER)

        vbox_lang = wx.BoxSizer(wx.HORIZONTAL)
        vbox_lang.Add(self.radio_zh, flag=wx.ALIGN_LEFT)
        vbox_lang.Add(self.radio_en, flag=wx.ALIGN_LEFT)

        vbox_line = wx.BoxSizer(wx.HORIZONTAL)
        vbox_line.Add(cmd_backup, 0, flag=wx.ALIGN_LEFT)
        vbox_line.Add((5, 5))
        vbox_line.Add(label_backup, 0, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER)

        vbox_startup_line = wx.BoxSizer(wx.HORIZONTAL)
        vbox_startup_line.Add(cmd_startup, 0, flag=wx.ALIGN_LEFT)
        vbox_startup_line.Add((5, 5))
        vbox_startup_line.Add(label_startup, 0, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER)

        vbox_desktop_line = wx.BoxSizer(wx.HORIZONTAL)
        vbox_desktop_line.Add(cmd_desktop, 0, flag=wx.ALIGN_LEFT)
        vbox_desktop_line.Add((5, 5))
        vbox_desktop_line.Add(label_desktop, 0, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER)

        vbox_add_content = wx.BoxSizer(wx.VERTICAL)
        vbox_add_content.Add(label_cmd_name, 0, flag=wx.ALIGN_LEFT)
        #vbox_add_content.Add(vbox_app, flag=wx.ALIGN_LEFT)
        #vbox_add_content.Add(label_cmd_name, flag=wx.ALIGN_LEFT)
        vbox_add_content.Add(self.cmd_name, 0, flag=wx.ALIGN_LEFT)
        vbox_add_content.Add((10, 10))
        vbox_add_content.Add(label_cmd_command, 0, flag=wx.ALIGN_LEFT)
        vbox_add_content.Add(self.cmd_command, 1, flag=wx.EXPAND)
        vbox_add_content.Add((15, 15))
        vbox_add_content.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_add_content.Add((15, 15))
        vbox_add_content.Add(vbox_timer, flag=wx.ALIGN_LEFT)
        vbox_add_content.Add((15, 15))
        vbox_add_content.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_add_content.Add((15, 15))
        vbox_add_content.Add(label_lang, 0, flag=wx.ALIGN_LEFT)
        vbox_add_content.Add((5, 5))
        vbox_add_content.Add(vbox_lang, flag=wx.ALIGN_LEFT)
        vbox_add_content.Add((15, 15))
        vbox_add_content.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_add_content.Add((15, 15))
        vbox_add_content.Add(self.help_checkbox, 0, flag=wx.ALIGN_LEFT)
        vbox_add_content.Add((15, 15))
        # vbox_add_content.Add(self.message_checkbox, 0, flag=wx.ALIGN_LEFT)
        # vbox_add_content.Add((15, 15))
        vbox_add_content.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_add_content.Add((12, 12))
        vbox_add_content.Add(vbox_line, flag=wx.ALIGN_LEFT)
        vbox_add_content.Add((12, 12))
        vbox_add_content.Add(vbox_startup_line, flag=wx.ALIGN_LEFT)
        vbox_add_content.Add((12, 12))
        vbox_add_content.Add(vbox_desktop_line, flag=wx.ALIGN_LEFT)
        #vbox_add_content.Add(cmd_startup, 0, flag=wx.ALIGN_LEFT)

        vbox_list.Add(self.listbox, 0, flag=wx.ALIGN_CENTER)
        vbox_list.Add((15, 15))
        vbox_list.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), flag=wx.EXPAND)
        vbox_list.Add((15, 15))
        vbox_list.Add(vbox_list_cmd, 0, flag=wx.ALIGN_CENTER)
        vbox_list.Add((15, 15))
        vbox_list.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), flag=wx.EXPAND)
        vbox_list.Add((15, 15))
        vbox_list.Add(vbox_add_content, 0, flag=wx.ALIGN_TOP)

        vbox_cmd = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd.Add(cmd_close, 0, flag=wx.ALIGN_CENTER)

        vbox_top.Add((15, 15))
        vbox_top.Add(label_title, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15, 15))
        vbox_top.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_top.Add((15, 15))
        vbox_top.Add(vbox_list, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15, 15))
        vbox_top.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_top.Add((10, 10))
        vbox_top.Add(vbox_cmd, 0, wx.ALIGN_CENTER)

        #Start Fit
        self.SetSizer(vbox_top)
        self.Layout()

        # self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnDclickListBox, self.listbox)
        self.Bind(wx.EVT_LISTBOX, self.OnListBox, self.listbox)
        self.Bind(wx.EVT_BUTTON, self.OnListUp, list_up)
        self.Bind(wx.EVT_BUTTON, self.OnListDown, list_down)
        self.Bind(wx.EVT_BUTTON, self.OnListAppDelete, list_app_delete)
        self.Bind(wx.EVT_BUTTON, self.OnListAppSave, list_app_save)
        self.Bind(wx.EVT_BUTTON, self.OnListAppAdd, list_app_add)
        self.Bind(wx.EVT_BUTTON, self.OnListAppClear, list_app_clear)
        self.Bind(wx.EVT_BUTTON, self.OnCmdClose, cmd_close)
        self.Bind(wx.EVT_BUTTON, self.OnCmdBackup, cmd_backup)
        self.Bind(wx.EVT_BUTTON, self.OnCmdStartup, cmd_startup)
        self.Bind(wx.EVT_BUTTON, self.OnCmdDesktop, cmd_desktop)
        self.Bind(wx.EVT_CHECKBOX, self.OnTimerCheckBox, self.timer_checkbox)
        self.Bind(wx.EVT_CHECKBOX, self.OnHelpCheckBox, self.help_checkbox)
        # self.Bind(wx.EVT_CHECKBOX, self.OnMessageCheckBox, self.message_checkbox)

        self.LoadToUI()
        self.quickmenu_read_write()

    def OnCmdStartup(self, event):
        dbmenus.Startup()
        # self.GetParent().GetParent().GetParent().SetMessageValue("create startup")
        self.GetTopLevelParent().SetMessageValue(_("Create Startup Succeed."))

    def OnCmdDesktop(self, event):
        dbmenus.Desktop()
        # self.GetParent().GetParent().GetParent().SetMessageValue("create startup")
        self.GetTopLevelParent().SetMessageValue(_("Create Desktop Succeed."))

    def OnRadioLanguage(self, event):
        radioSelected = event.GetEventObject()
        text = radioSelected.GetLabel()
        dbmenus.current["lang"] = text
        self.SetupContentChanged = True

    def OnTimerCheckBox(self, event):
        if (self.timer_checkbox.GetValue() == True):
            dbmenus.current["timer_enable"] = 1
            dbmenus.global_timer_enable = True
            self.GetTopLevelParent().main_frame.Timer_OnOff()
        else:
            dbmenus.current["timer_enable"] = 0
            dbmenus.global_timer_enable = False
            self.GetTopLevelParent().main_frame.Timer_OnOff()

        self.SetupContentChanged = True

    def OnHelpCheckBox(self, event):
        if (self.help_checkbox.GetValue() == True):
            dbmenus.current["help_enable"] = 1
        else:
            dbmenus.current["help_enable"] = 0

        self.SetupContentChanged = True

    # def OnMessageCheckBox(self, event):
    #     if (self.message_checkbox.GetValue() == True):
    #         dbmenus.current["message_enable"] = 1
    #     else:
    #         dbmenus.current["message_enable"] = 0

    #     self.SetupContentChanged = True

    def OnInputText(self, event):
        result = self.text_timer_time.GetValue()
        if result.isdigit():
            dbmenus.current["timer_timeout"] = int(result)
            self.SetupContentChanged = True

    def LoadToUI(self):
        if dbmenus.current["lang"] == "English":
            self.radio_en.SetValue(True)
            self.radio_zh.SetValue(False)
        else:
            self.radio_zh.SetValue(True)
            self.radio_en.SetValue(False)

        if dbmenus.current["help_enable"] == 1:
            self.help_checkbox.SetValue(True)
        else:
            self.help_checkbox.SetValue(False)

        # if dbmenus.current["message_enable"] == 1:
        #     self.message_checkbox.SetValue(True)
        # else:
        #     self.message_checkbox.SetValue(False)

        if dbmenus.current["timer_enable"] == 1:
            self.timer_checkbox.SetValue(True)
        else:
            self.timer_checkbox.SetValue(False)

        self.text_timer_time.SetValue(str(dbmenus.current["timer_timeout"]))

    def quickmenu_read_write(self, Write = False):
        if (Write == False) and os.path.isfile(dbmenus.quickmenu_filename):
            for menu in dbmenus.menus:
                self.listbox.Append(menu[0])

            print(dbmenus.menus)
            if len(dbmenus.menus) > 0:
                self.listbox.SetSelection(0)
                menu = dbmenus.menus[0]
                self.cmd_name.SetValue(menu[0])
                self.cmd_command.SetValue(menu[1])

        if Write == True:
            dbmenus.quickmenu_write()
            # fd = open(dbmenus.quickmenu_filename, 'w')
            # for li in dbmenus.menus:
            #     line = "::".join(ele for ele in li) + "\n"
            #     fd.write(line)
            # fd.close()

    def OnListUp(self, event):
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        if (total > 0) and (select > 0):
            name1 = self.listbox.GetString(select -1)
            name2 = self.listbox.GetString(select)
            self.listbox.SetString(select-1, name2)
            self.listbox.SetString(select, name1)
            dbmenus.menus[select-1], dbmenus.menus[select] = dbmenus.menus[select], dbmenus.menus[select-1]
            self.listbox.SetSelection(select-1)
            self.SetupContentChanged = True

    def OnListDown(self, event):
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        if (total > 0)  and (select < total - 1):
            name1 = self.listbox.GetString(select )
            name2 = self.listbox.GetString(select+1)
            self.listbox.SetString(select, name2)
            self.listbox.SetString(select+1, name1)
            dbmenus.menus[select], dbmenus.menus[select+1] = dbmenus.menus[select+1], dbmenus.menus[select]
            self.listbox.SetSelection(select+1)
            self.SetupContentChanged = True

    def OnListAppAdd(self, event):
        # dialog = wx.DirDialog(None,"Choose a directory:",
        #                       style=wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST)
        #os.environ['PROGRAMDATA']
        spath = os.environ['PROGRAMDATA']
        dialog = wx.FileDialog(self, "Choose app", spath, "",
                                      "*.*",
                                      wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            input_path = dialog.GetPath().decode('utf-8')
            name, txt = os.path.splitext(os.path.basename(input_path))
            self.cmd_name.SetValue(name)
            self.cmd_command.SetValue(input_path)
        dialog.Destroy()

    def OnListAppSave(self, event):
        add_new = True
        name = self.cmd_name.GetValue().strip()
        command = self.cmd_command.GetValue().strip()
        if len(name) == 0 or len(command) == 0:
            self.GetTopLevelParent().SetMessageValue(_("Add Faild! no name or command"))
            return False

        for menu in dbmenus.menus:
            if menu[1] == command:
                add_new = False

        if (add_new == True):
            dbmenus.menus.append([name, command])
            self.listbox.Append(name)
            total = self.listbox.GetCount()
            self.listbox.SetSelection(total-1)
            self.SetupContentChanged = True
            self.GetTopLevelParent().SetMessageValue(_("Add a new app menu"))
        else:
            index = self.listbox.GetSelection()
            menu = dbmenus.menus[index]

            self.listbox.SetString(index, name)
            dbmenus.menus[index] = [name, command]
            self.SetupContentChanged = True

            self.GetTopLevelParent().SetMessageValue(_("Save app menu: ") + name)

    # def OnCmdAdd(self, event):
    #     name = self.cmd_name.GetValue().strip()
    #     command = self.cmd_command.GetValue().strip()
    #     if len(name) == 0 or len(command) == 0:
    #         self.GetTopLevelParent().SetMessageValue(_("Add Faild! no name or command"))
    #         return False

    #     if [name, command] not in dbmenus.menus:
    #         dbmenus.menus.append([name, command])
    #         self.listbox.Append(name)
    #         self.cmd_name.SetValue("")
    #         self.cmd_command.SetValue("")
    #         self.SetupContentChanged = True
    #         self.GetTopLevelParent().SetMessageValue(_("Add a new app menu"))
    #     else:
    #         self.GetTopLevelParent().SetMessageValue(_("Add Faild! Command duplication"))

    #     return True

    def OnListAppClear(self, event):
        self.cmd_name.SetValue("")
        self.cmd_command.SetValue("")
        self.cmd_name.SetFocus()

    def OnListAppDelete(self, event):
        totals = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        if (totals > 0)  and (select < totals):
            self.listbox.Delete(select)
            del dbmenus.menus[select]
            totals -= 1
            if (select == totals):
                select -= 1
            self.listbox.SetSelection(select)
            self.OnListBox(event)
            self.SetupContentChanged = True

    def OnListBox(self, event):
        index = self.listbox.GetSelection()
        menu = dbmenus.menus[index]
        self.cmd_name.SetValue(menu[0])
        self.cmd_command.SetValue(menu[1])

    def OnCmdBackup(self, event):
        input_path = ""
        dialog = wx.DirDialog(None,"Choose a directory:",
                              style=wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            input_path = dialog.GetPath().decode('utf-8')
            if os.path.exists(dbmenus.basepath_doc):
                outpath = input_path + os.sep + "newmenu_doc"
                if os.path.exists(outpath):
                    shutil.rmtree(outpath)
                shutil.copytree(dbmenus.basepath_doc, outpath)
                self.GetTopLevelParent().SetMessageValue(_("Backup doc to: " + outpath))

        dialog.Destroy()

    def OnCmdClose(self, event):
        if self.SetupContentChanged:
            self.GetTopLevelParent().main_frame.Timer_Restart()
            #self.quickmenu_read_write(True)
            self.GetTopLevelParent().SetMessageValue(_("Saved app menu"))
            self.GetTopLevelParent().main_frame.addApp()
            #dbmenus.ConfigSave()


        self.GetTopLevelParent().Destroy()
        # self.Destroy()
        event.Skip()

class SetupFamousPage(wx.Panel):
    """famous working"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        # self.famous_file = "menudoc" + os.sep + "famous.txt"

        # self.SetBackgroundColour(dbmenus.sys_color)
        # label_title = wx.StaticText(self, -1, _("Famous Info"))
        # label_title.SetFont(dbmenus.big_font)
        self.text_multi_text = wx.TextCtrl(self, -1, "", size=(550, 450), style=wx.TE_MULTILINE)
        self.text_multi_text.SetFont(dbmenus.big_font)
        button_close = wx.Button(self, -1, label=_("Close"))

        vbox_cmd = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd.Add(button_close, 0, wx.ALIGN_CENTER)

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_top.Add((15, 15))
        vbox_top.Add(self.text_multi_text, 1, wx.EXPAND) #, 0, wx.ALIGN_CENTER)
        vbox_top.Add((10, 10))
        vbox_top.Add(vbox_cmd, 0, flag=wx.ALIGN_CENTER)
        vbox_top.Add((10, 10))

        self.SetSizer(vbox_top)
        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)
        # mouse
        # self.text_multi_text.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.text_multi_text.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseLeftDClick)

        if os.path.exists(dbmenus.famous_file):
            self.text_multi_text.LoadFile(dbmenus.famous_file)
            # fd = codecs.open(dbmenus.famous_file, mode='r', encoding="utf-8")
            # content = fd.read()
            # self.text_multi_text.SetValue(content)
            # fd.close()
            # del content

    def OnClose(self, event):
        # self.GetTopLevelParent().Destroy()
        self.Parse_famous_content()
        # wxPython 2.9.5 + winXP, TextCtrl->SaveFile() have bug
        self.text_multi_text.SaveFile(dbmenus.famous_file)
        #dbmenus.ConfigSave()
        # content = self.text_multi_text.GetValue()
        # fd = open(dbmenus.famous_file, 'w')
        # fd.write(content)
        # fd.close()
        # del content
        self.GetTopLevelParent().Destroy()

    def Parse_famous_content(self):
        if self.text_multi_text.IsEmpty():
            return
        item_num = 0
        index_line = -1
        startPos = 0
        endPos = 0
        totals = self.text_multi_text.GetNumberOfLines()
        for i in range(totals):
            line = self.text_multi_text.GetLineText(i).strip()
            if not line:
                continue
            if (line.find(CONTENT_ITEM_TAG) != -1):
                item_num = item_num + 1
                continue
            elif (line.strip().startswith("#")):
                continue
            elif (line.strip().startswith("index:")):
                index_line = i
                length = self.text_multi_text.GetLineLength(i)
                startPos = self.text_multi_text.XYToPosition(0, i)
                endPos = self.text_multi_text.XYToPosition(length, i)
                continue

        if (startPos == 0) and (endPos == 0):
            string = "index: " + str(item_num) + "\n"
        else:
            string = "index: " + str(item_num)
        self.text_multi_text.Replace(startPos, endPos, string)
        # wxPython 2.9.5, TextCtrl->SaveFile() have bug
        self.text_multi_text.SaveFile(dbmenus.famous_file)
        # content = self.text_multi_text.GetValue()
        # fd = open(dbmenus.famous_file, 'w')
        # fd.write(content)
        # fd.close()
        # del content

    def OnMouseLeftUp(self, event):
        # string = self.text_multi_text.GetStringSelection()
        # print string
        pass

    def OnMouseLeftDClick(self, event):
        self.SetCurrentLine()

    def SetCurrentLine(self):
        curPos = self.text_multi_text.GetInsertionPoint()
        col, line = self.text_multi_text.PositionToXY(curPos)
        length = self.text_multi_text.GetLineLength(line)
        startPos = self.text_multi_text.XYToPosition(0, line)
        endPos = self.text_multi_text.XYToPosition(length, line)

        self.text_multi_text.SetSelection(startPos, endPos)

class SetupHelpPage(wx.Panel):
    def __init__(self, parent):
        self.current_item = 0;
        self.total_item = 0;
        wx.Panel.__init__(self, parent)
        # self.SetBackgroundColour(dbmenus.sys_color)
        if dbmenus.current["lang"] == "English":
            self.help_file = os.path.join(dbmenus.basepath_doc, "en", "help.txt")
        else:
            self.help_file = os.path.join(dbmenus.basepath_doc, "zh", "help.txt")

        button_close = wx.Button(self, -1, label=_("Close"))

        label_title = wx.StaticText(self, -1, _("Help Info"))
        label_title.SetFont(dbmenus.big_font)
        self.text_multi_text = wx.TextCtrl(self, -1, "", size=(500, 440), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.text_multi_text.SetFont(dbmenus.big_font)

        self.tree = wx.TreeCtrl(self, -1, size=(200, 440), style=wx.TR_HAS_BUTTONS|wx.TR_DEFAULT_STYLE|wx.SUNKEN_BORDER)
        root = self.tree.AddRoot(_("Help"))
        self.__AddTreeNodes(root)
        self.tree.Expand(root)

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_win = wx.BoxSizer(wx.HORIZONTAL)

        vbox_win.Add(self.tree, 0, wx.ALIGN_LEFT)
        vbox_win.Add((15, 15))
        vbox_win.Add(self.text_multi_text, 1, wx.EXPAND) # 0, wx.ALIGN_LEFT)

        vbox_top.Add((10, 10))
        vbox_top.Add(label_title, 0, wx.ALIGN_CENTER)
        vbox_top.Add((10, 10))
        vbox_top.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_top.Add((10, 10))
        vbox_top.Add(vbox_win, 0, wx.ALIGN_CENTER)
        vbox_top.Add((10, 10))
        vbox_top.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_top.Add((10, 10))
        vbox_top.Add(button_close, 0, wx.ALIGN_CENTER)

        self.SetSizer(vbox_top)
        self.Layout()
        # vbox_top.Fit(self)

        # map event
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)
        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)

    def OnClose(self, event):
        #dbmenus.ConfigSave()
        self.GetTopLevelParent().Destroy()

    def __AddTreeNodes(self, parentItem):
        self.tree.AppendItem(parentItem, "Application")
        self.tree.AppendItem(parentItem, "Note")
        self.tree.AppendItem(parentItem, "Todo")
        self.tree.AppendItem(parentItem, "Famous")
        self.tree.AppendItem(parentItem, "Message")
        self.tree.AppendItem(parentItem, "Timer")
        self.tree.AppendItem(parentItem, "Setup")
        help_info = self.help_file_get_text_by_index(1)
        self.text_multi_text.SetValue(help_info)

    def OnSelChanged(self, event):
        help_info = ""
        text = self.tree.GetItemText(event.GetItem())
        if text == "Application":
            help_info = self.help_file_get_text_by_index(2)
        elif text == "Note":
            help_info = self.help_file_get_text_by_index(3)
        elif text == "Todo":
            help_info = self.help_file_get_text_by_index(4)
        elif text == "Famous":
            help_info = self.help_file_get_text_by_index(5)
        elif text == "Message":
            help_info = self.help_file_get_text_by_index(6)
        elif text == "Timer":
            help_info = self.help_file_get_text_by_index(7)
        elif text == "Setup":
            help_info = self.help_file_get_text_by_index(8)
        else:
            help_info = self.help_file_get_text_by_index(1)
            pass

        self.text_multi_text.SetValue(help_info)

    def help_file_get_text_by_index(self, index):
        help_text = ""
        if (index < 1):
            return help_text
        fd = open(self.help_file, mode='rt', encoding="utf-8")
        item_num = 0
        found_item = False
        while True:
            line = fd.readline()
            if not line:
                break
            if (line.find(CONTENT_ITEM_TAG) != -1):
                item_num = item_num + 1
                if (item_num == index):
                    found_item = True
                    continue
                if (found_item == True):
                    break
            else:
                if (found_item == True):
                    help_text = help_text + line

        help_text = help_text
        return help_text;

class SetupUpdatePage(wx.Panel):
    """this software auto update"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        # self.SetBackgroundColour(dbmenus.sys_color)
        self.update_path = os.path.join(dbmenus.basepath, "update")
        self.version = "1.0"
        self.web_version= "1.0"

        # self.version_file=os.path.join(dbmenus.basepath, "doc"+os.sep+"version.txt")
        self.url_info = "http://face2group.com/software/newmenus/newmenus.html"
        # self.url_info = "http://127.0.0.1/software/newimages/newimages.html"
        self.update_url = ""
        self.update_program = ""
        self.platform = ""
        self.enable_update = False

        label_title = wx.StaticText(self, -1, _("Update Online"))
        label_title.SetFont(dbmenus.big_font)
        label_current = wx.StaticText(self, -1, _("Current version:"), size=(120, -1))
        self.text_current_version = wx.TextCtrl(self, -1, "", size=(120, -1))
        label_new = wx.StaticText(self, -1, _("New version:"), size=(120, -1))
        self.text_new_version = wx.TextCtrl(self, -1, "", size=(120, -1))
        label_features = wx.StaticText(self, -1, _("Features:"), size=(80, -1))
        self.text_features = wx.TextCtrl(self, -1, "", size=(400, 320), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.text_features.SetFont(dbmenus.big_font)
        label_url_update = wx.StaticText(self, -1, _("Update:"), size=(80, -1))
        self.text_url_update = wx.TextCtrl(self, -1, _(" "), size=(350, -1))
        self.button_update = wx.Button(self, -1, label=_("Check"))
        # self.button_update.Disable()
        button_close = wx.Button(self, -1, label=_("Close"))

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_grid = wx.GridBagSizer(hgap=2, vgap=2)
        vbox_features = wx.BoxSizer(wx.HORIZONTAL)
        vbox_updatefile = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd = wx.BoxSizer(wx.HORIZONTAL)

        vbox_grid.Add(label_current, pos=(0,0), flag=wx.ALIGN_RIGHT, border=10)
        vbox_grid.Add(self.text_current_version, pos=(0,1), flag=wx.ALIGN_LEFT, border=10)
        vbox_grid.Add(label_new, pos=(1,0), flag=wx.ALIGN_RIGHT, border=10)
        vbox_grid.Add(self.text_new_version, pos=(1,1), flag=wx.ALIGN_LEFT, border=10)

        vbox_features.Add(label_features, 0, wx.ALIGN_RIGHT|wx.TOP)
        vbox_features.Add(self.text_features, 0, wx.ALIGN_CENTER)

        vbox_updatefile.Add(label_url_update, 0, wx.ALIGN_RIGHT|wx.TOP)
        vbox_updatefile.Add(self.text_url_update, 0, wx.ALIGN_CENTER)

        vbox_cmd.Add(self.button_update, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add(button_close, 0, wx.ALIGN_CENTER)

        vbox_top.Add((10, 10))
        vbox_top.Add(label_title, 0, wx.ALIGN_CENTER)
        vbox_top.Add((10, 10))
        vbox_top.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_top.Add((15, 15))
        vbox_top.Add(vbox_grid, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15, 15))
        vbox_top.Add(vbox_features, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15, 15))
        vbox_top.Add(vbox_updatefile, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15, 15))
        vbox_top.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_top.Add((10, 10))
        vbox_top.Add(vbox_cmd, 0, wx.ALIGN_CENTER)

        self.SetSizer(vbox_top)
        self.Layout()
        # vbox_top.Fit(self)

        self.get_local_version_info()

        self.Bind(wx.EVT_BUTTON, self.OnUpdate, self.button_update)
        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)

    def OnClose(self, event):
        #dbmenus.ConfigSave()
        self.GetTopLevelParent().Destroy()

    def OnUpdate(self, event):
        if self.enable_update == False:
            self.get_new_version_info()
            return

        # download and unextact files, then close main program and start update program; copy files and start main program, then close update program.
        if not os.path.isdir(self.update_path):
            os.mkdir(self.update_path)
        os.chdir(self.update_path)
        #self.get_url_file(self.update_url)
        dbmenus.get_url_file(self.update_url)
        filename = os.path.basename(self.update_url)
        # filename = self.update_path + os.sep +  filename
        self.update_extract(filename)

        # open update program
        # close main program
        self.GetTopLevelParent().main_frame.Destroy()
        self.GetTopLevelParent().Destroy()
        wx.Exit()

        shutil.copy(self.update_program, "../")
        os.chdir("../")
        cmd = self.update_program + " newmenus"
        subprocess.Popen(cmd.encode("gbk"))

    def get_local_version_info(self):
        # get local version
        try:
            fd = open(dbmenus.version_file, 'r')
        except IOError:
            # print("file: " + self.version_file + " no exist!")
            return False
        for line in fd:
            line = line.strip()
            if line.startswith("version"):
                li = line.split(":")
                if (len(li) > 1):
                    self.version = li[1].strip()
                    self.text_current_version.SetValue(self.version)
                    # break
            elif line.startswith("platform"):
                li = line.split(":")
                if (len(li) > 1):
                    self.platform = li[1].strip()
                pass
            elif (line.strip().startswith("#")):
                continue

        fd.close()

    def get_new_version_info(self):
        # get web version
        try:
            info = urllib.request.urlopen(self.url_info)
        except urllib.error.HTTPError as e:
            # print e.fp.read()
            return

        new_feature = False
        for line in info:
            line = line.strip()
            if line.startswith("version"):
                li = line.split(":")
                if (len(li) > 1):
                    self.web_version = li[1].strip()
                    self.text_new_version.SetValue(self.web_version)
            elif line.startswith("new feature"):
                new_feature = True
                self.text_features.SetValue("")
            elif line.startswith("win32_update_packages") and self.platform == "win32":
                li = line.split("s:")
                if (len(li) > 1):
                    self.update_url = li[1].strip()
            elif line.startswith("win32_update_program") and self.platform == "win32":
                li = line.split(":")
                if (len(li) > 1):
                    self.update_program = li[1].strip()
            elif line.startswith("win64_update_packages") and self.platform == "win64":
                li = line.split("s:")
                if (len(li) > 1):
                    self.update_url = li[1].strip()
            elif line.startswith("win64_update_program") and self.platform == "win64":
                li = line.split(":")
                if (len(li) > 1):
                    self.update_program = li[1].strip()
            elif line.startswith("darwin_update_packages") and self.platform == "darwin":
                li = line.split("s:")
                if (len(li) > 1):
                    self.update_url = li[1].strip()
            elif line.startswith("drawin_update_program") and self.platform == "drawin":
                li = line.split(":")
                if (len(li) > 1):
                    self.update_program = li[1].strip()
            elif line.startswith("linux_update_packages") and self.platform == "linux":
                li = line.split("s:")
                if (len(li) > 1):
                    self.update_url = li[1].strip()
            elif line.startswith("linux_update_program") and self.platform == "linux":
                li = line.split(":")
                if (len(li) > 1):
                    self.update_program = li[1].strip()

            elif line.startswith("*"):
                if new_feature == True:
                    self.text_features.AppendText(line.decode('utf-8')+"\n")
            else:
                if new_feature == True:
                    new_feature = False
        info.close()

        if self.compare_version() == True:
            self.enable_update = True
            self.button_update.SetLabel(_("Update"))
            self.text_url_update.SetValue(self.update_url)
        else:
            self.text_url_update.SetValue("")
            self.enable_update = False
            # print "compare versin false"

    def compare_version(self):
        tup = lambda x:[int(y) for y in (x+'.0.0.0.0').split('.')][:4]
        return cmp(tup(self.web_version), tup(self.version))


    def update_extract(self, filename):
        # print "try to extract zip file"
        # os.chdir("update")
        try:
            f = zipfile.ZipFile(filename)
            f.extractall()
        except zipfile.error as e:
            print("Bad zipfile: %s" % (e))

        f.close()
        # print "extract end"

    def cbk(self, a, b, c):
        # need download process display
        per = 100.0 * a * b / c
        if per > 100:
            per = 100
            self.text_url_update.SetValue(self.update_url)
            # print '%.2f%%' % per
        self.text_url_update.SetValue('%.2f%%' % per)

class SetupAboutPage(wx.Panel):
    """this software auto update"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        # self.SetBackgroundColour(dbmenus.sys_color)

        if dbmenus.current["lang"] == "English":
            self.about_file = os.path.join(dbmenus.basepath_doc, "en", "about.txt")
        else:
            self.about_file = os.path.join(dbmenus.basepath_doc, "zh", "about.txt")

        label_title = wx.StaticText(self, -1, _("About NewMenus"))
        label_title.SetFont(dbmenus.big_font)
        alipay = wx.StaticText(self, -1, "支付宝: luckrill@163.com", size=(500, -1))
        paypal = wx.StaticText(self, -1, "PayPal: luckrill@163.com", size=(500, -1))
        email = wx.StaticText(self, -1, " Email: luckrill@163.com", size=(500, -1))
        self.text_about = wx.TextCtrl(self, -1, "", size=(650, 410), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.text_about.SetFont(dbmenus.big_font)
        button_close = wx.Button(self, -1, label=_("Close"))

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_top.Add((10, 10))
        vbox_top.Add(label_title, 0, wx.ALIGN_CENTER)
        vbox_top.Add((10, 10))
        vbox_top.Add(alipay, 0, wx.ALIGN_CENTER)
        vbox_top.Add(paypal, 0, wx.ALIGN_CENTER)
        vbox_top.Add(email, 0, wx.ALIGN_CENTER)
        vbox_top.Add((10, 10))
        vbox_top.Add(self.text_about, 0, wx.ALIGN_CENTER)
        vbox_top.Add((10, 10))
        vbox_top.Add(button_close, 0, wx.ALIGN_CENTER)

        self.SetSizer(vbox_top)
        self.Layout()
        # vbox_top.Fit(self)

        self.__get_about_info()

        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)

    def OnClose(self, event):
        self.GetTopLevelParent().Destroy()

    def __get_about_info(self):
        try:
            fd = open(self.about_file, 'r', encoding='UTF-8')
        except IOError:
            # print("file: " + self.about_file + " no exist!")
            return False
        for line in fd:
            self.text_about.AppendText(line)
        fd.close()

class SetupFrame(wx.Frame):
    """System Setup Frame class, sub window."""
    def __init__(self, mainframe):
        """Create a Frame instance"""
        wx.Frame.__init__(self, None, title=_("System Setup"), size=(800, 650))
        # self.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)
        self.Centre()

        self.main_frame = mainframe
        self.current_index = 0

        panel = wx.Panel(self, size=self.GetSize())

        if (dbmenus.global_help_enable == False):
            self.statusBar = None
        else:
            self.statusBar = self.CreateStatusBar()

        self.nb = wx.Notebook(panel)
        self.setup_page = SetupPage(self.nb)
        self.famous_page = SetupFamousPage(self.nb)
        self.helpinfo_page = SetupHelpPage(self.nb)
        self.update_page = SetupUpdatePage(self.nb)
        about_page = SetupAboutPage(self.nb)

        self.nb.AddPage(self.setup_page, _("System Setup"))
        self.nb.AddPage(self.famous_page, _("Famous Setup"))
        self.nb.AddPage(self.helpinfo_page, _("Help Info"))
        self.nb.AddPage(self.update_page, _("Update"))
        self.nb.AddPage(about_page, _("About"))

        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)

        panel.SetSizer(sizer)
        panel.Layout()
        #sizer.Fit(self)

        #self.nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnChanged)

        self.nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnChanged)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.messagetimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnMessageTimer, self.messagetimer)

    def SetMessageValue(self, text, last=False):
        if (dbmenus.global_help_enable == False):
            return

        self.messagetimer.Stop()
        if self.statusBar:
            self.statusBar.SetStatusText(text)

        if last == False:
            self.messagetimer.Start(5000)

    def OnMessageTimer(self, event):
        self.messagetimer.Stop()
        if self.statusBar:
            self.statusBar.SetStatusText("")

    def OnChanged(self, event):
        old_index = event.GetOldSelection()
        if old_index == 0:
            if self.setup_page.SetupContentChanged:
                self.GetTopLevelParent().main_frame.Timer_Restart()
                #self.setup_page.quickmenu_read_write(True)
                self.SetMessageValue(_("Saved app menu"))
                self.main_frame.addApp()

    def OnClose(self, event):
        if self.setup_page.SetupContentChanged:
            self.GetTopLevelParent().main_frame.Timer_Restart()
            self.setup_page.quickmenu_read_write(True)
            self.SetMessageValue(_("Saved app menu"))
            self.main_frame.addApp()

        self.Destroy()

class FileDropTarget(wx.FileDropTarget):
    def __init__(self, mainframe):
        """ Initialize the Drop Target, passing in the Object Reference to
        indicate what should receive the dropped files """
        # Initialize the wxFileDropTarget Object
        wx.FileDropTarget.__init__(self)
        self.mainframe = mainframe

    def OnDropFiles(self, x, y, filenames):
        # print filenames
        first = True
        for file in filenames:
            self.mainframe.appPanel.AddNewApp(file)
            # if first == True:
            #     self.mainframe.AddImageFiles(file, True)
            #     first = False
            # else:
            #     print file
            #     self.mainframe.AddImageFiles(file, False)

class CompositeDropTarget(wx.PyDropTarget):
    """Implements drop target functionality to receive files, bitmaps and text"""
    def __init__(self):
        wx.PyDropTarget.__init__(self)
        self.do = wx.DataObjectComposite()  # the dataobject that gets filled with the appropriate data
        self.filedo = wx.FileDataObject()
        self.textdo = wx.TextDataObject()
        self.bmpdo = wx.BitmapDataObject()
        self.do.Add(self.filedo)
        self.do.Add(self.bmpdo)
        self.do.Add(self.textdo)
        self.SetDataObject(self.do)

    def OnData(self, x, y, d):
        """
        Handles drag/dropping files/text or a bitmap
        """
        # print "Handles drag/dropping files/text or a bitmap"
        if self.GetData():
            df = self.do.GetReceivedFormat().GetType()
            if df in [wx.DF_UNICODETEXT, wx.DF_TEXT]:
                text = self.textdo.GetText()
            elif df == wx.DF_FILENAME:
                for name in self.filedo.GetFilenames():
                    pass
            elif df == wx.DF_BITMAP:
                bmp = self.bmpdo.GetBitmap()

        return d  # you must return this

dbmenus = DBmenus()

class App(wx.App):
    """Application class."""
    def OnInit(self):
        dbmenus.ConfigLoad()
        localedir = os.path.join(dbmenus.basepath, "mdoc", "locale")
        if dbmenus.current["lang"] == "English":
            langid = wx.LANGUAGE_ENGLISH_US
        else:
            langid = wx.LANGUAGE_CHINESE_SIMPLIFIED
        domain = "newmenus"             # the translation file is messages.mo
        L.Init(langid)
        L.AddCatalogLookupPathPrefix(localedir)
        L.AddCatalog(domain)

        self.frame = MainFrame()
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True

def main():
    app = App()
    app.MainLoop()

if __name__ == '__main__':
    main()
