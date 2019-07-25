#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import os
import sys
from datetime import datetime
import subprocess
import importlib

# mult_text; todo; app; 1 hours time message

# add timer message
# add command self add/delete function
## format: {Emacs} : {D:\Program Files\emacs-24\bin\runemacs.exe}

importlib.reload(sys)
sys.setdefaultencoding("utf-8")
_ = wx.GetTranslation

Default_timeout = 4
Autokey_state = False
app4_cmd = r'"D:\Program Files\emacs-24\bin\runemacs.exe"'
app3_cmd = r'"C:\Program Files\Mozilla Firefox\firefox.exe"'
app2_cmd = r'"C:\Program Files\SecureCRT\SecureCRT.EXE"'
app1_cmd = r'"C:\Program Files\Outlook Express\msimn.exe"'
text_filename = "autokey_text.txt"
quickmenu_filename = "quickmenu.txt"

log = False

class DBmenus():
    menus = []
    big_font = None
    sys_color = 0
    def __init__(self):
        pass

class AppPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.menudb = []
        self.quickmenufile = "quickmenu.txt"
        self.number_of_command = 0
        self.subs = []
        self.addApp()

    def addApp(self):
        for app in self.subs:
            if log:
                print(("destroy" + str(app)))
            app.Destroy()
        self.subs = []

        self.sizer = wx.GridSizer(cols=5, hgap=2, vgap=12)

        self.quickmenu_read()
        for li in self.menudb:
            self.number_of_command += 1
            name = li[0]
            if log:
                print(name)
            button_cmd = wx.Button(self, label=name, name=name)
            self.subs.append(button_cmd)
            button_cmd.name = name
            self.sizer.Add(button_cmd, 0, wx.ALIGN_CENTER)
            button_cmd.Bind(wx.EVT_BUTTON, self.OnCommand)

        self.Refresh()
        self.SetSizerAndFit(self.sizer)
        
    def OnCommand(self, event):
        name = event.GetEventObject().name
        for li in self.menudb:
            if name == li[0]:
                cmd = "".join(li[1:])
                # print(name, cmd)
                subprocess.Popen(cmd, shell=True)

    def quickmenu_read(self):
        if os.path.isfile(self.quickmenufile):
            fd = open(self.quickmenufile, 'r')
            del self.menudb[:]
            while True:
                line = fd.readline()
                if not line:
                    break
                line = line.strip()
                li = line.split("::")
                li = [str.strip() for str in li]
                if line[0] != '#':
                    self.menudb.append(li)
            fd.close()

class TextPage(wx.Panel):
    """this software auto update"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.text_file = "menudoc/content.txt"
        self.key_ctrl = False
        self.key_shift = False
        self.key_alt = False
        # self.SetBackgroundColour(dbimages.sys_color)
        # label_title.SetFont(dbimages.sys_font)
        self.text_multi_text = wx.TextCtrl(self, -1, "", size=(700, 500), style=wx.TE_MULTILINE)
        self.text_multi_text.SetFont(dbmenus.big_font)
        button_test = wx.Button(self, -1, label=_("test"))
        button_close = wx.Button(self, -1, label=_("Close"))

        vbox_cmd = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd.Add(button_test, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add(button_close, 0, wx.ALIGN_CENTER)

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_top.Add((15,15))
        vbox_top.Add((15,15))
        vbox_top.Add(self.text_multi_text, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_cmd, 0, flag=wx.ALIGN_CENTER)
        vbox_top.Add((5,5))

        self.SetSizer(vbox_top)
        self.Layout()
        #vbox_top.Fit(self)

        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)
        self.Bind(wx.EVT_BUTTON, self.OnTest, button_test)
        # key, key up call twice, self and text widget
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        # self.text_multi_text.Bind(wx.EVT_CHAR, self.OnChar)
        self.text_multi_text.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        # mouse
        self.text_multi_text.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.text_multi_text.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseLeftDClick)

        if os.path.exists(self.text_file):
            self.text_multi_text.LoadFile(self.text_file)

    def OnSetup(self, event):
        pass
        # self.GetTopLevelParent()
        # quickmenu_setup_frame = QuickMenuSetupFrame(self.GetTopLevelParent())
        # quickmenu_setup_frame.Show(True)

    def OnTest(self, event):
        # GetLineText(lineNo)
        # GetNumberOfLines()
        # GetLineLength(lineNo)
        # WriteText(text), current point
        
        # SetSelection(-1,-1) will do it. 

        # GetSelection()
        # GetStringSelection()
        # SetSelection(from, to)
        # Replace(from, to, value)
        # GetRange(from, to)

        string = self.text_multi_text.GetStringSelection()
        print("out selection string")
        print(string)
        print(self.text_multi_text.GetNumberOfLines())
        string = self.text_multi_text.GetLineText(5)
        print("out ling string")
        print(string)
        print(self.text_multi_text.GetSelection())

        curPos = self.text_multi_text.GetInsertionPoint()
        cols, line = self.text_multi_text.PositionToXY(curPos)
        print((cols, line))

        self.SetCurrentLine()
        string = self.text_multi_text.GetStringSelection()
        print(string)
        self.ClipCopyTo(string)

    def OnKeyDown(self, event):
        # WXK_TAB, WXK_SHIFT, WXK_CONTROL, WXK_ALT
        print("key down")
        key = event.GetKeyCode()
        if (key == wx.WXK_CONTROL):
            self.key_ctrl = True
        pass
        event.Skip()

    def OnChar(self, event):
        print("on char")
        if (self.key_ctrl == False):
            event.Skip()
            return
        key = event.GetKeyCode()
        print(key)
        if key < 256:
            char = chr(key)
            print(("onchar Ctrl-%s:"%(char)))
        event.Skip()
        pass

    def OnKeyUp(self, event):
        print("on key up ======")
        key = event.GetKeyCode()
        # print ("KeyPress: %d"% (key)

        if (self.key_ctrl == False):
            event.Skip()
            return

        if (key == wx.WXK_CONTROL):
            self.key_ctrl = False

        key = event.GetKeyCode()
        if key < 256:
            char = chr(key)
            print(("onkeyup Ctrl-%s:"%(char)))
            # add function

        event.Skip()

    def SetCurrentLine(self):
        curPos = self.text_multi_text.GetInsertionPoint()
        col, line = self.text_multi_text.PositionToXY(curPos)
        print((col, line))
        length = self.text_multi_text.GetLineLength(line)
        startPos = self.text_multi_text.XYToPosition(0, line)
        endPos = self.text_multi_text.XYToPosition(length, line)

        self.text_multi_text.SetSelection(startPos, endPos)

    def ClipCopyTo(self, string):
        if not wx.TheClipboard.IsOpened():  # may crash, otherwise
            data = wx.TextDataObject(string)
            wx.TheClipboard.Open()
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()
            print("copyto succeed")
        pass

    def OnOpenDir(self, event):
        input_path = ""
        # check clipboard
        if not wx.TheClipboard.IsOpened():  # may crash, otherwise
            data = wx.TextDataObject()
            newdata = wx.TextDataObject("")
            wx.TheClipboard.Open()
            success = wx.TheClipboard.GetData(data)
            # howto wx.TheClipboard.Clear(), clear() only server for SetData
            # wx.TheClipboard.Clear()
            # wx.TheClipboard.SetData(newdata)
            wx.TheClipboard.Close()
            # print "handler clipboard data"
            if success:
                texts = str(data.GetText().strip().decode("utf-8"))
                # print "clipboard: ", texts
                if os.path.exists(texts) and os.path.isdir(texts):
                    open_path_info = "Do you want to open: \n\n" + texts
                    dlg = wx.MessageDialog(None, open_path_info, 
                                           "Open image path?",
                                           wx.YES_NO| wx.ICON_QUESTION)
                    result = dlg.ShowModal()
                    dlg.Destroy()
                    if result == wx.ID_YES:
                        input_path = texts
                        # print ("input_path: ", input_path)
                        self.AddImageFiles(input_path, True)

                        # clear clpboard
                        wx.TheClipboard.Open()
                        wx.TheClipboard.Clear()
                        wx.TheClipboard.SetData(newdata)
                        wx.TheClipboard.Close()
                        return

        dialog = wx.DirDialog(None,"Choose a directory:",
                              style=wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST)
        # dialog = wx.FileDialog(self, "Choose images", "", "", 
        #                               "*.*", 
        #                               wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_OK:
            # print dialog.GetPath()
            # print dialog.GetPaths()
            # print dialog.GetDirectory()
            # print dialog.GetFilename()
            # print dialog.GetFilenames()
            input_path = dialog.GetPath().decode('utf-8')

        dialog.Destroy()
        self.AddImageFiles(input_path, True)

    def OnMouseLeftUp(self, event):
        print("OnMouseLeftUp")
        string = self.text_multi_text.GetStringSelection()
        print(string)

        pass

    def OnMouseLeftDClick(self, event):
        print("OnMouseLeftDClick")
        self.SetCurrentLine()

        pass

    def OnClose(self, event):
        self.GetTopLevelParent().Destroy()
        # self.GetTopLevelParent().SaveContent()
        self.GetParent().GetParent().SaveContent()
        # self.text_multi_text.SaveFile(self.text_file)



class TodoPage(wx.Panel):
    """this software auto update"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.todo_file = "menudoc/todo.txt"
        self.todo_list = []
        self.mark = ','
        # self.SetBackgroundColour(dbimages.sys_color)
        # label_title.SetFont(dbimages.sys_font)
        self.text_multi_text = wx.TextCtrl(self, -1, "", size=(700, 500), style=wx.TE_MULTILINE)
        self.text_multi_text.SetFont(dbmenus.big_font)
        button_sort = wx.Button(self, -1, label=_("Sort"))
        button_close = wx.Button(self, -1, label=_("Close"))

        vbox_cmd = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd.Add(button_sort, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add(button_close, 0, wx.ALIGN_CENTER)

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_top.Add((15,15))
        vbox_top.Add(self.text_multi_text, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_cmd, 0, flag=wx.ALIGN_CENTER)
        vbox_top.Add((15,15))

        self.SetSizer(vbox_top)
        self.Layout()
        #vbox_top.Fit(self)

        self.Bind(wx.EVT_BUTTON, self.OnSort, button_sort)
        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.text_multi_text.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.text_multi_text.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseLeftDClick)

        if os.path.exists(self.todo_file):
            self.text_multi_text.LoadFile(self.todo_file)

    def OnSort(self, event):
        if self.text_multi_text.IsEmpty():
            return

        totals = self.text_multi_text.GetNumberOfLines()
        del self.todo_list[:]
        for i in range(totals):
            string = self.text_multi_text.GetLineText(i).strip()
            if string:
                print(string)
                num, text = self.parse_line(string)
                print(str(num) + " : " + text)
                self.todo_list.append([num, text])

        print(self.todo_list)
        self.todo_list.sort(key=lambda x:x[0])
        print(self.todo_list)
        self.text_multi_text.Clear()
        for li in self.todo_list:
            print(li)
            line = str(li[0]) + self.mark + ' ' + li[1] + "\n"
            self.text_multi_text.AppendText(line)

    def parse_line(self, string):
        index = string.find(' ')
        if index > 0:
            li = string.split()
            if len(li) < 1:
                return
            num_string = li[0]
            if num_string.isdigit():
                num = int(num_string)
            else:
                self.mark = num_string[-1]
                num_string = num_string[:-1]
                print(num_string)
                if num_string.isdigit():
                    num = int(num_string)
                else:
                    print("num string error")

            text = li[1]
            return num, text

    def OnMouseLeftUp(self, event):
        print("OnMouseLeftUp")
        pass

    def OnMouseLeftDClick(self, event):
        print("OnMouseLeftDClick")
        pass

    def OnKeyUp(self, event):
        # print "on key up ======"
        key = event.GetKeyCode()
        print(("KeyPress: %d"% (key)))
        # PageUp 366; PageDown 367
        # (27, 32, 314, 315, 316, 317)
        event.Skip()

    def OnClose(self, event):
        self.GetTopLevelParent().Destroy()
        self.GetParent().GetParent().SaveContent()
        # self.text_multi_text.SaveFile(self.todo_file)

class FamousPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.famous_file = "menudoc/famous.txt"

        # self.SetBackgroundColour(dbimages.sys_color)
        # label_title.SetFont(dbimages.sys_font)
        self.text_multi_text = wx.TextCtrl(self, -1, "", size=(700, 500), style=wx.TE_MULTILINE)
        self.text_multi_text.SetFont(dbmenus.big_font)
        button_new = wx.Button(self, -1, label=_("New"))
        button_setup = wx.Button(self, -1, label=_("Setup"))
        button_close = wx.Button(self, -1, label=_("Close"))

        vbox_cmd = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd.Add(button_new, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add(button_setup, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add(button_close, 0, wx.ALIGN_CENTER)

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_top.Add((15,15))
        vbox_top.Add(self.text_multi_text, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_cmd, 0, flag=wx.ALIGN_CENTER)
        vbox_top.Add((15,15))

        self.SetSizer(vbox_top)
        self.Layout()
        #vbox_top.Fit(self)


        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.text_multi_text.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.text_multi_text.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseLeftDClick)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        if os.path.exists(self.famous_file):
            self.text_multi_text.LoadFile(self.famous_file)

    def OnMouseLeftUp(self, event):
        print("OnMouseLeftUp")
        pass

    def OnMouseLeftDClick(self, event):
        print("OnMouseLeftDClick")
        pass

    def OnKeyUp(self, event):
        # print "on key up ======"
        key = event.GetKeyCode()
        print(("KeyPress: %d"% (key)))
        # PageUp 366; PageDown 367
        # (27, 32, 314, 315, 316, 317)
        event.Skip()

    def OnClose(self, event):
        self.GetTopLevelParent().Destroy()
        self.GetParent().GetParent().SaveContent()
        # self.text_multi_text.SaveFile(self.famous_file)


class MiddlePanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.autokey_timeout = int(Default_timeout * 60)
        self.shutdown_timeout = 0
        self.shutdown_or_restart = True
        self.autokey_state = False
        self.shutdown_state = False

        if not os.path.exists("menudoc"):
            os.mkdir("menudoc")

        button_shutdown = wx.Button(self, label="Shutdown", size=(-1, 30))
        button_restart = wx.Button(self, label="Restart", size=(-1, 30))
        self.text_shutdown_time = wx.TextCtrl(self, -1, "0", size=(50, 30))
        label_units = wx.StaticText(self, -1, "m/h")
        button_setup = wx.Button(self, label="Setup", size=(-1, 30))

        # self.sizer = wx.BoxSizer(wx.VERTICAL) #HORIZONTAL) 
        vbox_cmd = wx.BoxSizer(wx.HORIZONTAL) 
        vbox_cmd.Add(button_shutdown, 0, flag=wx.ALIGN_CENTER)
        vbox_cmd.Add(button_restart, 0, flag=wx.ALIGN_CENTER)
        vbox_cmd.Add(self.text_shutdown_time, 0, flag=wx.ALIGN_RIGHT)
        vbox_cmd.Add(label_units, 0, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER)
        vbox_cmd.Add(button_setup, 0, flag=wx.ALIGN_CENTER)

        self.nb = wx.Notebook(self)
        self.text_page = TextPage(self.nb)
        self.todo_page = TodoPage(self.nb)
        self.famous_page = FamousPage(self.nb)

        self.nb.AddPage(self.text_page, ("Text"))
        self.nb.AddPage(self.todo_page, ("Todo"))
        self.nb.AddPage(self.famous_page, ("Famous"))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(vbox_cmd, 0, flag=wx.ALIGN_RIGHT)
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Layout()

        self.nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnChanged)
        self.Bind(wx.EVT_BUTTON, self.OnShutdown, button_shutdown)
        self.Bind(wx.EVT_BUTTON, self.OnRestart, button_restart)
        self.Bind(wx.EVT_BUTTON, self.OnSetup, button_setup)

    def OnSetup(self, event):
        system_setup_frame = SystemSetupFrame(self.GetTopLevelParent())
        system_setup_frame.Show(True)
        pass

    def OnShutdown(self, event):
        pass

    def OnRestart(self, event):
        pass

    def OnChanged(self, event):
        # print self.nb.GetSelection()
        # print self.nb.GetPageText(2)
        index = self.nb.GetSelection()
        # if index == 0:
        #     self.text_page.text_multi_text.SetFocus()
        # elif index == 1:
        #     self.todo_page.text_multi_text.SetFocus()
        # elif index == 2:
        #     self.famous_page.text_multi_text.SetFocus()
        # else:
        #     pass

    def SaveContent(self):
        self.text_page.text_multi_text.SaveFile( self.text_page.text_file)
        self.todo_page.text_multi_text.SaveFile( self.todo_page.todo_file)
        self.famous_page.text_multi_text.SaveFile( self.famous_page.famous_file)
        pass



class MainFrame(wx.Frame):
    def __init__(self):
#        wx.Frame.__init__(self, None)
        wx.Frame.__init__(self, None, -1, "Auto Key", size=(900, 700))

        self.Centre()

#        panel = wx.Panel(self)

        dbmenus.sys_color = self.GetBackgroundColour()
        dbmenus.big_font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        dbmenus.big_font.SetPointSize(dbmenus.big_font.GetPointSize()+3)

        # # popup menu start
        # self.popupmenu = wx.Menu()

        # menu_item1 = self.popupmenu.Append(2001, "&test1 menu\tCtrl-B")
        # menu_item2 = self.popupmenu.Append(2002, "&test2 menu\tCtrl-X")
        # menu_quickmenu_setup = self.popupmenu.Append(2003, "&QuickMenuSetup\tCtrl-Q")
        # menu_timer_setup = self.popupmenu.Append(2004, "&TimerSetup\tCtrl-T")
        # self.popupmenu.AppendSeparator()
        # menu_exit = self.popupmenu.Append(-1, "E&xit")

        # self.Bind(wx.EVT_MENU, self.OnExit, menu_exit)

        # self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)

        # acceltbl = wx.AcceleratorTable([
        #     (wx.ACCEL_CTRL, ord('B'), menu_item1.GetId()),
        #     (wx.ACCEL_CTRL, ord('X'), menu_item2.GetId()),
        #     (wx.ACCEL_CTRL, ord('Q'), menu_quickmenu_setup.GetId()),
        #     (wx.ACCEL_CTRL, ord('T'), menu_timer_setup.GetId())
        #     ])
        # self.SetAcceleratorTable(acceltbl)

        # self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_item1)
        # self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_item2)
        # self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_quickmenu_setup)
        # self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_timer_setup)
        # # popup menu end

        self.middlePanel = MiddlePanel(self)
        self.appPanel = AppPanel(self)
#        button = wx.Button(self, label="Close")

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.appPanel, 0, wx.EXPAND)
        self.sizer.Add(wx.StaticLine(self), flag=wx.EXPAND)
        self.sizer.Add(self.middlePanel, 0, wx.EXPAND)
#        self.sizer.Add(button, 0, wx.ALIGN_CENTER)
#        button.Bind(wx.EVT_BUTTON, self.OnClose)

        self.SetSizerAndFit(self.sizer)

    def addApp(self):
        print("on add app ")
        self.appPanel.addApp()
        self.SetSizerAndFit(self.sizer)
        self.sizer.Layout()

    def OnCommand(self, event):
        print("mainframe add app")
        self.appPanel.addApp()
        self.SetSizerAndFit(self.sizer)
        self.sizer.Layout()
  

    def OnClose(self, event):
#        self.read_write_text(True)
        self.SysClose(event)

    def SysClose(self, event):
#        self.Destroy()
        self.Close()
        event.Skip()

    def OnShowPopup(self, event):
        pos = event.GetPosition()
        pos = self.ScreenToClient(pos)
        self.PopupMenu(self.popupmenu, pos)

    def OnPopupItemSelected(self, event):
        print("OnPopupItemSelected")
        #item = self.popupmenu.FindItemById(event.GetId())
        #print("select: %s" % item.GetText())
        print(event.GetId())
        id = event.GetId()
        if id == 2001:
            print("menu 1")
            pass
        elif id == 2002:
            print("menu 2")
            pass
        elif id == 2003:
            print("try to call quick menu setup")
            quickmenu_setup_frame = QuickMenuSetupFrame(self)
            quickmenu_setup_frame.Show(True)
        elif id == 2004:
            print("try to call timer setup")
            timer_setup_frame = TimerSetupFrame(self)
            timer_setup_frame.Show(True)

    def OnExit(self, event):
        print("OnExit, main_frame")
        #self.Close()
        self.Destroy()
        event.Skip()

class Frame(wx.Frame):
    """Frame class, main window."""
    def __init__(self):
        """Create a Frame instance"""
        wx.Frame.__init__(self, None, -1, "Auto Key", size=(900, 700))
        self.Centre()
#        self.panel = wx.Panel(self)
        self.autokey_timeout = int(Default_timeout * 60)
        self.shutdown_timeout = 0
        self.shutdown_or_restart = True
        self.autokey_state = False
        self.shutdown_state = False

        self.menudb = []
        self.quickmenufile = "quickmenu.txt"

        # popup menu start
        self.popupmenu = wx.Menu()

        menu_item1 = self.popupmenu.Append(2001, "&test1 menu\tCtrl-B")
        menu_item2 = self.popupmenu.Append(2002, "&test2 menu\tCtrl-X")
        menu_quickmenu_setup = self.popupmenu.Append(2003, "&QuickMenuSetup\tCtrl-Q")
        menu_timer_setup = self.popupmenu.Append(2004, "&TimerSetup\tCtrl-T")
        self.popupmenu.AppendSeparator()
        menu_exit = self.popupmenu.Append(-1, "E&xit")

        self.Bind(wx.EVT_MENU, self.OnExit, menu_exit)

        self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)

        acceltbl = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('B'), menu_item1.GetId()),
            (wx.ACCEL_CTRL, ord('X'), menu_item2.GetId()),
            (wx.ACCEL_CTRL, ord('Q'), menu_quickmenu_setup.GetId()),
            (wx.ACCEL_CTRL, ord('T'), menu_timer_setup.GetId())
            ])
        self.SetAcceleratorTable(acceltbl)

        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_item1)
        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_item2)
        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_quickmenu_setup)
        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_timer_setup)
        # popup menu end

        self.key_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnKeyTimer, self.key_timer)


        button_autokey = wx.Button(self.panel, label="AutoKey", size=(-1, 30))
        self.label_key_state = wx.StaticText(self.panel, -1, "Stop")
        self.text_key_time = wx.TextCtrl(self.panel, -1, "4", size=(150, -1))
        label_second = wx.StaticText(self.panel, -1, "m")

        button_app1 = wx.Button(self.panel, label="Outlook", size=(-1, 30))
        button_app2 = wx.Button(self.panel, label="SecureCRT", size=(-1, 30))
        button_app3 = wx.Button(self.panel, label="Firefox", size=(-1, 30))
        button_app4 = wx.Button(self.panel, label="Emacs", size=(-1, 30))

        button_shutdown = wx.Button(self.panel, label="Shutdown", size=(-1, 30))
        button_restart = wx.Button(self.panel, label="Restart", size=(-1, 30))
        self.text_shutdown_time = wx.TextCtrl(self.panel, -1, "0", size=(150, 30))
        label_units = wx.StaticText(self.panel, -1, "m/h")

        self.text_multi_text = wx.TextCtrl(self.panel, -1, "", size=(700, 500), style=wx.TE_MULTILINE)
        font=wx.Font(14, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        self.text_multi_text.SetFont(font)
        button_close = wx.Button(self.panel, label="Close", size=(-1, 30))

        self.vbox_top = wx.BoxSizer(wx.VERTICAL)

        vbox_grid = wx.FlexGridSizer(cols=4, hgap=5, vgap=5)
        vbox_grid.Add(button_autokey, 0, flag=wx.ALIGN_CENTER)
        vbox_grid.Add(self.label_key_state, 0, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER)
        vbox_grid.Add(self.text_key_time, 0, flag=wx.EXPAND|wx.ALL)
        vbox_grid.Add(label_second, 0, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER)

        vbox_grid.Add(button_app1, 0, flag=wx.ALIGN_CENTER)
        vbox_grid.Add(button_app2, 0, flag=wx.ALIGN_CENTER)
        vbox_grid.Add((15,15))
        vbox_grid.Add((15,15))
        vbox_grid.Add(button_app3, 0, flag=wx.ALIGN_CENTER)
        vbox_grid.Add(button_app4, 0, flag=wx.ALIGN_CENTER)
        vbox_grid.Add((15,15))
        vbox_grid.Add((15,15))

        vbox_grid.Add(button_shutdown, 0, flag=wx.ALIGN_CENTER)
        vbox_grid.Add(button_restart, 0, flag=wx.ALIGN_CENTER)
        vbox_grid.Add(self.text_shutdown_time, 0, flag=wx.ALIGN_RIGHT)
        vbox_grid.Add(label_units, 0, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER)

        self.vbox_top.Add(vbox_grid, 0, wx.ALIGN_CENTER)

        self.number_of_command = 0
        self.vbox_command = wx.BoxSizer(wx.VERTICAL)
        self.vbox_top.Add(self.vbox_command, 0, wx.ALIGN_CENTER)

        self.vbox_top.Add(self.text_multi_text, 0, wx.ALIGN_CENTER)
        self.vbox_top.Add(button_close, 0, wx.ALIGN_CENTER)

#        self.vbox_top.Hide(self.vbox_command)

        self.panel.SetSizer(self.vbox_top)

        self.Bind(wx.EVT_BUTTON, self.OnAutoKey, button_autokey)
        self.Bind(wx.EVT_BUTTON, self.OnShutdown, button_shutdown)
        self.Bind(wx.EVT_BUTTON, self.OnRestart, button_restart)
        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)
        self.Bind(wx.EVT_BUTTON, self.OnApp1, button_app1)
        self.Bind(wx.EVT_BUTTON, self.OnApp2, button_app2)
        self.Bind(wx.EVT_BUTTON, self.OnApp3, button_app3)
        self.Bind(wx.EVT_BUTTON, self.OnApp4, button_app4)
        
        self.execute_autokey_task()
        self.read_write_text(False)

    def OnAddCommand(self):
        self.quickmenu_read()
        for li in self.menudb:
            self.number_of_command += 1
            name = li[0]
            print(name)
            new_button = wx.Button(self, label=name, name=name)
            new_button.name = name
            self.vbox_command.Add(new_button, 0, wx.ALL, 5)
            new_button.Bind(wx.EVT_BUTTON, self.OnCommand)

#        self.SetSizerAndFit(self.vbox_command)
#        self.vbox_top.Show(self.vbox_command)
#        self.Layout()
#        self.Fit()
            #        self.frame.fSizer.Layout()

    def OnCommand(self, event):
        name = event.GetEventObject().name
        print(name)
        for li in self.menudb:
            if name == li[0]:
                print(name)
            else:
                print(("not " + name))

    def quickmenu_read(self):
        if os.path.isfile(self.quickmenufile):
            fd = open(self.quickmenufile, 'r')
            while True:
                line = fd.readline()
                if not line:
                    break
                line = line.strip()
                li = line.split("::")
                li = [str.strip() for str in li]
                if line[0] != '#':
                    self.menudb.append(li)
            fd.close()

    def read_write_text(self, Write = False):
        if (Write == False) and os.path.isfile(text_filename):
            fd = open(text_filename, 'r')
            while True:
                line = fd.readline()
                if not line:
                    break
                self.text_multi_text.AppendText(line)
            fd.close()
        if Write == True:
            self.text_multi_text.SaveFile(text_filename)

    def OnApp1(self, event):
        subprocess.Popen(app1_cmd, shell=True)

    def OnApp2(self, event):
        subprocess.Popen(app2_cmd, shell=True)

    def OnApp3(self, event):
        subprocess.Popen(app3_cmd, shell=True)

    def OnApp4(self, event):
        subprocess.Popen(app4_cmd, shell=True)

    def OnAutoKey(self, event):
        self.execute_autokey_task()

    def execute_autokey_task(self):
        # "start a task or stop a task"
        if (self.autokey_state == False):
            input_string = self.text_key_time.GetValue().strip()
            num = 0
            if input_string.isdigit():
                num = int(input_string)
                self.autokey_timeout = int(num * 5 * 1000)
                self.press_key()
                self.key_timer.Start(self.autokey_timeout)
                self.autokey_state = True
                self.label_key_state.SetLabel("Start")
                #self.text_multi_text.AppendText("auto key start\n")
        else:
            self.key_timer.Stop()
            self.autokey_state = False
            self.label_key_state.SetLabel("Stop")
            #self.text_multi_text.AppendText("auto key stop\n")

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
        self.OnAddCommand()
        #self.parse_shutdown_string()
        #cmd_shutdown = "shutdown /s -t " + str(self.shutdown_timeout)
        #self.text_multi_text.AppendText(cmd_shutdown + "\n")
        #os.system(cmd_shutdown)
        #self.SysClose(event)

    def OnRestart(self, event):
        #self.parse_shutdown_string()
        cmd_restart = "shutdown /r -t " + str(self.shutdown_timeout)
        #self.text_multi_text.AppendText(cmd_restart + "\n")
        #os.system(cmd_restart)
        #self.SysClose(event)

    def OnClose(self, event):
        self.read_write_text(True)
        self.SysClose(event)

    def SysClose(self, event):
        self.Destroy()
        event.Skip()

    def OnShowPopup(self, event):
        pos = event.GetPosition()
        pos = self.panel.ScreenToClient(pos)
        self.panel.PopupMenu(self.popupmenu, pos)

    def OnPopupItemSelected(self, event):
        print("OnPopupItemSelected")
        #item = self.popupmenu.FindItemById(event.GetId())
        #print("select: %s" % item.GetText())
        print(event.GetId())
        id = event.GetId()
        if id == 2001:
            print("menu 1")
            pass
        elif id == 2002:
            print("menu 2")
            pass
        elif id == 2003:
            print("try to call quick menu setup")
            quickmenu_setup_frame = QuickMenuSetupFrame()
            quickmenu_setup_frame.Show(True)
        elif id == 2004:
            print("try to call timer setup")
            timer_setup_frame = TimerSetupFrame()
            timer_setup_frame.Show(True)

    def OnExit(self, event):
        print("OnExit, main_frame")
        #self.Close()
        self.Destroy()
        event.Skip()

    def OnKeyTimer(self, event):
        self.press_key()

    def press_key(self):
        # 17, 144, Num Lock key
        pass


class QuickMenuSetupFrame(wx.Frame):
    """System Setup Frame class, sub window."""
    def __init__(self, frame):
        """Create a Frame instance"""
        wx.Frame.__init__(self, None, title="System Setup", size=(850, 650))
        self.Centre()
        print(self.GetSize())

        self.main_frame= frame
        panel = wx.Panel(self)

        self.menudb = []
        self.quickmenufile = "quickmenu.txt"
        self.listboxChanged = False

        label_title = wx.StaticText(panel, -1, "Quick Menu Setup")

#        self.listbox = wx.ListBox(panel, -1, (20, 20), (220, 360), "", wx.LB_EXTENDED)
        self.listbox = wx.ListBox(panel, -1, (20, 20), (220, 360), "", wx.LB_SINGLE)
        list_up = wx.Button(panel, -1, label=_("Up"))
        list_down = wx.Button(panel, -1, label=_("Down"))
        list_delete = wx.Button(panel, -1, label=_("Delete"))

        self.cmd_name = wx.TextCtrl(panel, 0, "", size=(100, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
        self.cmd_command = wx.TextCtrl(panel, 0, "", size=(230, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
        self.cmd_parameter = wx.TextCtrl(panel, 0, "", size=(100, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
        cmd_add = wx.Button(panel, -1, label=_("Add"))
        cmd_clear = wx.Button(panel, -1, label=_("Clear"))
        cmd_close = wx.Button(panel, -1, label=_("Close"))

        # start layout
        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_list = wx.BoxSizer(wx.HORIZONTAL)
        vbox_list_cmd = wx.BoxSizer(wx.VERTICAL)
        vbox_list_cmd.Add(list_up, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15,15))
        vbox_list_cmd.Add(list_down, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15,15))
        vbox_list_cmd.Add(list_delete, 0, flag=wx.ALIGN_CENTER)
        vbox_list.Add(self.listbox, 0, flag=wx.ALIGN_CENTER)
        vbox_list.Add((15,15))
        vbox_list.Add(vbox_list_cmd, 0, flag=wx.ALIGN_CENTER)
        vbox_add_content = wx.BoxSizer(wx.HORIZONTAL)
        vbox_add_content.Add(self.cmd_name, 0, flag=wx.ALIGN_CENTER)
        vbox_add_content.Add((15,15))
        vbox_add_content.Add(self.cmd_command, 0, flag=wx.ALIGN_CENTER)
        vbox_add_content.Add((15,15))
        vbox_add_content.Add(self.cmd_parameter, 0, flag=wx.ALIGN_CENTER)
        vbox_add_cmd = wx.BoxSizer(wx.HORIZONTAL)
        vbox_add_cmd.Add(cmd_add, 0, flag=wx.ALIGN_CENTER)
        vbox_add_cmd.Add((15,15))
        vbox_add_cmd.Add(cmd_clear, 0, flag=wx.ALIGN_CENTER)
        vbox_add_cmd.Add((15,15))
        vbox_add_cmd.Add(cmd_close, 0, flag=wx.ALIGN_CENTER)

        vbox_top.Add((15,15))
        vbox_top.Add(label_title, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(wx.StaticLine(panel), flag=wx.EXPAND)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_list, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_add_content, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_add_cmd, 0, wx.ALIGN_CENTER)

        #Start Fit
        panel.SetSizer(vbox_top)

        #        self.Bind(wx.EVT_LISTBOX, self.OnListBox, self.listbox)
        #       self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnDclickListBox, self.listbox)
        self.Bind(wx.EVT_LISTBOX, self.OnListBox, self.listbox)
        self.Bind(wx.EVT_BUTTON, self.OnListUp, list_up)
        self.Bind(wx.EVT_BUTTON, self.OnListDown, list_down)
        self.Bind(wx.EVT_BUTTON, self.OnListDelete, list_delete)
        self.Bind(wx.EVT_BUTTON, self.OnCmdAdd, cmd_add)
        self.Bind(wx.EVT_BUTTON, self.OnCmdClear, cmd_clear)
        self.Bind(wx.EVT_BUTTON, self.OnCmdClose, cmd_close)
        self.quickmenu_read_write()

    def quickmenu_read_write(self, Write = False):
        if (Write == False) and os.path.isfile(self.quickmenufile):
            fd = open(self.quickmenufile, 'r')
            self.listbox.Clear()
            del self.menudb[:]
            while True:
                line = fd.readline()
                if not line:
                    break
                line = line.strip()
                li = line.split("::")
                li = [str.strip() for str in li]
                if line[0] != '#':
                    self.menudb.append(li)
                    self.listbox.Append(li[0])
                    # self.text_multi_text.AppendText(line)
            self.listbox.SetSelection(0)
            fd.close()
        if Write == True:
            fd = open(self.quickmenufile, 'w')
            currtime = "#quickmenu write at " + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n"
            fd.write(currtime)
            for li in self.menudb:
                line = "::".join(ele for ele in li) + "\n"
                fd.write(line)
            fd.close()
            #self.text_multi_text.SaveFile(quickmenu_filename)

    def OnListBox(self, event):
        pass

    def OnListUp(self, event):
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        if log:
            print("-----------------------")
        if (total > 0) and (select > 0):
            name1 = self.listbox.GetString(select -1)
            name2 = self.listbox.GetString(select)
            self.listbox.SetString(select-1, name2)
            self.listbox.SetString(select, name1)
            self.menudb[select-1], self.menudb[select] = self.menudb[select], self.menudb[select-1]
            self.listbox.SetSelection(select-1)
            self.listboxChanged = True
        if log:
            for li in self.menudb:
                print(li)

    def OnListDown(self, event):
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        if log:
            print("==================")
        if (total > 0)  and (select < total - 1):
            name1 = self.listbox.GetString(select )
            name2 = self.listbox.GetString(select+1)
            self.listbox.SetString(select, name2)
            self.listbox.SetString(select+1, name1)
            self.menudb[select], self.menudb[select+1] = self.menudb[select+1], self.menudb[select]
            self.listbox.SetSelection(select+1)
            self.listboxChanged = True
        if log:
            for li in self.menudb:
                print(li)

    def OnListDelete(self, event):
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        if (total > 0)  and (select < total):
            self.listbox.Delete(select)
            del self.menudb[select]
            self.listboxChanged = True

        if log:
            for li in self.menudb:
                print(li)

    def OnCmdAdd(self, event):
        name = self.cmd_name.GetValue()
        command = self.cmd_command.GetValue()
        parameter = self.cmd_parameter.GetValue()
        if [name, command, parameter] not in self.menudb:
            self.menudb.append([name, command, parameter])
            self.listbox.Append(name)
            self.cmd_name.SetValue("")
            self.cmd_command.SetValue("")
            self.cmd_parameter.SetValue("")
            self.listboxChanged = True
        else:
            print("command duplication errors")

        pass

    def OnCmdClear(self, event):
        self.cmd_name.SetValue("")
        self.cmd_command.SetValue("")
        self.cmd_parameter.SetValue("")

#      self.quickmenu_read_write()
#      self.text_multi_text.SetValue(dbfamous.famous_list_get_text_by_index(self.current_item).decode("utf-8"))
#      self.text_multi_text.SetValue("")


    def OnCmdClose(self, event):
        if self.listboxChanged:
            print("changed and save")
            self.quickmenu_read_write(True)
            self.main_frame.addApp()

        self.Destroy()
        event.Skip()

class TimerSetupFrame(wx.Frame):
    """System Setup Frame class, sub window."""
    def __init__(self, frame):
        """Create a Frame instance"""
        wx.Frame.__init__(self, None, title="System Setup", size=(850, 650))
        #self.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)
        self.Centre()
        print(self.GetSize())

        self.main_frame= frame
        panel = wx.Panel(self)

        self.timerdb = []
        self.quickmenufile = "quickmenu.txt"
        self.listboxChanged = False

        label_title = wx.StaticText(panel, -1, "Timer Setup")

#        self.listbox = wx.ListBox(panel, -1, (20, 20), (220, 360), "", wx.LB_SINGLE)
        self.listbox = wx.ListBox(panel, -1, (20, 20), (220, 360), "", wx.LB_SINGLE)
        list_up = wx.Button(panel, -1, label=_("Up"))
        list_down = wx.Button(panel, -1, label=_("Down"))
        list_delete = wx.Button(panel, -1, label=_("Delete"))

#        self.cmd_name = wx.TextCtrl(panel, 0, "", size=(100, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
#        self.cmd_command = wx.TextCtrl(panel, 0, "", size=(230, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
#        self.cmd_parameter = wx.TextCtrl(panel, 0, "", size=(100, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);

        self.timer_name = wx.TextCtrl(panel, 0, "", size=(100, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
        self.timer_message = wx.TextCtrl(panel, 0, "", size=(230, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
        self.timer_timeout = wx.TextCtrl(panel, 0, "", size=(100, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
        self.timer_loop_times = wx.TextCtrl(panel, 0, "", size=(100, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
        self.timer_enable = wx.CheckBox(panel, 0, "Enable");

        cmd_add = wx.Button(panel, -1, label=_("Add"))
        cmd_clear = wx.Button(panel, -1, label=_("Clear"))
        cmd_update = wx.Button(panel, -1, label=_("Update"))
        cmd_close = wx.Button(panel, -1, label=_("Close"))

        # start layout
        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_list = wx.BoxSizer(wx.HORIZONTAL)
        vbox_list_cmd = wx.BoxSizer(wx.VERTICAL)
        vbox_list_cmd.Add(list_up, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15,15))
        vbox_list_cmd.Add(list_down, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15,15))
        vbox_list_cmd.Add(list_delete, 0, flag=wx.ALIGN_CENTER)
        vbox_list.Add(self.listbox, 0, flag=wx.ALIGN_CENTER)
        vbox_list.Add((15,15))
        vbox_list.Add(vbox_list_cmd, 0, flag=wx.ALIGN_CENTER)

        vbox_add_content1 = wx.BoxSizer(wx.HORIZONTAL)
        vbox_add_content1.Add(self.timer_name, 0, flag=wx.ALIGN_CENTER)
        vbox_add_content1.Add((15,15))
        vbox_add_content1.Add(self.timer_message, 0, flag=wx.ALIGN_CENTER)

        vbox_add_content2 = wx.BoxSizer(wx.HORIZONTAL)
        vbox_add_content2.Add(self.timer_timeout, 0, flag=wx.ALIGN_CENTER)
        vbox_add_content2.Add((15,15))
        vbox_add_content2.Add(self.timer_loop_times, 0, flag=wx.ALIGN_CENTER)
        vbox_add_content2.Add((15,15))
        vbox_add_content2.Add(self.timer_enable, 0, flag=wx.ALIGN_CENTER)

        vbox_add_cmd = wx.BoxSizer(wx.HORIZONTAL)
        vbox_add_cmd.Add(cmd_add, 0, flag=wx.ALIGN_CENTER)
        vbox_add_cmd.Add((15,15))
        vbox_add_cmd.Add(cmd_clear, 0, flag=wx.ALIGN_CENTER)
        vbox_add_cmd.Add((15,15))
        vbox_add_cmd.Add(cmd_update, 0, flag=wx.ALIGN_CENTER)
        vbox_add_cmd.Add((15,15))
        vbox_add_cmd.Add(cmd_close, 0, flag=wx.ALIGN_CENTER)

        vbox_top.Add((15,15))
        vbox_top.Add(label_title, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(wx.StaticLine(panel), flag=wx.EXPAND)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_list, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_add_content1, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_add_content2, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_add_cmd, 0, wx.ALIGN_CENTER)

        #Start Fit
        panel.SetSizer(vbox_top)

        self.Bind(wx.EVT_LISTBOX, self.OnListBox, self.listbox)
        self.Bind(wx.EVT_BUTTON, self.OnListUp, list_up)
        self.Bind(wx.EVT_BUTTON, self.OnListDown, list_down)
        self.Bind(wx.EVT_BUTTON, self.OnListDelete, list_delete)
        self.Bind(wx.EVT_BUTTON, self.OnCmdAdd, cmd_add)
        self.Bind(wx.EVT_BUTTON, self.OnCmdClear, cmd_clear)
        self.Bind(wx.EVT_BUTTON, self.OnCmdClose, cmd_close)


    def OnListBox(self, event):
        pass

    def OnListUp(self, event):
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        if log:
            print("-----------------------")
        if (total > 0) and (select > 0):
            name1 = self.listbox.GetString(select -1)
            name2 = self.listbox.GetString(select)
            self.listbox.SetString(select-1, name2)
            self.listbox.SetString(select, name1)
            self.menudb[select-1], self.menudb[select] = self.menudb[select], self.menudb[select-1]
            self.listbox.SetSelection(select-1)
            self.listboxChanged = True
        if log:
            for li in self.menudb:
                print(li)

    def OnListDown(self, event):
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        if log:
            print("==================")
        if (total > 0)  and (select < total - 1):
            name1 = self.listbox.GetString(select )
            name2 = self.listbox.GetString(select+1)
            self.listbox.SetString(select, name2)
            self.listbox.SetString(select+1, name1)
            self.menudb[select], self.menudb[select+1] = self.menudb[select+1], self.menudb[select]
            self.listbox.SetSelection(select+1)
            self.listboxChanged = True
        if log:
            for li in self.menudb:
                print(li)

    def OnListDelete(self, event):
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        if (total > 0)  and (select < total):
            self.listbox.Delete(select)
            del self.menudb[select]
            self.listboxChanged = True

        if log:
            for li in self.menudb:
                print(li)

    def OnCmdAdd(self, event):
        name = self.timer_name.GetValue()
        message = self.timer_message.GetValue()
        timeout = self.timer_timeout.GetValue()
        loop_times = self.timer_loop_times.GetValue()
        enable = self.timer_enable.GetValue()
        
        if True:
#        if [name, command, parameter] not in self.menudb:
#            self.menudb.append([name, command, parameter])
            self.listbox.Append(name)

            self.timer_name.SetValue("")
            self.timer_message.SetValue("")
            self.timer_timeout.SetValue("")
            self.timer_loop_times.SetValue("")
            self.timer_enable.SetValue(False)
            self.listboxChanged = True
        else:
            print("command duplication errors")

    def OnCmdClear(self, event):
        self.cmd_name.SetValue("")
        self.cmd_command.SetValue("")
        self.cmd_parameter.SetValue("")

    def OnCmdClose(self, event):
        if self.listboxChanged:
            print("changed and save")
            #self.quickmenu_read_write(True)
            #self.main_frame.addApp()

        self.Destroy()
        event.Skip()

class SystemPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.menudb = []
        self.quickmenufile = "quickmenu.txt"
        self.listboxChanged = False

        label_title = wx.StaticText(self, -1, "Quick Menu Setup")

        # self.listbox = wx.ListBox(self, -1, (20, 20), (220, 360), "", wx.LB_EXTENDED)
        self.listbox = wx.ListBox(self, -1, (20, 20), (220, 360), "", wx.LB_SINGLE)
        list_up = wx.Button(self, -1, label=_("Up"))
        list_down = wx.Button(self, -1, label=_("Down"))
        list_delete = wx.Button(self, -1, label=_("Delete"))

        label_cmd_name = wx.StaticText(self, -1, ("Name"))
        label_cmd_command = wx.StaticText(self, -1, ("Command"))
        label_cmd_parameter = wx.StaticText(self, -1, ("Parameter"))
        self.cmd_name = wx.TextCtrl(self, 0, "", size=(100, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
        self.cmd_command = wx.TextCtrl(self, 0, "", size=(300, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
        self.cmd_parameter = wx.TextCtrl(self, 0, "", size=(100, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
        cmd_add = wx.Button(self, -1, label=_("Add"))
        cmd_clear = wx.Button(self, -1, label=_("Clear"))
        cmd_close = wx.Button(self, -1, label=_("Close"))

        # start layout
        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_list = wx.BoxSizer(wx.HORIZONTAL)
        vbox_list_cmd = wx.BoxSizer(wx.VERTICAL)
        vbox_list_cmd.Add(list_up, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15,15))
        vbox_list_cmd.Add(list_down, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15,15))
        vbox_list_cmd.Add(list_delete, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15,15))
        vbox_list_cmd.Add((15,15))
        vbox_list_cmd.Add(cmd_add, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15,15))
        vbox_list_cmd.Add(cmd_clear, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15,15))

        vbox_add_content = wx.BoxSizer(wx.VERTICAL)
        vbox_add_content.Add(label_cmd_name, flag=wx.ALIGN_LEFT)
        vbox_add_content.Add(self.cmd_name, flag=wx.ALIGN_LEFT)
        vbox_add_content.Add((10,10))
        vbox_add_content.Add(label_cmd_command, flag=wx.ALIGN_LEFT)
        vbox_add_content.Add(self.cmd_command, flag=wx.ALIGN_LEFT)
        vbox_add_content.Add((10,10))
        vbox_add_content.Add(label_cmd_parameter, flag=wx.ALIGN_LEFT)
        vbox_add_content.Add(self.cmd_parameter, flag=wx.ALIGN_LEFT)

        vbox_list.Add(self.listbox, 0, flag=wx.ALIGN_CENTER)
        vbox_list.Add((15,15))
        vbox_list.Add(vbox_list_cmd, 0, flag=wx.ALIGN_CENTER)
        vbox_list.Add((15,15))
        vbox_list.Add(vbox_add_content, 0, flag=wx.ALIGN_TOP)

        # vbox_add_content.Add(self.cmd_name, 0, flag=wx.ALIGN_CENTER)
        # vbox_add_content.Add((15,15))
        # vbox_add_content.Add(self.cmd_command, 0, flag=wx.ALIGN_CENTER)
        # vbox_add_content.Add((15,15))
        # vbox_add_content.Add(self.cmd_parameter, 0, flag=wx.ALIGN_CENTER)
        vbox_cmd = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd.Add(cmd_close, 0, flag=wx.ALIGN_CENTER)

        vbox_top.Add((15,15))
        vbox_top.Add(label_title, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_list, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        # vbox_top.Add(vbox_add_content, 0, wx.ALIGN_CENTER)
        # vbox_top.Add((15,15))
        vbox_top.Add(vbox_cmd, 0, wx.ALIGN_CENTER)

        #Start Fit
        self.SetSizer(vbox_top)

        #        self.Bind(wx.EVT_LISTBOX, self.OnListBox, self.listbox)
        #       self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnDclickListBox, self.listbox)
        self.Bind(wx.EVT_LISTBOX, self.OnListBox, self.listbox)
        self.Bind(wx.EVT_BUTTON, self.OnListUp, list_up)
        self.Bind(wx.EVT_BUTTON, self.OnListDown, list_down)
        self.Bind(wx.EVT_BUTTON, self.OnListDelete, list_delete)
        self.Bind(wx.EVT_BUTTON, self.OnCmdAdd, cmd_add)
        self.Bind(wx.EVT_BUTTON, self.OnCmdClear, cmd_clear)
        self.Bind(wx.EVT_BUTTON, self.OnCmdClose, cmd_close)
        self.quickmenu_read_write()

    def quickmenu_read_write(self, Write = False):
        if (Write == False) and os.path.isfile(self.quickmenufile):
            fd = open(self.quickmenufile, 'r')
            self.listbox.Clear()
            del self.menudb[:]
            while True:
                line = fd.readline()
                if not line:
                    break
                line = line.strip()
                li = line.split("::")
                li = [str.strip() for str in li]
                if line[0] != '#':
                    self.menudb.append(li)
                    self.listbox.Append(li[0])
                    # self.text_multi_text.AppendText(line)
            self.listbox.SetSelection(0)
            fd.close()
        if Write == True:
            fd = open(self.quickmenufile, 'w')
            currtime = "#quickmenu write at " + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n"
            fd.write(currtime)
            for li in self.menudb:
                line = "::".join(ele for ele in li) + "\n"
                fd.write(line)
            fd.close()
            #self.text_multi_text.SaveFile(quickmenu_filename)

    def OnListBox(self, event):
        pass

    def OnListUp(self, event):
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        if log:
            print("-----------------------")
        if (total > 0) and (select > 0):
            name1 = self.listbox.GetString(select -1)
            name2 = self.listbox.GetString(select)
            self.listbox.SetString(select-1, name2)
            self.listbox.SetString(select, name1)
            self.menudb[select-1], self.menudb[select] = self.menudb[select], self.menudb[select-1]
            self.listbox.SetSelection(select-1)
            self.listboxChanged = True
        if log:
            for li in self.menudb:
                print(li)

    def OnListDown(self, event):
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        if log:
            print("==================")
        if (total > 0)  and (select < total - 1):
            name1 = self.listbox.GetString(select )
            name2 = self.listbox.GetString(select+1)
            self.listbox.SetString(select, name2)
            self.listbox.SetString(select+1, name1)
            self.menudb[select], self.menudb[select+1] = self.menudb[select+1], self.menudb[select]
            self.listbox.SetSelection(select+1)
            self.listboxChanged = True
        if log:
            for li in self.menudb:
                print(li)

    def OnListDelete(self, event):
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        if (total > 0)  and (select < total):
            self.listbox.Delete(select)
            del self.menudb[select]
            self.listboxChanged = True

        if log:
            for li in self.menudb:
                print(li)

    def OnCmdAdd(self, event):
        name = self.cmd_name.GetValue()
        command = self.cmd_command.GetValue()
        parameter = self.cmd_parameter.GetValue()
        if [name, command, parameter] not in self.menudb:
            self.menudb.append([name, command, parameter])
            self.listbox.Append(name)
            self.cmd_name.SetValue("")
            self.cmd_command.SetValue("")
            self.cmd_parameter.SetValue("")
            self.listboxChanged = True
        else:
            print("command duplication errors")

        pass

    def OnCmdClear(self, event):
        self.cmd_name.SetValue("")
        self.cmd_command.SetValue("")
        self.cmd_parameter.SetValue("")

#      self.quickmenu_read_write()
#      self.text_multi_text.SetValue(dbfamous.famous_list_get_text_by_index(self.current_item).decode("utf-8"))
#      self.text_multi_text.SetValue("")


    def OnCmdClose(self, event):
        # if self.listboxChanged:
        #     print("changed and save")
        #     # self.quickmenu_read_write(True)
        #     # self.main_frame.addApp()
        self.GetTopLevelParent().Destroy()
        # self.Destroy()
        event.Skip()

class FamousSetupPage(wx.Panel):
    """famous working"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.famous_file = "menudoc/famous.txt"

        # self.SetBackgroundColour(dbimages.sys_color)
        # label_title.SetFont(dbimages.sys_font)
        self.text_multi_text = wx.TextCtrl(self, -1, "", size=(700, 550), style=wx.TE_MULTILINE)
        self.text_multi_text.SetFont(dbmenus.big_font)
        button_close = wx.Button(self, -1, label=_("Close"))

        vbox_cmd = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd.Add(button_close, 0, wx.ALIGN_CENTER)

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_top.Add((15,15))
        vbox_top.Add(self.text_multi_text, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_cmd, 0, flag=wx.ALIGN_CENTER)
        vbox_top.Add((15,15))

        self.SetSizer(vbox_top)
        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)

    def OnClose(self, event):
        self.GetTopLevelParent().Destroy()

class HelpInfoPage(wx.Panel):
    def __init__(self, parent):
        self.current_item = 0;
        self.total_item = 0;
        wx.Panel.__init__(self, parent)
        return
        self.SetBackgroundColour(dbmenus.sys_color)
        # if dbimages.current["lang"] == "English":
        #     self.help_file = os.path.join(dbimages.basepath, "doc/en/help.txt")
        # else:
        #     self.help_file = os.path.join(dbimages.basepath, "doc/zh/help.txt")

        button_close = wx.Button(self, -1, label=_("Close"))

        label_title = wx.StaticText(self, -1, _("Help Info"))
        label_title.SetFont(dbmenus.sys_font)
        self.text_multi_text = wx.TextCtrl(self, -1, "", size=(500, 450), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.text_multi_text.SetFont(dbmenus.sys_font)

        self.tree = wx.TreeCtrl(self, -1, size=(200, 450), style=wx.TR_HAS_BUTTONS|wx.TR_DEFAULT_STYLE|wx.SUNKEN_BORDER)
        root = self.tree.AddRoot(_("Help"))
        self.__AddTreeNodes(root)
        self.tree.Expand(root)

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_win = wx.BoxSizer(wx.HORIZONTAL)

        vbox_win.Add(self.tree, 0, wx.ALIGN_LEFT)
        vbox_win.Add((15,15))
        vbox_win.Add(self.text_multi_text, 0, wx.ALIGN_LEFT)

        vbox_top.Add((15,15))
        vbox_top.Add(label_title, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_win, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_top.Add((15,15))
        vbox_top.Add(button_close, 0, wx.ALIGN_CENTER)

        self.SetSizer(vbox_top)
        vbox_top.Fit(self)

        # map event
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)
        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)

    def OnClose(self, event):
        self.GetTopLevelParent().Destroy()

    def __AddTreeNodes(self, parentItem):
        self.tree.AppendItem(parentItem, "Main Window")
        self.tree.AppendItem(parentItem, "Merge Window")
        self.tree.AppendItem(parentItem, "View Window")
        self.tree.AppendItem(parentItem, "Setup Window")

        help_info = self.help_file_get_text_by_index(1)
        self.text_multi_text.SetValue(help_info)

    def OnSelChanged(self, event):
        help_info = ""
        text = self.tree.GetItemText(event.GetItem())
        if text == "Main Window":
            help_info = self.help_file_get_text_by_index(2)
        elif text == "Merge Window":
            help_info = self.help_file_get_text_by_index(3)
        elif text == "View Window":
            help_info = self.help_file_get_text_by_index(4)
        elif text == "Setup Window":
            help_info = self.help_file_get_text_by_index(5)
        else:
            help_info = self.help_file_get_text_by_index(1)
            pass

        self.text_multi_text.SetValue(help_info)

    def parse_help_file_header(self):
        fd = open(self.help_file, 'r')
        found_header = False
        while True:
            line = fd.readline()
            if not line:
                break
            if (line.find(FILE_HEADER_TAG) != -1):
                found_header = True
                continue
            if (line.find("totals") != -1):
                li = line.strip().split("=")
                val = int(li[1])
                DBfamous.famous_total_item = val

    def help_file_get_text_by_index(self, index):
        help_text = ""
        if (index < 1):
            return help_text
        fd = codecs.open(self.help_file, mode='r', encoding="utf-8")
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
        
        help_text = help_text.decode("utf-8")
        return help_text;

class UpdatePage(wx.Panel):
    """this software auto update"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(dbmenus.sys_color)
        self.update_path = "update"
        self.version = "1.0"
        self.web_version= "1.0"
        return
        self.version_file=os.path.join(dbmenus.basepath, "version.txt")
        self.url_info = "http://face2group.com/software/newimages/newimages.html"
        # self.url_info = "http://127.0.0.1/software/newimages/newimages.html"
        self.update_url = ""
        self.update_program = ""
        self.platform = ""
        self.enable_update = False

        label_title = wx.StaticText(self, -1, _("Update Online"))
        label_title.SetFont(dbmenus.sys_font)
        label_current = wx.StaticText(self, -1, _("Current version:"), size=(120, -1))
        self.text_current_version = wx.TextCtrl(self, -1, "", size=(120, -1))
        label_new = wx.StaticText(self, -1, _("New version:"), size=(120, -1))
        self.text_new_version = wx.TextCtrl(self, -1, "", size=(120, -1))
        label_features = wx.StaticText(self, -1, _("Features:"), size=(80, -1))
        self.text_features = wx.TextCtrl(self, -1, "", size=(350, 300), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.text_features.SetFont(dbmenus.sys_font)
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

        vbox_top.Add((15,15))
        vbox_top.Add(label_title, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_grid, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_features, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_updatefile, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_cmd, 0, wx.ALIGN_CENTER)

        self.SetSizer(vbox_top)
        vbox_top.Fit(self)

        self.get_local_version_info()

        self.Bind(wx.EVT_BUTTON, self.OnUpdate, self.button_update)
        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)

    def OnClose(self, event):
        self.GetTopLevelParent().Destroy()

    def OnUpdate(self, event):
        print("update: " + os.getcwd())
        if self.enable_update == False:
            self.get_new_version_info()
            return

        # download and unextact files, then close main program and start update program; copy files and start main program, then close update program.
        if not os.path.isdir(self.update_path):
            os.mkdir(self.update_path)
        os.chdir(self.update_path)
        self.get_url_file(self.update_url)
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
        cmd = self.update_program + " newimages"
        subprocess.Popen(cmd)

        # if sys.platform == "win32":
        #     shutil.copy("update.exe", "../")
        #     os.chdir("../")
        #     os.system("update.exe newimages")
        # elif sys.platform == "darwin":
        #     shutil.copy("update.dmp", "../")
        #     os.chdir("../")
        #     os.system("update.dmg newimages")
        # else:
        #     shutil.copy("update.py", "../")
        #     os.chdir("../")
        #     os.system("python update.py newimages")


    def get_local_version_info(self):
        # get local version
        try:
            fd = open(self.version_file, 'r')
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

    def get_url_file(self, url):
        filename = os.path.basename(url)
        try:
            u = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            # print e.fp.read()
            return

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
        # self.text_url_update.SetValue(self.url_update)

    def update_extract(self, filename):
        # print "try to extract zip file"
        # os.chdir("update")
        print("update extract: " + os.getcwd())
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

class AboutPage(wx.Panel):
    """this software auto update"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(dbmenus.sys_color)
        return
        # if dbmenus.current["lang"] == "English":
        #     self.about_file = os.path.join(dbmenus.basepath, "doc/en/about.txt")
        # else:
        #     self.about_file = os.path.join(dbmenus.basepath, "doc/zh/about.txt")

        label_title = wx.StaticText(self, -1, _("About NewImages"))
        label_title.SetFont(dbmenus.sys_font)
        alipay = wx.StaticText(self, -1, "支付宝: luckrill@163.com", size=(500, -1))
        paypal = wx.StaticText(self, -1, "PayPal: luckrill@163.com", size=(500, -1))
        email = wx.StaticText(self, -1, " Email: luckrill@163.com", size=(500, -1))
        self.text_about = wx.TextCtrl(self, -1, "", size=(500, 400), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.text_about.SetFont(dbmenus.sys_font)
        button_close = wx.Button(self, -1, label=_("Close"))

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_top.Add((15,15))
        vbox_top.Add(label_title, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add((15,15))
        vbox_top.Add(alipay, 0, wx.ALIGN_CENTER)
        vbox_top.Add(paypal, 0, wx.ALIGN_CENTER)
        vbox_top.Add(email, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(self.text_about, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(button_close, 0, wx.ALIGN_CENTER)

        self.SetSizer(vbox_top)
        vbox_top.Fit(self)

        self.__get_about_info()

        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)

    def OnClose(self, event):
        self.GetTopLevelParent().Destroy()

    def __get_about_info(self):

        try:
            fd = open(self.about_file, 'r')
        except IOError:
            # print("file: " + self.about_file + " no exist!")
            return False
        for line in fd:
            self.text_about.AppendText(line.decode("utf-8"))
        fd.close()


class SystemSetupFrame(wx.Frame):
    """System Setup Frame class, sub window."""
    def __init__(self, mainframe):
        """Create a Frame instance"""
        wx.Frame.__init__(self, None, title=_("System Setup"), size=(850, 650))
        # self.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)
        self.Centre()

        self.main_frame = mainframe
        self.current_index = 0

        panel = wx.Panel(self, size=self.GetSize())

        self.nb = wx.Notebook(panel)
        self.system_page = SystemPage(self.nb)
        self.famous_page = FamousSetupPage(self.nb)
        self.helpinfo_page = HelpInfoPage(self.nb)
        self.update_page = UpdatePage(self.nb)
        about_page = AboutPage(self.nb)


        self.nb.AddPage(self.system_page, _("System Setup"))
        self.nb.AddPage(self.famous_page, _("Famous Setup"))
        self.nb.AddPage(self.helpinfo_page, _("Help Info"))
        self.nb.AddPage(self.update_page, _("Update"))
        self.nb.AddPage(about_page, _("About"))

        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        #sizer.Fit(self)

        self.nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnChanged)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnChanged(self, event):
        # 0 -- 4, 5 items
        pass
        # if self.current_index == 0:
        #     self.system_page.SaveUIData()
        # self.current_index = self.nb.GetSelection()
        # # print "index:" + str(index) + "; total items: " + str(dbfamous.famous_total_item)
        # if self.current_index == 1 and self.famous_page.famous_get_data == False:
        #     self.famous_page.FirstStart()
        #     self.famous_page.famous_get_data = True
        #     pass

    def OnClose(self, event):
        # print "note on close !?"
        self.GetTopLevelParent().Destroy()

dbmenus = DBmenus()

class App(wx.App):
    """Application class."""
    def OnInit(self):
        self.frame = MainFrame()
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True

def main():
    app = App()
    app.MainLoop()

if __name__ == '__main__':
    main()
