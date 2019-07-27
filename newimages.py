#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import wx.lib.scrolledpanel as scrolled
import os
import sys
import shutil
import codecs
import random
import gettext
import zipfile
import urllib.request, urllib.error, urllib.parse
import subprocess 
import importlib

importlib.reload(sys)
sys.setdefaultencoding("utf-8")

L = wx.Locale()
_ = wx.GetTranslation

def anyTrue(predicate, sequence):
    return True in list(map(predicate, sequence))

exts = [".jpeg", ".jpg", ".bmp", ".gif", ".png", ".JPEG", ".JPG", "PNG", ".BMP", ".GIF", ".tif", ".TIF"]
imagedatatype = {"input_dir_path":1, "out_dir_path":2, "current_filename":3}

BAD_IMAGE = -1

IMAGEFRAME_IMAGE_NORMAL_MODE = 1
IMAGEFRAME_IMAGE_ZOOM_MODE = 2
IMAGEFRAME_IMAGE_QUICK_ZOOM_MODE = 3
IMAGEFRAME_IMAGE_ROTATE_MODE = 4

IMAGE_ALL_LIST_MODE = 2
IMAGE_LIST_VIEW_MODE = 3
IMAGE_SLIDER_SHOW_MODE = 4
IMAGE_SELECT_MERGER_MODE = 5

STATE_MAIN_LIST_TEXT_MODE = 1
STATE_MAIN_LIST_SELECT_MODE = 1
STATE_MAIN_LIST_CHANGEING_MODE = 1


# next, need include in class
default_lang = "English"
default_photo_format = "jpg"
default_text_width = 1024
default_text_height = 1024
default_slide_time = 3
default_open_help = 1

FAMOUS_STATE_NORMAL = 1
FAMOUS_STATE_ADD = 2
FAMOUS_STATE_DELETE = 3

FILE_HEADER_TAG = "<@>header<@>"
FILE_CONTENT_TAG = "<@>content<@>"
CONTENT_ITEM_TAG = "@__file_content_item__@"

FILE_STATE_NORMAL = 1
FILE_STATE_SELECT = 2
# FILE_STATE_COPYTO = 3

def check_path():
    basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
    config_file = os.path.join(basepath, "pdoc", "doc", "Config")
    try:
        open(config_file, 'a+')
    except IOError as e:
        # app_path = os.environ['APPDATA']
        app_path = os.environ['PROGRAMDATA']
        root_newimages = app_path+os.sep+"newimages"
        if not os.path.exists(root_newimages):
            os.mkdir(root_newimages)
        if not os.path.exists(root_newimages+os.sep+"doc"):
            shutil.copytree(basepath+os.sep+"doc", root_newimages+os.sep+"doc")
            shutil.copytree(basepath+os.sep+"locale", root_newimages+os.sep+"locale")
        basepath = root_newimages

    return basepath

def working_reset_mode():
    dbimages.global_working_mode = IMAGE_ALL_LIST_MODE

def working_set_mode(mode):
    dbimages.global_working_mode = mode

def working_get_mode():
    return dbimages.global_working_mode

class ImageDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, info, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE,
            ):

        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)
        pre.CentreOnParent()
        self.PostCreate(pre)

        label = wx.StaticText(self, -1, info)
        label.SetFont(dbimages.sys_font)
        self.checkbox = wx.CheckBox(self, -1, _("Please don't remind again"))
        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((15,15))
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add((15,15))
        sizer.Add(self.checkbox,0, wx.ALIGN_CENTER|wx.ALL, 5)
        sizer.Add((15,15))
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        self.Layout()
        sizer.Fit(self)

    def GetValue(self):
        return self.checkbox.GetValue()

class DBfamous():
    famous_current_item = 0
    famous_total_item = 0
    famous_list = []
    famous_data_changed = True

    def __init__(self):
        #self.famous_filename = os.path.join(dbimages.basepath_doc, "famous.txt")
        pass

    def parse_famous_file_header(self):
        fd = open(dbimages.famous_file, 'r')
        found_header = False
        while True:
            line = fd.readline()
            if not line:
                break
            if (line.find(FILE_HEADER_TAG) != -1):
                found_header = True
                continue
            if (line.find("index") != -1):
                li = line.strip().split(":")
                val = int(li[1])
                DBfamous.famous_total_item = val

    def parse_famous_file_to_index(self):
        """parse famous file and produce index list"""
        fd = open(dbimages.famous_file, 'r')
        item_num = 0
        found_new_item = False
        item_text = ""
        if DBfamous.famous_total_item > 1:
            del DBfamous.famous_list[:]
        while True:
            line = fd.readline()
            if not line:
                break
            if (line.find(CONTENT_ITEM_TAG) != -1):
                item_num = item_num + 1
                found_new_item = True
                if item_text != "":
                    DBfamous.famous_list.append(item_text)
                    item_text = ""
                continue
            elif (line.strip().startswith("#")):
                continue

            if found_new_item:
                item_text = item_text + line

        if item_text != "":
            DBfamous.famous_list.append(item_text)
        
        DBfamous.famous_total_item = item_num
        fd.close()

    # def famous_get_total_item(self):
    #     return DBfamous.famous_total_item

    def famous_file_get_text_by_index(self, index):
        famous_text = ""
        if (index < 1):
            return famous_text

        fd = codecs.open(dbimages.famous_file, mode='r', encoding="utf-8")
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
                    famous_text = famous_text + line
        
        famous_text = famous_text.decode("utf-8")
        return famous_text;

    def famous_list_get_text_by_index(self, index):
        famous_text = ""
        if ((index < 1) or (index > len(DBfamous.famous_list))):
            return famous_text

        return DBfamous.famous_list[index -1]

    # def famous_get_previous_item_id(self, loop):
    #     pass

    # def famous_get_next_item_id(self, loop):
    #     pass

    # def famous_get_last_item(self):
    #     return DBfamous.famous_total_item
    
    def famous_add_item_by_index(self, index, famous_text):
        # famous_filename, famous_index_filename
        # print "add item by index"
        if (famous_text == ""):
            return
        if (index < 0 or index >= DBfamous.famous_total_item):
            DBfamous.famous_list.append(famous_text)
            DBfamous.famous_total_item = DBfamous.famous_total_item + 1
        else:
            # print "append: ", famous_text
            DBfamous.famous_list.append(famous_text)
            # DBfamous.famous_list.insert(index-1, famous_text)

    def famous_remove_item_by_index(self, index):
        if (DBfamous.famous_total_item < 1):
            return False
            # print "remove total item: " + str(DBfamous.famous_total_item) + "index: " + str(index)
        if (index > 0 or index <= DBfamous.famous_total_item):
            # print "len list: " + str(len(DBfamous.famous_list))
            del DBfamous.famous_list[index-1]
            DBfamous.famous_total_item = DBfamous.famous_total_item - 1
            return True

        return False

    def famous_file_update_by_list(self):
        """delete item from file, then reproduce index"""
        totals = len(DBfamous.famous_list)
        if (totals < 1):
            return False 
        new_filename = os.path.join(dbimages.basepath, "tmp.txt")
        fd = open(new_filename, 'w')
        fd.write(FILE_HEADER_TAG+"\n")
        fd.write("totals = " + str(totals) + "\n")
        fd.write(FILE_CONTENT_TAG+"\n")
        # print "famous update by list"
        for li in DBfamous.famous_list:
            fd.write(CONTENT_ITEM_TAG+"\n")
            fd.write(li)

        fd.write("\n")
        fd.close()
        shutil.copy(new_filename, self.famous_file)

        return True

class DBimages():
    # I can and must use dict for selects, if images can use dict, then it maybe very good
    images = []
    image_selects = []

    global_working_mode = None
    global_slideshow_started = False
    global_more_help = False
    global_little_help = False
    sys_font = None
    sys_color = 0
    image_width = 0
    image_height = 0
    image_rate = 0
    rotate_message_enable = True
    delete_message_enable = True

    default = {"lang":"English", "image_quality":"high", "image_format":"jpg", 
               "image_width":800, "image_height":600, 
               "slideshow_timeout":3, "quick_skip_num": 10, "merge_space": 10, "more_help":1, "little_help":0}
    current = {"lang":"English", "image_quality":"high", "image_format":"jpg", 
               "image_width":800, "image_height":600, 
               "slideshow_timeout":3, "quick_skip_num": 10, "merge_space": 10, "more_help":1, "little_help":0}

    input_path = ""
    output_path = ""
    copyto_path = ""
    rotate = 0

    basepath = check_path()
    basepath_doc = os.path.join(basepath, "pdoc", "doc")
    config_file = os.path.join(basepath_doc, "Config")
    version_file = os.path.join(basepath_doc, "Version")
    famous_file = os.path.join(basepath, "mdoc", "doc", "famous.txt")

    def __init__(self):
        # self.basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
        # self.config_file = os.path.join(self.basepath, "Config.txt")
        pass

    def ImageRotate(self, image):
        """this function server for save rotate image
        @Todo: rotate value have bug, and need give up this function
        """
        return

    def image_selects_add(self, index, filename):
        # print ("input", index, filename)
        # print ("db: ", self.image_selects)
        # print ("db len: ", self.image_selects_count())
        if self.image_selects_count() > 0:
            # if [index, filename] not in dbimages.image_selects:
            if self.images[index][1] != FILE_STATE_SELECT:
                self.image_selects.append([index, filename])
                self.images[index][1] = FILE_STATE_SELECT
            else:
                return False
        else:
            self.image_selects.append([index, filename])
            self.images[index][1] = FILE_STATE_SELECT

            # print self.image_selects
            # print self.images
        return True

    def image_selects_get_name(self, index):
        return self.image_selects[index][1]

    def image_selects_delete(self, index, filename):
        if self.images[index][1] == FILE_STATE_SELECT:
            self.images[index][1] = FILE_STATE_NORMAL
            self.image_selects.remove([index, filename])

    def image_selects_clear(self):
        for element in self.image_selects:
            # print ("restore file state: ", element)
            list_index = element[0]
            self.images[list_index][1] = FILE_STATE_NORMAL

        del self.image_selects[:]

    def image_selects_count(self):
        return len(self.image_selects)

    def list_add(self, filename):
        self.images.append([filename, FILE_STATE_NORMAL])
        # print len(self.images)
        # print self.images
        pass

    def list_delete(self, index):
        num = len(self.images)
        # print num
        del self.images[index]
        pass

    def list_clear(self):
        del self.images[:]
        pass

    def list_count(self):
        # print self.images
        return len(self.images)

    def list_setvalue(self, data_type, data_value):
        pass

    def list_getvalue(self, data_type):
        pass

    def ConfigLoad(self):
        """load config info into current dict from config file"""
        fd = codecs.open(dbimages.config_file, mode='r', encoding="utf-8")
        # print "on config load"
        while True:
            line = fd.readline()
            if not line:
                break
            line = line.strip()
            if (line.startswith("#")):
                continue
            li = line.split("=")
            li = [x.strip() for x in li]
            if li[0] == "lang":
                dbimages.current["lang"] = li[1]
            elif li[0] == "image_quality":
                dbimages.current["image_quality"] = li[1]
            elif li[0] == "image_format":
                dbimages.current["image_format"] = li[1]
            elif li[0] == "image_width":
                dbimages.current["image_width"] = int(li[1])
            elif li[0] == "image_height":
                dbimages.current["image_height"] = int(li[1])
            elif li[0] == "slideshow_timeout":
                dbimages.current["slideshow_timeout"] = int(li[1])
            elif li[0] == "quick_skip_num":
                dbimages.current["quick_skip_num"] = int(li[1])
            elif li[0] == "merge_space":
                dbimages.current["merge_space"] = int(li[1])
            elif li[0] == "more_help":
                dbimages.current["more_help"] = int(li[1])
            elif li[0] == "little_help":
                dbimages.current["little_help"] = int(li[1])

        fd.close()
        if dbimages.current["more_help"] == 1:
            dbimages.global_more_help = True
        else:
            dbimages.global_more_help = False
            # print dbimages.current

        if dbimages.current["little_help"] == 1:
            dbimages.global_little_help = True
        else:
            dbimages.global_little_help = False

    def ConfigSave(self):
        """save window config info to current dict and config file"""
        fd = open(dbimages.config_file, 'w')
        fd.write("# NewImages setup config\n")
        # print dbimages.current
        for key in list(dbimages.current.keys()):
            fd.write(str(key) + " = " + str(dbimages.current[key]) + "\n")
        fd.close()

    def ConfigReset(self):
        """copy default value to display window"""
        for key in list(dbimages.default.keys()):
            # print key, dbimages.default[key]
            dbimages.current[key] = dbimages.default[key]
        self.updateConfigUI()

class ImageView(wx.Window):
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, 
                 style=wx.BORDER_SUNKEN
                 ):
        wx.Window.__init__(self, parent, id, (0, 0), (-1, 300), style=style)
        self.maxWidth = 0
        self.maxHeight = 0

        self.image = None
        self.dark_bg = None
        self.lite_bg = None
        self.famous_words = ""
        self.rotate = 0
        self.zoom_value = 1.0
        self.image_scale = 0


        self.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseLeftDClick)
        # self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        # self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        # self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
        # self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    # def OnEnterWindow(self, event):
    #     pass
    #     #        print "On Enter Window -------"

    # def OnLeaveWindow(self, event):
    #     pass
    #     #        print "On Leave Window -------"

    def OnKeyUp(self, event):
        key = event.GetKeyCode()
        # print "on key up ------: ", key
        Level = event.StopPropagation()
        if (Level == 0):
            Level = 1
            event.ResumePropagation(Level)
            event.Skip()
        # event.Skip 作用是告诉MainLoop继续处理这个消息，而不是在当前handler处理完了就中断

    def OnMouseLeftDClick(self, event):
        # slidershow start if have image
        self.GetTopLevelParent().slidershow_start()

    def OnMouseLeftUp(self, event):
        Level = event.StopPropagation()
        if (Level == 0):
            Level = 1
            event.ResumePropagation(Level)
            event.Skip()

    def SetValue(self, filename, rotate, enlarge):
        # rotate: +-90, +-180, +-270, default:0; quality: 1.0, 0.8, 0.6, default: 0.8; size_extend: 0, 1.1, 1.2, 2.0, default:1
        # print "ImagePanel set value: " + filename
        if (filename):
            self.image = wx.Image(filename, wx.BITMAP_TYPE_ANY)
            if (rotate == 0):
                dbimages.rotate = 0
            else:
                if (rotate == 90):
                    dbimages.rotate = dbimages.rotate + 90
                    if (dbimages.rotate == 360):
                        dbimages.rotate = 0
                elif (rotate == -90):
                    dbimages.rotate = dbimages.rotate - 90
                    if (dbimages.rotate == -360):
                        dbimages.rotate = 0

                self.image = dbimages.ImageRotate(self.image)
        else:
            # print "no file, try to clear"
            self.image = None
            self.famous_words == " "

        self.Refresh()


    def SetImageObject(self, image_object):
        if image_object:
            self.image = image_object
            # self.image = wx.EmptyImage(image_object.size[0], image_object.size[1] )
            # self.image.SetData(image_object.convert( 'RGB' ).tostring())
            # self.image = image_object
            self.Refresh()

    def SetZoomValue(self, value):
        self.zoom_value = value
        # print "imageview zoom value: ", self.zoom_value
        if self.maxWidth == 0:
            self.maxWidth, self.maxHeight = self.GetSize()

        self.maxWidth = int(self.maxWidth * self.zoom_value)
        self.maxHeight = int(self.maxHeight * self.zoom_value)

        self.SetVirtualSize((self.maxWidth, self.maxHeight))
        self.SetScrollRate(20,20)

    def SetBackgroundMode(self, mode):
        self.bg_mode = mode
        self._updateBGInfo()

    def _updateBGInfo(self):
        bg = self.bg_mode
        border = self.border_mode

        self.dark_bg = None
        self.lite_bg = None

        if border == wx.ID_BOX_FRAME:
            self.lite_bg = wx.BLACK_PEN

        if bg == wx.ID_WHITE_BG:
            if border == wx.ID_CROP_FRAME:
                self.SetBackgroundColour('LIGHT GREY')
                self.lite_bg = wx.WHITE_BRUSH
            else:
                self.SetBackgroundColour('WHITE')

        elif bg == wx.ID_GREY_BG:
            if border == wx.ID_CROP_FRAME:
                self.SetBackgroundColour('GREY')
                self.lite_bg = wx.LIGHT_GREY_BRUSH
            else:
                self.SetBackgroundColour('LIGHT GREY')

        elif bg == wx.ID_BLACK_BG:
            if border == wx.ID_BOX_FRAME:
                self.lite_bg = wx.WHITE_PEN
            if border == wx.ID_CROP_FRAME:
                self.SetBackgroundColour('GREY')
                self.lite_bg = wx.BLACK_BRUSH
            else:
                self.SetBackgroundColour('BLACK')

        else:
            if self.check_bmp is None:
                print("self.check_bmp is None")
                # self.check_bmp = GetCheckeredBitmap()
                # self.check_dim_bmp = GetCheckeredBitmap(rgb0='\x7F', rgb1='\x66')
            if border == wx.ID_CROP_FRAME:
                self.dark_bg = self.check_dim_bmp
                self.lite_bg = self.check_bmp
            else:
                self.dark_bg = self.check_bmp

        self.Refresh()

    def SetBorderMode(self, mode):
        self.border_mode = mode
        self._updateBGInfo()

    def OnSize(self, event):
        # print "image view: on size"
        event.Skip()
        self.Refresh()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.DrawImage(dc)

    def OnEraseBackground(self, evt):
        if self.bg_mode != wx.ID_CHECK_BG:
            evt.Skip()
            return
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        self.PaintBackground(dc, self.dark_bg)

    def PaintBackground(self, dc, painter, rect=None):
        if painter is None:
            return
        if rect is None:
            pos = self.GetPosition()
            sz = self.GetSize()
        else:
            pos = rect.Position
            sz = rect.Size

        if type(painter)==wx.Brush:
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.SetBrush(painter)
            dc.DrawRectangle(pos.x,pos.y,sz.width,sz.height)
        elif type(painter)==wx.Pen:
            dc.SetPen(painter)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawRectangle(pos.x-1,pos.y-1,sz.width+2,sz.height+2)
        else:
            self.TileBackground(dc, painter, pos.x,pos.y,sz.width,sz.height)
        

    def TileBackground(self, dc, bmp, x,y,w,h):
        """Tile bmp into the specified rectangle"""
        bw = bmp.GetWidth()
        bh = bmp.GetHeight()

        dc.SetClippingRegion(x,y,w,h)

        # adjust so 0,0 so we always match with a tiling starting at 0,0
        dx = x % bw
        x = x - dx
        w = w + dx

        dy = y % bh
        y = y - dy
        h = h + dy

        tx = x
        x2 = x+w
        y2 = y+h

        while tx < x2:
            ty = y
            while ty < y2:
                dc.DrawBitmap(bmp, tx, ty)
                ty += bh
            tx += bw

    def DrawImage(self, dc):
        """must use one type image, pil or wx.image"""
        if not hasattr(self, 'image') or self.image is None:
            # print "dc.DrawText words"
            if (working_get_mode() == IMAGE_SELECT_MERGER_MODE):
                return    
            font=wx.Font(16, wx.ROMAN, wx.NORMAL, wx.NORMAL)
            dc.SetFont(font)
            if (self.famous_words == ""):
                dbfamous.parse_famous_file_header()
                if (dbfamous.famous_total_item > 0):
                    item_id = random.randint(1, dbfamous.famous_total_item)
                    #print "----------------------------- ", item_id
                    self.famous_words = dbfamous.famous_file_get_text_by_index(item_id)
                    self.famous_words = self.famous_words.replace("\n\r", "\n")
                    # print dbfamous.famous_total_item, len(dbfamous.famous_list)

            dc_tw, dc_th = dc.GetSize()
            # print("dc.GetSize: %d, %d" % (dc_tw, dc_th))
            lines = self.famous_words.split("\n")
            start = 0
            start_x = 10
            start_y = 10
            for line in lines:
                # print line
                start_x = 10
                line_total_width, line_height = dc.GetTextExtent(line)
                if line_total_width < dc_tw:
                    dc.DrawText(line, start_x, start_y)
                    start_y += line_height
                else:
                    start = 0
                    line_total_num = len(line)
                    line_max_num = line_total_num * (dc_tw-20) / line_total_width
                    # print line_max_num
                    while 1:
                        tmp = line[start:(start+line_max_num)].strip()
                        dc.DrawText(tmp, start_x, start_y)
                        start_y += line_height
                        start += line_max_num
                        line_total_num = line_total_num - line_max_num
                        if (line_total_num < 0):
                            break
                if (start_y >= dc_th):
                    break;
            return
            # print "DrawImage jzx"

        wwidth,wheight = self.GetSize()
        # print("image self.GetSize(), *** w: %d, %d" % (wwidth, wheight))
        if self.maxWidth > 0:
            wwidth = self.maxWidth
            wheight = self.maxHeight

        image = self.image
        bmp = None
        # print("image reset Size(), *** w: %d, %d, %f" % (wwidth, wheight, self.zoom_value))
        # use wx.image object
        iwidth = image.GetWidth()   # dimensions of image file
        iheight = image.GetHeight()

        xfactor = float(wwidth) / iwidth
        yfactor = float(wheight) / iheight

        self.image_scale = 0
        if self.image_scale == 0:
            if xfactor < 1.0 and xfactor < yfactor:
                self.image_scale = xfactor
            elif yfactor < 1.0 and yfactor < xfactor:
                self.image_scale = yfactor
            else:
                self.image_scale = 1.0
        else:
            if self.zoom_value > 0:
                self.image_scale *= self.zoom_value
                # print("scale: ", self.image_scale)

        # calcu scale, then change image width and height. very good
        out_width = int(self.image_scale*iwidth)
        out_height = int(self.image_scale*iheight)

        diffx = (wwidth - out_width)/2   # center calc
        diffy = (wheight - out_height)/2   # center calc

        if not bmp:
            if out_width!=iwidth or out_height!=iheight:
                sc_image = sc_image = image.Scale(out_width,out_height)
            else:
                sc_image = image
            bmp = sc_image.ConvertToBitmap()

        if image != BAD_IMAGE and image.IsOk():
            self.PaintBackground(dc, self.lite_bg, wx.Rect(diffx,diffy,out_width,out_height))
        dc.DrawBitmap(bmp, diffx, diffy, useMask=True)        # draw the image to window

class ImagePanel(wx.Panel):
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.NO_BORDER ):
        wx.Panel.__init__(self, parent, id, pos, size, style=style)
        self.bs = wx.BoxSizer(wx.VERTICAL)
        self.view = ImageView(self)
        self.bs.Add(self.view, 1, wx.EXPAND)
        self.SetSizer(self.bs)

    def SetValue(self, filename, rotate=0, enlarge=1):    # display the selected file in the panel
        # print "ImagePanel set value: " + filename
        self.view.SetValue(filename, rotate, enlarge)

    def SetImageObject(self, image_object):    # display the selected file in the panel
        self.view.SetImageObject(image_object)

    def SetZoomValue(self, value):
        self.view.SetZoomValue(value)

# button refer code
#     self.btn.SetBackgroundColour("DARKGREY")
#     self.btn.Refresh()
class Frame(wx.Frame):
    """Frame class, main window."""
    def __init__(self, startpath):
        """Create a Frame instance"""
        wx.Frame.__init__(self, None, -1, "NewImages", size=(800, 600))
        # self.SetIcon(wx.Icon('newimages.ico', wx.BITMAP_TYPE_ICO))

        self.Centre()

        self.panel = wx.Panel(self)
        dbimages.sys_color = self.panel.GetBackgroundColour()
        # print dbimages.sys_color
        dbimages.sys_font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        dbimages.sys_font.SetPointSize(dbimages.sys_font.GetPointSize()+2)

        self.list_num = 0
        self.list_selects_num = 0
        self.delete_first = True
        self.delete_image_enable = False

        self.filename = None
        self.listbox_curr_item = -1
        self.tmp_mark = True

        # do not need popup menu
        # popup menu start
        # self.popupmenu = wx.Menu()

        # menu_item1 = self.popupmenu.Append(2001, "&test1 menu\tCtrl-B")
        # menu_item2 = self.popupmenu.Append(2002, "&test2 menu\tCtrl-X")
        # menu_setup = self.popupmenu.Append(2003, "&SystemSetup\tCtrl-S")
        # self.popupmenu.AppendSeparator()
        # menu_exit = self.popupmenu.Append(-1, "E&xit")

        # self.Bind(wx.EVT_MENU, self.OnExit, menu_exit)

        # self.panel.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)

        # acceltbl = wx.AcceleratorTable([
        #     (wx.ACCEL_CTRL, ord('B'), menu_item1.GetId()),
        #     (wx.ACCEL_CTRL, ord('X'), menu_item2.GetId()),
        #     (wx.ACCEL_CTRL, ord('S'), menu_setup.GetId())
        #     ])
        # self.SetAcceleratorTable(acceltbl)

        # self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_item1)
        # self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_item2)
        # self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_setup)
        # popup menu end


        # label_in_path = wx.StaticText(self.panel, -1, "in path")
        self.text_in_path = wx.TextCtrl(self.panel, -1, "", size=(400, -1))
        label_out_path = wx.StaticText(self.panel, -1, _("Out Path"), size=(60, -1))
        self.text_out_path = wx.TextCtrl(self.panel, -1, "", size=(400, -1))
        button_open_dir = wx.Button(self.panel, label="...", size=(60, -1))

        # new refactor
        label_format = wx.StaticText(self.panel, -1, _("Format"), size=(60, -1))
        self.text_format = wx.TextCtrl(self.panel, 0, "", size=(50, -1), style=wx.TE_PROCESS_ENTER|wx.TE_CENTER);
        label_change_unit = wx.StaticText(self.panel, -1, "%")
        self.label_image_size = wx.StaticText(self.panel, -1, "", (90, -1), style=wx.ALIGN_CENTER)

        list_reset = wx.Button(self.panel, -1, label=_("Reset"))
        list_invert = wx.Button(self.panel, -1, label=_("Invert"))
        list_remove = wx.Button(self.panel, -1, label=_("Remove"))
        list_select = wx.Button(self.panel, -1, label=_("Select*"))
        list_copyto = wx.Button(self.panel, -1, label=_("Copyto"))
        list_delete = wx.Button(self.panel, -1, label=_("Delete"))
        self.list_merge = wx.Button(self.panel, -1, label=_("Merge"))
        list_slide = wx.Button(self.panel, -1, label=_("SlideShow"))
        list_change = wx.Button(self.panel, -1, label=_("Change"))
        list_setup = wx.Button(self.panel, -1, label=_("Setup"))
        list_close = wx.Button(self.panel, -1, label=_("Close"))

        # wx.LB_MULTIPLE | wx.LB_SINGLE | wx.EXTENDED

        self.list_checkbox = wx.CheckBox(self.panel, -1, _("dirs"), (20, 20), (150, 20))
        self.listbox = wx.ListBox(self.panel, -1, (20, 20), (150, 460), "", wx.LB_EXTENDED)
        self.list_label_num = wx.StaticText(self.panel, -1, "Num:")

        # start layout
        vbox_top = wx.BoxSizer(wx.HORIZONTAL)

        self.image_view = ImagePanel(self.panel)
        # self.image_view = ImagePanel( self.panel, pos=(0, 0), size=(400, 300) )

        vbox_left = wx.BoxSizer(wx.VERTICAL)

        vbox_path = wx.BoxSizer(wx.HORIZONTAL)
        vbox_path.Add(label_out_path, 0, flag=wx.ALIGN_CENTER)
        vbox_path.Add(self.text_out_path, 0, flag=wx.ALIGN_CENTER)
        vbox_path.Add((5,5))
        vbox_path.Add(button_open_dir, 0, flag=wx.ALIGN_CENTER)

        vbox_change_format = wx.BoxSizer(wx.HORIZONTAL)
        vbox_change_format.Add(label_format, 0, flag=wx.ALIGN_CENTER)
        vbox_change_format.Add(self.text_format, 0, flag=wx.EXPAND|wx.ALL)
        vbox_change_format.Add((5,5))
        vbox_change_format.Add(label_change_unit, 0, flag=wx.ALIGN_CENTER)
        vbox_change_format.Add((10,10))
        vbox_change_format.Add(self.label_image_size, 0, flag=wx.ALIGN_CENTER)

        vbox_left.Add(vbox_path, 0, flag=wx.ALIGN_LEFT)
        vbox_left.Add(vbox_change_format, 0, flag=wx.ALIGN_LEFT)
        vbox_left.Add(self.image_view, 1, wx.EXPAND)

        vbox_top.Add(vbox_left, 1, wx.EXPAND)

        vbox_cmd = wx.BoxSizer(wx.VERTICAL)
        vbox_listbox = wx.BoxSizer(wx.VERTICAL)

        vbox_cmd.Add(list_reset, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((8,8))
        vbox_cmd.Add(list_invert, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((15,15))
        vbox_cmd.Add(list_remove, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((8,8))
        vbox_cmd.Add(list_select, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((8,8))
        vbox_cmd.Add(self.list_merge, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((15,15))
        vbox_cmd.Add(list_copyto, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((8,8))
        vbox_cmd.Add(list_delete, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((8,8))
        vbox_cmd.Add(list_slide, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((8,8))
        vbox_cmd.Add(list_change, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((15,15))
        vbox_cmd.Add(list_setup, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((8,8))
        vbox_cmd.Add(list_close, 0, wx.ALIGN_CENTER)

        # self.list_merge.Disable()

        vbox_listbox.Add(self.list_checkbox, 0, wx.ALL|wx.EXPAND, border=2)
        vbox_listbox.Add(self.listbox, 0, wx.ALL|wx.EXPAND, border=1)
        vbox_listbox.Add(self.list_label_num, 0, wx.ALL|wx.EXPAND, border=2)

        vbox_cmd_listbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd_listbox.Add(vbox_cmd, 0, flag=wx.ALIGN_CENTER)
        vbox_cmd_listbox.Add(vbox_listbox, 0, flag=wx.ALIGN_CENTER)

        vbox_outpath = wx.BoxSizer(wx.HORIZONTAL)
        vbox_outpath.Add(label_out_path, 0, flag=wx.EXPAND)
        vbox_outpath.Add(self.text_out_path, 1, flag=wx.EXPAND|wx.ALL)

        vbox_format = wx.BoxSizer(wx.HORIZONTAL)
        vbox_format.Add(label_format, 0, flag=wx.ALIGN_CENTER)
        vbox_format.Add(self.text_format, 0, flag=wx.EXPAND)

        vbox_right = wx.BoxSizer(wx.VERTICAL)
        vbox_right.Add(vbox_cmd_listbox, 0, flag=wx.ALIGN_CENTER)

        vbox_top.Add(vbox_right, 0, flag=wx.ALL|wx.EXPAND, border=2)

        # start fit
        self.panel.SetSizer(vbox_top)
        self.panel.Layout()
        # vbox_top.SetSizeHints(self)
        # vbox_top.Fit(self)


        self.default_format = "1024*768"
        self.format_width = 0
        self.format_height = 0
        self.format_size = 0
        self.format_rate = 0

        # map event
        self.Bind(wx.EVT_BUTTON, self.OnOpenDir, button_open_dir)
        # comment this for release
        # button_open_dir.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterButton)
        # button_open_dir.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveButton)

        #self.Bind(wx.EVT_TEXT, self.OnInputText, self.text_format)
        #self.Bind(wx.EVT_TEXT_ENTER, self.OnInputTextEnter, self.text_format)
        self.text_format.Bind(wx.EVT_TEXT, self.OnInputText)
        self.text_format.Bind(wx.EVT_TEXT_ENTER, self.OnInputTextEnter)
        # self.text_format.Bind(wx.EVT_KILL_FOCUS, self.OnInputLostFocus)
        #self.text_format.Bind(wx.EVT_CHAR, self.OnKeyPress)
        #self.Bind(wx.EVT_BUTTON, self.OnImageChange, button_image_change)

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox, self.list_checkbox)
        self.Bind(wx.EVT_LISTBOX, self.OnListBox, self.listbox)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnDclickListBox, self.listbox)
        # self.listbox.Bind(wx.EVT_CHAR, self.OnListKeyPress)

        self.Bind(wx.EVT_BUTTON, self.OnListReset, list_reset)
        self.Bind(wx.EVT_BUTTON, self.OnListInvert, list_invert)
        self.Bind(wx.EVT_BUTTON, self.OnListRemove, list_remove)
        self.Bind(wx.EVT_BUTTON, self.OnListSelect, list_select)
        self.Bind(wx.EVT_BUTTON, self.OnListCopyto, list_copyto)
        self.Bind(wx.EVT_BUTTON, self.OnListMerge, self.list_merge)
        self.Bind(wx.EVT_BUTTON, self.OnListDelete, list_delete)
        self.Bind(wx.EVT_BUTTON, self.OnListSlide, list_slide)
        self.Bind(wx.EVT_BUTTON, self.OnListChange, list_change)
        self.Bind(wx.EVT_BUTTON, self.OnListSetup, list_setup)
        self.Bind(wx.EVT_BUTTON, self.OnExit, list_close)

        # main frame, EVT_SIZE have bug
        # self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        # self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

        # hide text ctrl 
        self.text_in_path.Hide()
        # self.label_changeto.Hide()
        # self.label_image_new_size.Hide()
        
        # drop target
        dt = FileDropTarget(self)
        self.panel.SetDropTarget(dt)

        self.messagetimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnMessageTimer, self.messagetimer)
        if ((dbimages.global_little_help == False) and (dbimages.global_more_help == False)):
            self.statusBar = None
        else:
            self.statusBar = self.CreateStatusBar()

        # if dbimages.global_more_help == True:
        self.SetMessageValue(_("Please use '...' button select a image path at first"), True)
        if os.path.isdir(startpath):
            self.AddImageFiles(startpath, True)

    def SetMessageValue(self, text, last=False):
        if ((dbimages.global_little_help == False) and (dbimages.global_more_help == False)):
            return

        self.messagetimer.Stop()
        if self.statusBar:
            self.statusBar.SetStatusText(text)
        # if self.statusBar.IsShown():
        #     self.statusBar.SetStatusText(text)
        # else:
        #     self.statusBar.Show()
        #     self.statusBar.SetStatusText(text)
        if last == False:
            self.messagetimer.Start(5000)

    def OnMessageTimer(self, event):
        self.messagetimer.Stop()
        if self.statusBar:
            self.statusBar.SetStatusText("")
        # self.statusBar.Hide()


    # def OnAccelerated(self, event):
    #     print event
    #     print "OnAccelerated(self, event)"


    def AddImageFiles(self, path, new=True):
        # print ("AddImageFiles: ", path)
        if os.path.exists(path):
            if os.path.isdir(path):
                dbimages.input_path = path
            else:
                if anyTrue(path.endswith, exts):
                    dbimages.input_path = os.path.dirname(path)
        else:
            return

            # print dbimages.input_path
        dbimages.output_path = dbimages.input_path + "_output"

        self.SetTitle(dbimages.input_path)

        self.text_out_path.SetValue(dbimages.output_path)
        self.in_path_len = len(dbimages.input_path) + 1 # add os.sep
  
        sub_dir_enable = self.list_checkbox.GetValue()

        # 1, Add to dbimages.images
        if (new == True):
            del dbimages.images[:]
        if os.path.isdir(path):
            if sub_dir_enable == True:
                os.path.walk(dbimages.input_path, self.scanfile, 0)
            else:
                files = os.listdir(dbimages.input_path)
                # print str(len(files)) + "" + os.path.abspath(dbimages.input_path)
                if (len(files) > 0):
                    for filename in files:
                        if anyTrue(filename.endswith, exts):
                            dbimages.images.append([filename, FILE_STATE_NORMAL])
        elif os.path.isfile(path):
            filename = os.path.basename(path)
            dbimages.images.append([filename, FILE_STATE_NORMAL])
        else:
            # print "input path is error!"
            return

        # 2, Update self.list_num
        self.list_num = len(dbimages.images)
        if self.list_num > 0:
            if dbimages.global_more_help == True:
                self.SetMessageValue(_("select* --> merge, Format: x% --> change"))
        # 3, listbox data update
        self.ListBoxDataUpdate()

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

    def scanfile(self, arg, dirname, names):
        for tmpfile in names:
            filename = dirname + os.sep + tmpfile
            if os.path.isfile(filename) and (os.stat(filename)[6] != 0):
                if anyTrue(filename.endswith, exts):
                    short_filename = filename[self.in_path_len:]
                    dbimages.images.append([short_filename, FILE_STATE_NORMAL])
            # win have bug for isdir, linux | win diff with this issue
            # elif os.path.isdir(filename):
            #     return
            # elif os.path.islink(filename):
            #     return

    def ListBoxDataUpdate(self):
        # print "ListBoxDataUpdate"
        self.listbox.Clear()
        for li in dbimages.images:
            if li[1] == FILE_STATE_SELECT:
                self.listbox.Append("* " + li[0])
            else:
                self.listbox.Append(li[0])
        if len(dbimages.images) > 0:
            self.listbox.SetSelection(0)
            self.__listbox_draw_image(0)
            self.listbox_curr_item = 0

        self.__ListNumUpdate()

    def __ListNumUpdate(self):
        self.list_num = len(dbimages.images)
        self.list_selects_num = dbimages.image_selects_count()
        if (self.list_num > 0):
            num_string = "Num: " + str(self.list_num)
        else:
            num_string = "Num: " + "0"

        if (self.list_selects_num > 0):
            num_string += "  Selects: " + str(self.list_selects_num)
        #     self.list_merge.Enable()
        # else:
        #     self.list_merge.Disable()
        self.list_label_num.SetLabel(num_string)

    def OnListSetup(self, event):
        system_setup_frame = SystemSetupFrame(self)
        system_setup_frame.Show(True)

    def OnListChange(self, event):
        totals = len(dbimages.images)
        if totals < 1:
            self.SetMessageValue(_("Image not found!"))
            return

        # change selects images size
        enable_change_selects = False
        self.__new_image_size_update()

        if (dbimages.format_rate <= 0):
            # print "error! no input format!"
            self.SetMessageValue(_("Not input change format."))
            return

        if (dbimages.image_selects_count() > 0):
            dlg = wx.MessageDialog(None, _("Do you want to use selects images?"), 
                                   _("Select yes/no Message"),
                                   wx.OK|wx.CANCEL|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            if (result == wx.ID_OK):
                enable_change_selects = True
            else:
                enable_change_selects = False
            dlg.Destroy()

        index = 0
        if enable_change_selects == True:
            # print("dbimages selects")
            for li in dbimages.image_selects:
                index += 1
                name = li[1]
                filename = dbimages.input_path + os.sep + name
                self.__ChangeImage(filename, index)
        else:
            selects = self.listbox.GetSelections()
            # print("listbox selects: ", selects, "len dbimages.images", len(dbimages.images))
            for index in selects:
                # print("index: ", index)
                name = dbimages.images[index][0]
                filename = dbimages.input_path + os.sep + name
                index += 1
                self.__ChangeImage(filename, index)
    
    def __ChangeImage(self, filename, index):
        # execute image change
        # print("__ChangeImage: ", filename)
        width = 800
        height = 600

        im = wx.Image(filename, wx.BITMAP_TYPE_ANY)

        im_w, im_h = im.GetSize()
        # width, height; format_width, format_height
        width = int(im_w * dbimages.format_rate/100)
        height = int(im_h * dbimages.format_rate/100)

        out_im = im.Rescale(width, height, wx.IMAGE_QUALITY_HIGH)
        dbimages.output_path = self.text_out_path.GetValue()
        #print(self.text_out_path.GetValue())
        #print(dbimages.input_path)
        #print(dbimages.output_path)
        newfilename = filename.replace(dbimages.input_path, dbimages.output_path)
        #print(newfilename)
        newpath = os.path.dirname(newfilename)
        if not os.path.isdir(newpath):
            os.makedirs(newpath)

        name, ext = os.path.splitext(newfilename)
        ext = ext.lower()
        if ext == ".jpg":
            out_im.SaveFile(newfilename, wx.BITMAP_TYPE_JPEG)
        elif ext == ".png":
            out_im.SaveFile(newfilename, wx.BITMAP_TYPE_PNG)
        elif ext == ".tif":
            newfilename = newfilename.replace(".tif", ".png")
            out_im.SaveFile(newfilename, wx.BITMAP_TYPE_PNG)
        elif ext == ".gif":
            out_im.SaveFile(newfilename, wx.BITMAP_TYPE_GIF)
        else:
            out_im.SaveFile(newfilename, wx.BITMAP_TYPE_JPEG)

        num_string = self.list_label_num.GetLabel()
        num_string_on_change = num_string + " -> " + str(index)
        try:
            filesize = os.path.getsize(newfilename)/1024
        except:
            os.error
            return
        # check filesize, can display warning message to user if more then hope size.

        # display change image process with "+ -"
        if self.tmp_mark == True:
            message = " + " + newfilename + "  file size: " + str(filesize) + "k"
            self.tmp_mark = False
        else:
            message = " - " + newfilename + "  file size: " + str(filesize) + "k"
            self.tmp_mark = True

        self.SetMessageValue(message)

    def OnListReset(self, event):
        totals = self.listbox.GetCount()
        if totals < 1:
            self.SetMessageValue(_("Image not found!"))
            return

        dbimages.copyto_path = ""
        for item in dbimages.image_selects:
            self.listbox.SetString(item[0], item[1])
        dbimages.image_selects_clear()
        if dbimages.global_more_help == True:
            self.SetMessageValue(_("Reset select* and copyto status done"))

        # self.__ListNumUpdate()

    def OnListInvert(self, event):
        totals = self.listbox.GetCount()
        if totals < 1:
            self.SetMessageValue(_("Image not found!"))
            return
        selects = self.listbox.GetSelections()
        for li in range(totals):
            if li in selects:
                self.listbox.Deselect(li)
                pass
            else:
                self.listbox.SetSelection(li)
                pass
        if dbimages.global_more_help == True:
            self.SetMessageValue(_("Select or deselect listbox item"))


    def OnListRemove(self, event):
        totals = self.listbox.GetCount()
        if totals < 1:
            self.SetMessageValue(_("Image not found!"))
            return

        selects = self.listbox.GetSelections()
        for index in selects:
            name = dbimages.images[index][0]
            self.listbox.Delete(index)
            del dbimages.images[index]
            totals -= 1
            if (index == totals):
                index -= 1
            self.listbox.SetSelection(index)
            string = _("Remove image: ") + name
            self.SetMessageValue(string)

        self.__ListNumUpdate()


    def OnListSelect(self, event):
        totals = self.listbox.GetCount()
        if totals < 1:
            self.SetMessageValue(_("Image not found!"))
            return
        self.listbox.SetFocus()
        selects = self.listbox.GetSelections()
        # print "listbox selects: ", selects
        for index in selects:
            # print index
            # print dbimages.image_selects
            name = self.listbox.GetString(index)
            result = dbimages.image_selects_add(index, name)
            if result:
                self.listbox.SetString(index, "* " + name)
            else:
                # print "result is false"
                name = self.listbox.GetString(index)
                name = name.lstrip("* ")
                dbimages.image_selects_delete(index, name)
                self.listbox.SetString(index, name)
                if dbimages.global_more_help == True:
                    string = _("select* image: ") + name
                    self.SetMessageValue(string)

            # if dbimages.image_selects_count() > 0:
            #     if index not in dbimages.image_selects[index]:
            #         name = self.listbox.GetString(index)
            #         print name
            #         dbimages.image_selects_add(index, name)
            #         self.listbox.SetString(index, "* " + name)
            #     else:
            #         #name = self.listbox.GetString(index)
            #         #name = name.lstrip("* ")
            #         name = dbimages.image_selects_get_name(index)
            #         print name
            #         dbimages.image_selects_delete_by_index(index)
            #         self.listbox.SetString(index, name)
            # else:
            #         name = self.listbox.GetString(index)
            #         dbimages.image_selects_add(index, name)
            #         self.listbox.SetString(index, "* " + name)

            # if (dbimages.images[index][1] != FILE_STATE_SELECT): 
            #     # print self.listbox.GetString(index)
            #     name = self.listbox.GetString(index)
            #     dbimages.image_selects.append(name)
            #     dbimages.images[index][1] = FILE_STATE_SELECT
            #     # print dbimages.image_selects
            #     self.listbox.SetString(index, "* " + name)
            #     self.selects.append(index)
            # else:
            #     print "file have be select"
        
        self.list_selects_num = dbimages.image_selects_count()
        self.__ListNumUpdate()

    def OnListCopyto(self, event):
        # print "list copyto event"
        totals = len(dbimages.images)
        if totals < 1:
            self.SetMessageValue(_("Image not found!"))
            return

        if dbimages.copyto_path == "":
            dialog = wx.DirDialog(None,_("Choose a directory:"),
                                  style=wx.DD_DEFAULT_STYLE)
            if dialog.ShowModal() == wx.ID_OK:
                # self.imagecopyto_path = dialog.GetPath()
                dbimages.copyto_path = dialog.GetPath()
                # self.image_path = self.text_in_path.GetValue()
                # self.image_path = dbimages.input_path
                # self.first_copy = False
            else:
                # print "input path maybe error"
                dialog.Destroy()
                return
            dialog.Destroy()

        if (cmp(dbimages.copyto_path, dbimages.input_path) != 0):
            # print dbimages.copyto_path
            selects = self.listbox.GetSelections()
            for index in selects:
                #if index not in dbimages.have_copyto_index:
                #    dbimages.have_copyto_index.append(index)
                #else:
                #    return False
                #name = self.listbox.GetString(index)
                # if (dbimages.images[index][1] != FILE_STATE_COPYTO):
                name = dbimages.images[index][0]
                org_name = dbimages.input_path + os.sep + name
                copyto_name = dbimages.copyto_path + os.sep + name
                shutil.copy2(org_name, copyto_name)
                string = _("Copyto images: ") + name
                self.SetMessageValue(string)

                # dbimages.images[index][1] = FILE_STATE_COPYTO
                # self.listbox.SetString(index, "|| " + name)
                # print "copy file: ", org_name, " to ", copyto_name
                # else:
                #     pass
                # print "maybe path error"

        return True

    def OnListMerge(self, event):
        # totals = len(dbimages.image_selects)
        totals = dbimages.image_selects_count()
        if totals < 1:
            # print "no select any item to merge big image"
            string = _("Please select* one or more image at first")
            self.SetMessageValue(string)
            return

        self.Show(False)
        mergeframe = MergeFrame(self)
        mergeframe.Show(True)
        return

    def OnListDelete(self, event):
        totals = len(dbimages.images)
        if totals < 1:
            self.SetMessageValue(_("Image not found!"))
            return
        if not self.delete_image_enable:
            # dlg = wx.MessageDialog(None, "delete?", 
            #                        "Delete Message",
            #                        wx.YES_NO| wx.ICON_QUESTION)
            # result = dlg.ShowModal()
            dlg = ImageDialog(None, -1, _("Delete image from your PC, Please confirm!!!"), 
                              _("Delete Image Message"))
            result = dlg.ShowModal()
            if (result == wx.ID_OK):
                if dlg.GetValue() == True:
                    self.delete_image_enable = True
            else:
                dlg.Destroy()
                return
            dlg.Destroy()
            # print "delete file"

        selects = self.listbox.GetSelections()
        for index in selects:
            #name = self.listbox.GetString(index)
            name = dbimages.images[index][0]
            filename = dbimages.input_path + os.sep + name
            # print filename    
            try:
                os.remove(filename)
                self.listbox.Delete(index)
                del dbimages.images[index]
                string = _("Delete image: ") + name
                self.SetMessageValue(string)
            except:
                os.error

        if index == len(dbimages.images):
            index -= 1
        # self.__ListNumUpdate()
        self.__ListboxUpdate(index)

    def OnListSlide(self, event):
        totals = len(dbimages.images)
        if totals < 1:
            self.SetMessageValue(_("Image not found!"))
            return

        self.slidershow_start()

    def format_input_string(self, input_string):
        # ";" or ":" or "" -> ",",  "x" or "X" -> "M" or "m" -> "%" or ""
        input_string = input_string.replace(":", ";")
        input_string = input_string.replace("x", "*")
        input_string = input_string.replace("X", "*")
        input_string = input_string.replace("m", "M")
        input_string = input_string.replace("k", "K")
        self.text_format.SetValue(input_string)
        # print(input_string)

    def parse_input_string(self, input_string):
        # string = "1920* 768, 1 M, 10% "
        # bug string = "1920 * 768, 1 M, 10% "
        # input_string = self.text_format.GetValue()
        self.format_width = 0
        self.format_height = 0
        self.format_size = 0
        self.format_rate = 0

        # first, delete all blank from string
        input_string = input_string.replace(" ", "")
        # print(input_string)
        format_sep = ' '
        # "," or ";" or " "
        if input_string.find(',') > -1:
            format_sep = ','
        elif input_string.find(';') > -1:
            format_sep = ';'

        input_parts = input_string.split(format_sep)
        input_parts=[input_parts[x].strip() for x in range(len(input_parts))]
        # abc = [str.strip() for str in abc.split('*')] 

        for part in input_parts:
            if part.find('*') > -1:
                li_w_h = part.split('*')
                str_num = len(li_w_h)
                if str_num > 1:
                    if li_w_h[0].isdigit():
                        self.format_width = int(li_w_h[0])
                    if li_w_h[1].isdigit():
                        self.format_height = int(li_w_h[1])
                elif str_num == 1:
                    pass
                    # print "string error"
            elif part.find('M') > -1:
                tmp = part.rstrip('M').strip()
                if tmp.isdigit():
                    self.format_size = int(tmp) * 1024 * 1024
                    # print self.format_size
                pass
            elif part.find('K') > -1:
                tmp = part.rstrip('K').strip()
                if tmp.isdigit():
                    self.format_size = int(tmp) * 1024
                    # print self.format_size
                pass
            elif part.find('%') > -1:
                tmp = part.rstrip('%').strip()
                if tmp.isdigit():
                    tmp = int(tmp)
                    if 0 < tmp < 100:
                        self.format_rate = int(tmp) / 100.0
                        # print self.format_rate

    def OnInputText(self, event):
        # input_format_help = ""
        # wait time and display info, no auto set correct value?
        # timer is must for user and me, hehe
        #        print "OnInputText"
        self. __new_image_size_update()
        # set image format
        #print self.text_format.GetValue()
        
        #self.statusBar.SetStatusText(self.text_format.GetValue())
        pass

    def OnInputTextEnter(self, event):
        # print "OnInputTextEnter"
        self. __new_image_size_update()

    # def OnInputLostFocus(self, event):
    #     # print "OnInputLostFocus"
    #     return True

    def __new_image_size_update(self):
        input_string = self.text_format.GetValue()
        if len(input_string) <= 0:
            dbimages.format_rate = 0
            return True
            num_string = str(dbimages.image_width) + " * " + str(dbimages.image_height)
            self.label_image_size.SetLabel(num_string)
            return True

        try:
            format_rate = int(input_string)
        except:
            self.text_format.SetValue("")
            return False

        # format_rate must > 5 and < 100

        dbimages.format_rate = format_rate
        if (format_rate != 0):
            num_string = str(dbimages.image_width) + " * " + str(dbimages.image_height)
            new_num_string = str(dbimages.image_width * format_rate/100) + " * " + str(dbimages.image_height * format_rate/100)
            out_string = num_string + " -> " + new_num_string 
            self.label_image_size.SetLabel(out_string)
        else:
            self.label_image_new_size.SetLabel("")

    def OnKeyPress(self, event):
        # print "OnKeyPress"
        pass

    def OnListKeyPress(self, event):
        # print "OnListKeyPress"
        pass

    def OnListBox(self, event):
        # click on listbox
        # print "click on listbox"
        selects = self.listbox.GetSelections()
        if len(selects) > 0:
            if self.listbox_curr_item != selects[0]:
                self.__listbox_draw_image(selects[0])
                self.listbox_curr_item = selects[0]
            else:
                pass
                # print "skip list item"
            ##name = self.listbox.GetString(selects[0])
            ##filename = self.text_in_path.GetValue() + os.sep + name
            #im = Image.open(filename)
            ##print filename
            #self.filename = filename
            ##self.image_view.SetValue(filename)
            #im = wx.Image(filename, wx.BITMAP_TYPE_ANY)
            #new_im = im.Scale(400, 300)
            #bmp = im.ConvertToBitmap()
            #new_im = wx.StaticBitmap(self.image_panel, -1, bmp)
            #self.image_panel.SetBackgroundColour('White')

    def OnDclickListBox(self, event):
        # print "OnDclickListBox and start imageframe"
        self.slidershow_start()

    def slidershow_start(self):
        selects = self.listbox.GetSelections()
        self.totals = len(dbimages.images)
        index = 0
        if self.totals > 0:
            if len(selects) > 0:
                index = selects[0]

            self.Show(False)
            imageframe = ImageFrame(self, index)
            imageframe.Show(True)
            # imageframe.MakeModal(True)
            # imageframe.ShowFullScreen(True)
            return True
        else:
            # print "no images"
            return False

    def __ListboxUpdate(self,index):
        # listbox update
        list_num = len(dbimages.images)

        if list_num == 0:
            self.__listbox_draw_image(index)
        else:
            if index < list_num:
                self.listbox.SetSelection(index)
                self.__listbox_draw_image(index)
            else:
                self.listbox.SetSelection(0)
                self.__listbox_draw_image(0)

        self.__ListNumUpdate()

    def __listbox_draw_image(self, index):
        # name = self.listbox.GetString(index)
        if index < 0:
            # print "setvalue blank"
            self.image_view.SetValue("")
        else:
            name = dbimages.images[index][0]
            filename = dbimages.input_path + os.sep + name
            self.image_view.SetValue(filename)
            # display image size
            im = wx.Image(filename, wx.BITMAP_TYPE_ANY)
            im_w, im_h = im.GetSize()
            # num_string = (str(im_w) + " * " + str(im_h))
            # self.label_image_size.SetLabel(num_string)
            dbimages.image_width, dbimages.image_height = im_w, im_h
            # ? wx.Image.Destroy() 
            self. __new_image_size_update()

    def OnCheckBox(self, event):
        # print "OnCheckBox"
        if (self.list_checkbox.GetValue() == True):
            self.SetMessageValue(_("Please select a image path and will support sub directory search"))
        pass

        # do not need popup menu    
    # def OnShowPopup(self, event):
    #     pos = event.GetPosition()
    #     pos = self.panel.ScreenToClient(pos)
    #     self.panel.PopupMenu(self.popupmenu, pos)

    # def OnPopupItemSelected(self, event):
    #     print "OnPopupItemSelected"
    #     #item = self.popupmenu.FindItemById(event.GetId())
    #     #print("select: %s" % item.GetText())
    #     print event.GetId()
    #     id = event.GetId()
    #     if id == 2001:
    #         print("menu 1")
    #         pass
    #     elif id == 2002:
    #         print("menu 2")
    #         pass
    #     elif id == 2003:
    #         system_setup_frame = SystemSetupFrame(self)
    #         system_setup_frame.Show(True)

    def OnSize(self, event):
        # print "main frame OnSize"
        return
        # print self.GetSize()
        # print event.GetSize()

    def OnExit(self, event):
        # print "OnExit, main_frame"
        # self.Close()
        self.Destroy()
        event.Skip()

class ImageFrame(wx.Frame):
    """
    Frame class, main window.
    use char -90, +90, zoomIn, zoomOut
    """
    def __init__(self, mainframe, index=0):
        """Create a Frame instance"""
        # wx.MAXIMIZE | wx.DEFAULT_FRAME_STYLE |
        # wx.Frame.__init__(self, None, -1, "Image Change", size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE)

        self.main_frame = mainframe
        # wx.Frame.__init__(self, None, -1, "Image Change", size=(-1,-1), style=wx.MAXIMIZE | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER| wx.MINIMIZE_BOX | wx.CLOSE_BOX)
        wx.Frame.__init__(self, None, -1, "Image Show", size=wx.DisplaySize(), style=wx.DEFAULT_FRAME_STYLE)
        # Only MS Windows support Maximize() 
        self.Maximize(True)
        self.Centre()

        # Create split window
        self.split = wx.SplitterWindow( self, -1, style=wx.SP_NOBORDER )
        self.imgpanel = wx.ScrolledWindow( self.split, -1, style=wx.NO_BORDER )
        self.imgpanel.SetScrollbars( 50, 50, 20, 20 )
        # self.img = wx.StaticBitmap( self.imgpanel, -1 )

        # imgVsizer = wx.BoxSizer( wx.VERTICAL )
        # imgHsizer = wx.BoxSizer( wx.wx.HORIZONTAL )
        # imgHsizer.Add( self.img, 1, wx.CENTER, 0 )
        # imgVsizer.Add( imgHsizer, 1, wx.CENTER, 0 )
        # self.imgpanel.SetSizer( imgVsizer )

        # print "Create a Frame instance"
        self.panel = wx.Panel(self.split, -1, style=wx.SP_NOBORDER) 
        # wx.SUNKEN_BORDER)

        # wx 2.8 -1 is ok, wx 2.9 -1 is bug, modify to 35
        self.split.SplitHorizontally ( self.imgpanel, self.panel, -30 )

        self.messagetimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnMessageTimer, self.messagetimer)
        if ((dbimages.global_little_help == False) and (dbimages.global_more_help == False)):
            self.statusBar = None
        else:
            self.statusBar = self.CreateStatusBar()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

        dbimages.global_slideshow_started = False
        self.rotate_message_enable = True
        self.delete_message_enable = True

        self._buffer = 0
        self.filename = None
        self.rotate_message_enable = True
        self.delete_message_enable = True
        self.selects_copyto_enable = True
        self.zoom_value = 1.0
        self.image_scale = 0
        self.image = None
        self.image_width = 0
        self.image_height = 0
        self.win_zoom_value = 0
        self.image_mode = IMAGEFRAME_IMAGE_NORMAL_MODE
        self.slideshow_state = False

        self.cmd_box = wx.BoxSizer(wx.HORIZONTAL)

        image_up = wx.Button(self.panel, -1, label=_("Up"), size=(60, -1))
        image_next = wx.Button(self.panel, -1, label=_("Next"), size=(60, -1))
        self.text_current_num = wx.TextCtrl(self.panel, -1, "", size=(40, -1), style=wx.TE_PROCESS_ENTER|wx.TE_CENTER)
        self.label_total_num = wx.StaticText(self.panel, -1, "/", size=(40, -1))
        self.image_slide = wx.Button(self.panel, -1, label=_("Play"), size=(60, -1))
        image_select = wx.Button(self.panel, -1, label=_("Select*"), size=(60, -1))
        image_copyto = wx.Button(self.panel, -1, label=_("Copyto"), size=(60, -1))
        image_delete = wx.Button(self.panel, -1, label=_("Delete"), size=(60, -1))
        image_rotate_left = wx.Button(self.panel, -1, label="-90°", size=(60, -1))
        image_rotate_right = wx.Button(self.panel, -1, label="+90°", size=(60, -1))
        self.image_rotate_save = wx.Button(self.panel, -1, label=_("Save"), size=(60, -1))
        image_zoom_in = wx.Button(self.panel, -1, label="⊙ ○", size=(60, -1))
        image_zoom_out = wx.Button(self.panel, -1, label="○ ⊙", size=(60, -1))
        # #"〇⊙○● ○●△▲◇◆□■·．☆★○●◇◆□◎■△▲☆★○● ∵∴ Ⅴ∧∨∵∴"
        #⊙ ○  ○ ⊙;  〇 ○, ○ 〇
        image_close = wx.Button(self.panel, -1, label=_("Close"), size=(60, -1))
        self.select_label_num = wx.StaticText(self.panel, -1, "")

        self.cmd_box.Add(image_up, 0, wx.ALIGN_CENTER)
        self.cmd_box.Add(image_next, 0, wx.ALIGN_CENTER)
        self.cmd_box.Add(self.text_current_num, 0, wx.ALIGN_CENTER)
        self.cmd_box.Add(self.label_total_num, 0, wx.ALIGN_CENTER)
        self.cmd_box.Add(self.image_slide, 0, wx.ALIGN_CENTER)
        self.cmd_box.Add((10,10))
        self.cmd_box.Add(image_zoom_in, 0, wx.ALIGN_CENTER)
        self.cmd_box.Add(image_zoom_out, 0, wx.ALIGN_CENTER)
        self.cmd_box.Add((10,10))
        self.cmd_box.Add(image_select, 0, wx.ALIGN_CENTER)
        self.cmd_box.Add(image_copyto, 0, wx.ALIGN_CENTER)
        self.cmd_box.Add(image_delete, 0, wx.ALIGN_CENTER)
        self.cmd_box.Add((10,10))
        self.cmd_box.Add(image_rotate_left, 0, wx.ALIGN_CENTER)
        self.cmd_box.Add(image_rotate_right, 0, wx.ALIGN_CENTER)
        self.cmd_box.Add(self.image_rotate_save, 0, wx.ALIGN_CENTER)
        self.cmd_box.Add((10,10))
        self.cmd_box.Add(image_close, 0, wx.ALIGN_CENTER)
        self.cmd_box.Add(self.select_label_num, 0, wx.ALIGN_CENTER)

        # Disable image_rotate_save button
        self.image_rotate_save.Disable()

        self.main_box = wx.BoxSizer(wx.VERTICAL)
        self.main_box.Add(self.cmd_box, 0, wx.ALIGN_CENTER)

        # fix image display auto size bug, must use panel.SetSizer
        self.panel.SetSizer(self.main_box)
        # on mac, need Layout(), why win/linux 
        self.panel.Layout()

        # map event
        self.Bind(wx.EVT_BUTTON, self.OnImageUp, image_up)
        self.Bind(wx.EVT_BUTTON, self.OnImageNext, image_next)
        self.Bind(wx.EVT_BUTTON, self.OnImageSlide, self.image_slide)
        self.Bind(wx.EVT_BUTTON, self.OnImageSelect, image_select)
        self.Bind(wx.EVT_BUTTON, self.OnImageCopyto, image_copyto)
        self.Bind(wx.EVT_BUTTON, self.OnImageDelete, image_delete)
        self.Bind(wx.EVT_BUTTON, self.OnImageRotateLeft, image_rotate_left)
        self.Bind(wx.EVT_BUTTON, self.OnImageRotateRight, image_rotate_right)
        self.Bind(wx.EVT_BUTTON, self.OnImageRotateSave, self.image_rotate_save)
        self.Bind(wx.EVT_BUTTON, self.OnImageZoomIn, image_zoom_in)
        self.Bind(wx.EVT_BUTTON, self.OnImageZoomOut, image_zoom_out)
        self.Bind(wx.EVT_BUTTON, self.OnImageClose, image_close)

        self.imgpanel.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.imgpanel.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseLeftDClick)
        self.imgpanel.Bind(wx.EVT_PAINT, self.OnPaint)        
        # self.imgpanel.Bind(wx.EVT_SIZE, self.OnImgpanelSize)

        self.imgpanel.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.panel.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

        self.text_current_num.Bind(wx.EVT_TEXT, self.OnInputText)
        self.text_current_num.Bind(wx.EVT_TEXT_ENTER, self.OnInputTextEnter)

        self.Bind(wx.EVT_CLOSE, self.OnExit)

        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.diffx = self.diffy = 0
        # self.imgpanel.GeiSize() is right after one photo be draw.
        # if sys.platform == "win32":
        #     # win, no issue
        #     self.win_width, self.win_height = self.imgpanel.GetSize()
        # else:
        #     # linux, have issue
        #     self.win_width, self.win_height = wx.DisplaySize()
        
        self.totals = len(dbimages.images)
        if self.totals > 0:
            if index < self.totals:
                self.index = index
            else:
                self.index = 0

            self.SetImageMode(mode=IMAGEFRAME_IMAGE_NORMAL_MODE)
            name = dbimages.images[self.index][0]
            filename = dbimages.input_path + os.sep + name
            self.SetValue(filename, new=True)
        else:
            self.index = -1
            # print "may be list box data error"
        
        self.imgpanel.SetFocus()
        self.image_ui_num_update()

        if dbimages.global_more_help == True:
            self.SetMessageValue(_("PageUp/PageDown support quick skip; select* --> merge; +-90 --> Save"))

    def OnPaint(self, event):
        # dc = wx.BufferedPaintDC(self.imgpanel, self._buffer, wx.BUFFER_VIRTUAL_AREA)
        dc = wx.PaintDC(self.imgpanel)
        # self.imgpanel.PrepareDC(dc)
        dc.DrawBitmap(self._buffer, self.diffx, self.diffy)

    # def OnImgpanelSize(self, event):
    #     event.Skip()
    #     # print "imgpanel on size"
    #     # print self.imgpanel.GetSize()

    def OnInputText(self, event):
        # print "OnInputText *"
        event.Skip()
 
    def OnInputTextEnter(self, event):
        # print "OnInputTextEnter *"
        input_string = self.text_current_num.GetValue()
        index = 0
        try:
            index = int(input_string) - 1
        except:
            index = 0
            # print ("index: ", index)
        if (self.index != index) and (index < self.totals):
            self.index = index
            self.SetImageMode(mode=IMAGEFRAME_IMAGE_NORMAL_MODE)
            name = dbimages.images[self.index][0]
            filename = dbimages.input_path + os.sep + name
            self.SetValue(filename, new=True)
                 
        event.Skip()

    def SetMessageValue(self, text, last=False):
        if ((dbimages.global_little_help == False) and (dbimages.global_more_help == False)):
            return

        self.messagetimer.Stop()
        if self.statusBar:
            self.statusBar.SetStatusText(text)

        # if self.statusBar.IsShown():
        #     self.statusBar.SetStatusText(text)
        # else:
        #     self.statusBar.Show()
        #     self.statusBar.SetStatusText(text)
            # print "message timer start"
        if last == False:
            self.messagetimer.Start(5000)

    def OnMessageTimer(self, event):
        self.messagetimer.Stop()
        if self.statusBar:
            self.statusBar.SetStatusText("")
        # self.statusBar.Hide()

    def OnImageRotateLeft(self, event):
        if self.totals < 1:
            self.SetMessageValue("Image not found!")
            return

        # print "rotate left event"
        # print "rotate left"
        self.SetImageMode(IMAGEFRAME_IMAGE_ROTATE_MODE)
        name = dbimages.images[self.index][0]
        filename = dbimages.input_path + os.sep + name
        self.SetValue(filename, rotate=-90)
        if dbimages.global_more_help == True:
            self.SetMessageValue(_("Image rotate -90"))

    def OnImageRotateRight(self, event):
        if self.totals < 1:
            self.SetMessageValue("Image not found!")
            return

        # print "rotate right event"
        # print "rotate right"
        self.SetImageMode(IMAGEFRAME_IMAGE_ROTATE_MODE)
        name = dbimages.images[self.index][0]
        filename = dbimages.input_path + os.sep + name
        self.SetValue(filename, rotate=90)
        if dbimages.global_more_help == True:
            self.SetMessageValue(_("Image rotate +90"))

    def OnImageZoomIn(self, event):
        if self.totals < 1:
            self.SetMessageValue("Image not found!")
            return

        self.SetImageMode(IMAGEFRAME_IMAGE_ZOOM_MODE)
        if (self.zoom_value > 0.1):
            self.zoom_value -= 0.1
            name = dbimages.images[self.index][0]
            filename = dbimages.input_path + os.sep + name
            # print ("zoom in", self.zoom_value)
            self.SetValue(filename)
            if dbimages.global_more_help == True:
                self.SetMessageValue(_("Image zoom in"))

    def OnImageZoomOut(self, event):
        if self.totals < 1:
            self.SetMessageValue("Image not found!")
            return

        self.SetImageMode(IMAGEFRAME_IMAGE_ZOOM_MODE)
        if (self.zoom_value < 20):
            self.zoom_value += 0.1
            name = dbimages.images[self.index][0]
            filename = dbimages.input_path + os.sep + name
            # print ("zoom out", self.zoom_value)
            self.SetValue(filename)
            if dbimages.global_more_help == True:
                self.SetMessageValue(_("Image zoom out"))

    def OnImageRotateSave(self, event):
        """message and save to
        """
        if self.totals < 1:
            self.SetMessageValue("Image not found!")
            return

        enable_rotate_save = True
        if (self.totals > 0) and (dbimages.rotate != 0):
            if dbimages.rotate_message_enable == True:
                dlg = ImageDialog(None, -1, _("Save will overwrite the original image file!!!"), 
                                       _("Rotate Save Message"))
                # dlg = wx.MessageDialog(None, "save will overwrite the original image file!!!", 
                #                        "Rotate save Message",
                #                        wx.YES_NO| wx.ICON_QUESTION)
                result = dlg.ShowModal()
                if (result == wx.ID_OK):
                    if dlg.GetValue() == True:
                        dbimages.rotate_message_enable = False

                else:
                    enable_rotate_save = False
                dlg.Destroy()

            if enable_rotate_save == True:
                name = dbimages.images[self.index][0]
                filename = dbimages.input_path + os.sep + name
                image = wx.Image(filename, wx.BITMAP_TYPE_ANY)
                while (dbimages.rotate != 0):
                    if dbimages.rotate > 0:
                        dbimages.rotate -= 90
                        image = image.Rotate90(True)
                    else:
                        dbimages.rotate += 90
                        image = image.Rotate90(False)

                image.SaveFile(filename, type=wx.BITMAP_TYPE_JPEG)
                if dbimages.global_more_help == True:
                    string = _("Saved image: ") + name
                    self.SetMessageValue(string)

    def image_ui_num_update(self):
        # print "image_ui_num_update: ", self.index, self.totals
        if self.totals < 1 or self.index < 0:
            return
        self.text_current_num.SetValue(str(self.index+1))
        self.label_total_num.SetLabel("/"+str(self.totals))

        if (dbimages.images[self.index][1] == FILE_STATE_SELECT):
            self.SetTitle("* " + dbimages.images[self.index][0])
        else:
            self.SetTitle(dbimages.images[self.index][0])
        # if (dbimages.images[self.index][1] == FILE_STATE_NORMAL):
        #     self.SetTitle(dbimages.images[self.index][0])
        # elif (dbimages.images[self.index][1] == FILE_STATE_SELECT):
        #     self.SetTitle("* " + dbimages.images[self.index][0])
        # elif (dbimages.images[self.index][1] == FILE_STATE_COPYTO):
        #     self.SetTitle("|| " + dbimages.images[self.index][0])
        # else:
        #     pass
        # print "state error: ", dbimages.images[self.index][1]
        self.__SelectNumUpdate()

    def OnKeyUp(self, event):
        # print "on key up ======"
        if self.totals < 1:
            self.SetMessageValue("Image not found!")
            return

        key = event.GetKeyCode()
        # print ("KeyPress: %d"% (key))
        # PageUp 366; PageDown 367
        # (27, 32, 314, 315, 316, 317)
        if ((key == wx.WXK_LEFT) or (key == wx.WXK_UP)):
            self.ImageUp()
        elif ((key == wx.WXK_DOWN) or (key == wx.WXK_RIGHT)):
            self.ImageNext()
        elif ((key == wx.WXK_ESCAPE) or (key == wx.WXK_SPACE)):
            if (dbimages.global_slideshow_started == True):
                self.slider_on_off()
        elif (key == wx.WXK_PAGEUP):
              self.ImageQuickUp()
        elif (key == wx.WXK_PAGEDOWN):
              self.ImageQuickDown()

        if dbimages.global_more_help == True:
            self.SetMessageValue(_("Receive keyboard message"))

        # print(wx.WXK_ESCAPE, wx.WXK_SPACE, wx.WXK_LEFT, wx.WXK_UP, wx.WXK_RIGHT, wx.WXK_DOWN)
        event.Skip()

    def OnMouseLeftUp(self, event):
        # print "mouse left on up click ======"
        # print("global_slideshow_started: ", dbimages.global_slideshow_started)
        if (dbimages.global_slideshow_started == True):
            self.slider_on_off()
            if dbimages.global_more_help == True:
                self.SetMessageValue(_("Play is stoped."))


    def OnMouseLeftDown(self, event):
        pass
        # print "mouse left on down click ======="

    def OnMouseLeftDClick(self, event):
        # print "mouse left dclick"
        # -1, 0, 1
        if self.totals < 1:
            self.SetMessageValue("Image not found!")
            return

        self.SetImageMode(IMAGEFRAME_IMAGE_QUICK_ZOOM_MODE)
        self.win_zoom_value += 1
        if self.win_zoom_value > 1:
            self.win_zoom_value = -1
            # print ("self.win_zoom_value: %d" % self.win_zoom_value)
        name = dbimages.images[self.index][0]
        filename = dbimages.input_path + os.sep + name
        # print ("quick zoom", self.win_zoom_value)
        self.SetValue(filename)
        if dbimages.global_more_help == True:
            self.SetMessageValue(_("Image quick zoom"))

    def KeyPress(self, event):
        # print "Key press ======"
        key = event.GetKeyCode()
        # print "KeyPress: ", key

    # def OnEnterWindow(self, event):
    #     pass
    #     # print "On Enter Window"

    # def OnLeaveWindow(self, event):
    #     pass
    #     # print "On Leave Window"

    def OnSize(self, event):
        event.Skip()
        # print "image frame OnSize"
        # print self.GetSize()
        # print event.GetSize()
        # self.Layout()

    def ImageQuickUp(self):
        num = dbimages.current["quick_skip_num"]
        if (self.totals < num) or (self.index == 0):
            return

        if ((self.index - num) > 0) and (self.index < self.totals):
            self.index -= num
        else:
            self.index = 0

        self.SetImageMode(mode=IMAGEFRAME_IMAGE_NORMAL_MODE)
        name = dbimages.images[self.index][0]
        filename = dbimages.input_path + os.sep + name
        self.SetValue(filename, new=True)
        if dbimages.global_more_help == True:
            self.SetMessageValue(_("Image quick skip up"))

    def ImageQuickDown(self):
        num = dbimages.current["quick_skip_num"]
        if (self.totals < num) or (self.index == self.totals - 1):
            return

        if ((self.index + num) < self.totals and (self.index >= 0)):
            self.index += num
        else:
            self.index = self.totals - 1

        self.SetImageMode(mode=IMAGEFRAME_IMAGE_NORMAL_MODE)
        name = dbimages.images[self.index][0]
        filename = dbimages.input_path + os.sep + name
        self.SetValue(filename, new=True)
        if dbimages.global_more_help == True:
            self.SetMessageValue(_("Image quick skip down"))

    def OnImageUp(self, event):
        if self.totals < 1:
            self.SetMessageValue("Image not found!")
            return

        self.ImageUp()

    def ImageUp(self):
        if (self.index > 0) and (self.index < self.totals):
            self.index -= 1
        else:
            self.index = self.totals - 1

        self.SetImageMode(mode=IMAGEFRAME_IMAGE_NORMAL_MODE)
        name = dbimages.images[self.index][0]
        filename = dbimages.input_path + os.sep + name
        self.SetValue(filename, new=True)

    def OnImageNext(self, event):
        if self.totals < 1:
            self.SetMessageValue("Image not found!")
            return

        self.ImageNext()

    def ImageNext(self):
        if (self.index >= 0) and (self.index < (self.totals-1)):
            self.index += 1
        else:
            self.index = 0

            # print "image next"
        self.SetImageMode(mode=IMAGEFRAME_IMAGE_NORMAL_MODE)
        name = dbimages.images[self.index][0]
        filename = dbimages.input_path + os.sep + name
        self.SetValue(filename, new=True)

    def OnImageSlide(self, event):
        self.slider_on_off()

    def slider_on_off(self):
        if self.totals < 1:
            self.SetMessageValue("Image not found!")
            return

        if (self.slideshow_state == False):
            self.SetMessageValue(_("Start playing ..."))
            self.SetImageMode(mode=IMAGEFRAME_IMAGE_NORMAL_MODE)
            timeout = dbimages.current["slideshow_timeout"] * 1000
            self.timer.Start(timeout)
            self.slideshow_state = True
            #self.panel.Hide()
            # if self.statusBar:
            #     self.statusBar.Destroy()
            #self.split.SetSashPosition(-1)
            self.ShowFullScreen(True)
            self.extend_height, self.extend_width = self.GetSize()
            self.split.SetSashPosition(self.extend_width)
            dbimages.global_slideshow_started = True
            name = dbimages.images[self.index][0]
            filename = dbimages.input_path + os.sep + name
            self.SetValue(filename, new=False)
        else:
            self.timer.Stop()
            dbimages.global_slideshow_started = False
            self.slideshow_state = False
            # self.panel.Show()
            # if ((dbimages.global_little_help == False) and (dbimages.global_more_help == False)):
            #     pass
            # else:
            #     self.statusBar = self.CreateStatusBar()
            self.ShowFullScreen(False)
            self.split.SetSashPosition(-30)
            name = dbimages.images[self.index][0]
            filename = dbimages.input_path + os.sep + name
            self.SetValue(filename, new=False)
            # self.Layout()

    def OnTimer(self, event):
        if (self.index >= 0) and (self.index < (self.totals-1)):
            self.index += 1
            name = dbimages.images[self.index][0]
            filename = dbimages.input_path + os.sep + name
            # self.SetTitle(name)
            # print "ontimer and set value"
            self.SetValue(filename, new=True)
        else:
            # print "timer stop done"
            self.timer.Stop()
            self.slideshow_state = False
            self.ShowFullScreen(False)
            self.split.SetSashPosition(-30)
            name = dbimages.images[self.index][0]
            filename = dbimages.input_path + os.sep + name
            self.SetValue(filename, new=False)

            # self.panel.Show()
            # if ((dbimages.global_little_help == False) and (dbimages.global_more_help == False)):
            #     pass
            # else:
            #     self.statusBar = self.CreateStatusBar()
            # self.split.SetSashPosition(-30)
            # self.Layout()
            # self.statusBar.Show()

    def OnImageSelect(self, event):
        if self.totals < 1:
            self.SetMessageValue("Image not found!")
            return
        name = dbimages.images[self.index][0]
        result = dbimages.image_selects_add(self.index, name)
        self.image_ui_num_update()
        # self.__SelectNumUpdate()

    def __SelectNumUpdate(self):
        num_string = ""
        self.select_num = dbimages.image_selects_count()
        if (self.select_num > 0):
            num_string = num_string + " Selects: " + str(self.select_num)

        if dbimages.images[self.index][1] == FILE_STATE_SELECT:
            num_string += " |☆"

        self.select_label_num.SetLabel(num_string)

    def OnImageCopyto(self, event):
        # print "list copyto event"
        totals = len(dbimages.images)
        enable_copyto_selects = False
        if totals < 1:
            self.SetMessageValue("Image not found!")
            return

        if dbimages.copyto_path == "":
            dialog = wx.DirDialog(None,_("Choose a directory:"),
                                  style=wx.DD_DEFAULT_STYLE)
            if dialog.ShowModal() == wx.ID_OK:
                dbimages.copyto_path = dialog.GetPath()
            else:
                # print "input path maybe error"
                dialog.Destroy()
                return
            dialog.Destroy()

        if (dbimages.image_selects_count() > 0) and (self.selects_copyto_enable == True):
            dlg = ImageDialog(None, -1, _('Do you want to select "select*" to execute copyto?'), 
                              _('Select "selects"?'))
            result = dlg.ShowModal()
            if (result == wx.ID_OK):
                if dlg.GetValue() == True:
                    self.selects_copyto_enable = False
                enable_copyto_selects = True
            else:
                enable_copyto_selects = False
            dlg.Destroy()

        if enable_copyto_selects == True:
            for li in dbimages.image_selects:
                self.ImageCopyTo(li[0])
                # print("copyto file: ", li[1])
                # print("image_selects_clear")
            dbimages.image_selects_clear()

        else:
            # print("copyto file id: ", self.index)
            self.ImageCopyTo(self.index)

    def ImageCopyTo(self, index):
        if ((cmp(dbimages.copyto_path, dbimages.input_path) != 0)):
            # and (dbimages.images[index][1] != FILE_STATE_COPYTO)):
            # print dbimages.copyto_path

            name = dbimages.images[index][0]
            org_name = dbimages.input_path + os.sep + name
            copyto_name = dbimages.copyto_path + os.sep + name
            shutil.copy2(org_name, copyto_name)
            string = _("Copyto images: ") + name
            self.SetMessageValue(string)

            # dbimages.images[index][1] == FILE_STATE_COPYTO
            # print "copy file: ", org_name, " to ", copyto_name
        else:
            pass
            # print "maybe path error"

        return True

    def OnImageDelete(self, event):
        totals = len(dbimages.images)
        if totals < 1:
            self.SetMessageValue("Image not found!")
            return
        enable_delete = True
        # print "on image delete"
        if dbimages.delete_message_enable == True:
            dlg = ImageDialog(None, -1, _("Delete image from your PC, Please confirm!!!"), 
                              _("Delete Image Message"))

            result = dlg.ShowModal()
            if (result == wx.ID_OK):
                if dlg.GetValue() == True:
                    dbimages.delete_message_enable = False
            else:
                enable_delete = False
            dlg.Destroy()

        if (enable_delete == True):
            name = dbimages.images[self.index][0]
            filename = dbimages.input_path + os.sep + name
            # filename    
            try:
                os.remove(filename)
                del dbimages.images[self.index]
                self.totals = self.totals - 1
                string = _("Delete image: ") + name
                self.SetMessageValue(string)

                if (self.totals > 0):
                    if (self.index == self.totals):
                        self.index = self.index -1
                    name = dbimages.images[self.index][0]
                    filename = dbimages.input_path + os.sep + name
                    # print ("try to:", filename)
                    self.SetImageMode(IMAGEFRAME_IMAGE_NORMAL_MODE)
                    self.SetValue(filename, new=True)
                else:
                    self.SetValue("")
            except:
                os.error

            self.image_ui_num_update()

    def OnImageClose(self, event):
        self.main_frame.ListBoxDataUpdate()

        self.Destroy()
        if self.main_frame:
            self.main_frame.Show(True)
        pass

    def SetImageMode(self, mode=IMAGEFRAME_IMAGE_NORMAL_MODE):
        self.image_mode = mode
        if (mode == IMAGEFRAME_IMAGE_ROTATE_MODE):
            self.image_rotate_save.Enable()
        else:
            self.image_rotate_save.Disable()

    def GetImageMode(self):
        return self.image_mode

    def __calculate_scale(self, win_width, win_height, image_width, image_height):
        # print ("self.GetSize(): ", self.GetSize())
        # print "window size: " + str(self.win_width) + " * " + str(self.win_height)
        # print "image size: " + str(self.image_width) + " * " + str(self.image_height)
        xfactor = float(win_width) / image_width
        yfactor = float(win_height) / image_height
        # print ("xfactor: %d, yfactor: %d"% (xfactor, yfactor))
        if xfactor < 1.0 and xfactor < yfactor:
            if yfactor != 0:
                image_scale = xfactor
            else:
                image_scale = yfactor
        elif yfactor < 1.0 and yfactor < xfactor:
            if xfactor != 0:
                image_scale = yfactor
            else:
                image_scale = xfactor
        else:
            image_scale = 1.0
        # print ("image_scale: %d" %image_scale)
        return image_scale

    def DrawImage(self, filename, rotate):
        # need mode: normal; zoom; quick zoom; 
        mode = self.GetImageMode()
        image_scale = 0
        if self.totals < 1 or self.index < 0:
            # print ("self.GetSize(): ", self.GetSize())
            win_width, win_height = self.GetSize()
            win_width -= 100
            win_height -= 100
            empty_image = wx.EmptyImage(win_width, win_height)
            empty_image.Replace(0,0,0,255,255,255)
            self._buffer = empty_image.ConvertToBitmap()
            sz = (win_width,win_height)
            self.Refresh()
            # self.img.SetSize( sz )
            # self.img.SetBitmap( bmp )
            self.imgpanel.SetVirtualSize( sz )
            return

        if mode == IMAGEFRAME_IMAGE_ZOOM_MODE:
            # print "zoom mode"
            if self.zoom_value > 0:
                out_image_scale = self.image_scale * self.zoom_value

        elif mode == IMAGEFRAME_IMAGE_QUICK_ZOOM_MODE:
            # print "quick zoom mode"
            if self.win_zoom_value == 1:
                out_image_scale = 1.0
            elif self.win_zoom_value == 0:
                # out_image_scale = self.__calculate_scale()
                out_image_scale = self.__calculate_scale(self.win_width, self.win_height, self.image_width, self.image_height)
            elif self.win_zoom_value == -1:
                win_width, win_height = self.GetSize()
                win_width /= 2
                win_height /= 2
                xfactor = float(win_width) / self.image_width
                yfactor = float(win_height) / self.image_height
                if xfactor < 1.0 and xfactor < yfactor:
                    image_scale = xfactor
                elif yfactor < 1.0 and yfactor < xfactor:
                    image_scale = yfactor
                else:
                    image_scale = 1.0
                out_image_scale = image_scale

        elif mode == IMAGEFRAME_IMAGE_ROTATE_MODE:
            if (rotate == 0):
                dbimages.rotate = 0
            else:
                if (rotate == 90):
                    self.image = self.image.Rotate90(True)
                    dbimages.rotate = dbimages.rotate + 90
                    if (dbimages.rotate == 360):
                        dbimages.rotate = 0
                elif (rotate == -90):
                    self.image = self.image.Rotate90(False)
                    dbimages.rotate = dbimages.rotate - 90
                    if (dbimages.rotate == -360):
                        dbimages.rotate = 0

            self.image_width = self.image.GetWidth()
            self.image_height = self.image.GetHeight()

            # out_image_scale = self.__calculate_scale()
            out_image_scale = self.__calculate_scale(self.win_width, self.win_height, self.image_width, self.image_height)
            self.image_scale = out_image_scale
        else:
            # print ("normal image mode: %d", mode)
            self.image = wx.Image(filename, wx.BITMAP_TYPE_ANY)
            self.image_width, self.image_height = self.image.GetSize()
            self.win_width, self.win_height = self.imgpanel.GetSize()
            if (self.win_width == 0 or self.win_height == 0):
                # get screen size, and reduce deviation, magic number
                self.win_width, self.win_height = wx.DisplaySize()
                self.win_width -= 25
                self.win_height -= 70
            # print self.imgpanel.GetSize()
            out_image_scale = self.__calculate_scale(self.win_width, self.win_height, self.image_width, self.image_height)
            if out_image_scale == 0:
                out_image_scale = 1.0

            self.image_scale = out_image_scale

        # print ("self.image_scale, out_image_scale: ", self.image_scale, out_image_scale)
        if (out_image_scale != 1.0):
            out_width = int(out_image_scale * self.image_width)
            out_height = int(out_image_scale * self.image_height)
            sc_image = self.image.Scale(out_width, out_height)
            self._buffer = sc_image.ConvertToBitmap()
            self.diffx = (self.win_width - out_width)/2
            self.diffy = (self.win_height - out_height)/2
        else:
            self._buffer = self.image.ConvertToBitmap()
            self.diffx = (self.win_width - self.image_width)/2
            self.diffy = (self.win_height - self.image_height)/2
            out_width = self.image_width
            out_height = self.image_height

        # print("self.image_width: %d, self.image_height: %d, self.win_width: %d, self.win_height: %d, out_width: %d, out_height: %d"%
        #       (self.image_width, self.image_height, self.win_width, self.win_height, out_width, out_height))
        # print("self.diffx: %d, self.diffy: %d"% (self.diffx, self.diffy))
        sz = (out_width, out_height)
        self.imgpanel.SetVirtualSize( sz )
        self.Refresh()

        # self.img.SetSize( sz )
        # self.img.SetBitmap( bmp )
        # print ("virtualsize: ", sz)


    def SetValue(self, filename, rotate=0, new=False):    # display the selected file in the panel
        # print ("Image SetValue and draw bitmap" + filename)
        if new == True:
            self.ResetVal()
        # im = wx.Image(filename, wx.BITMAP_TYPE_ANY)
        # self._buffer = im.ConvertToBitmap()
        # self.Refresh()
        # return
        # skip draw image for refactor

        self.DrawImage(filename, rotate)
        li = filename.split(os.sep)
        if len(li) > 0:
            self.SetTitle(li[-1])
        else:
            self.SetTitle("")
        self.image_ui_num_update()

    def ResetVal(self):
        self.zoom_value = 1.0
        self.image_scale = 0
        self.win_zoom_value = 0

    def OnExit(self, event):
        if (self.slideshow_state == True):
            self.timer.Stop()
            self.slideshow_state = False

        self.main_frame.ListBoxDataUpdate()

        self.Destroy()
        if self.main_frame:
            self.main_frame.Show(True)

    def scale_size(self, s_width, s_height, to_width, to_height):
        xfactor = float(to_width) / s_width
        yfactor = float(to_height) / s_height
        # print (s_width, s_height)
        # print (to_width, to_height)
        # print (xfactor, yfactor)
        if xfactor < 1.0 and xfactor < yfactor:
            scale = xfactor
        elif yfactor < 1.0 and yfactor < xfactor:
            scale = yfactor
        else:
            scale = xfactor

        # scale = 1.0
        # print scale
        out_width = int(scale*s_width)
        out_height = int(scale*s_height)

        # print (out_width, out_height)
        return (out_width, out_height)

class MergeFrame(wx.Frame):
    """Merge Images Frame class, sub window."""
    def __init__(self, mainframe):
        """Create a Frame instance"""
        self.main_frame = mainframe
        wx.Frame.__init__(self, None, -1, _("Merge Image"), size=(850, 650))

        self.Centre()
        panel = wx.Panel(self)

        self.merge_done = False
        self.image_w = 0
        self.image_h = 0

        # if not self.main_frame:
        #     pass
        #     # print "insert db data for slideshow"
        self.big_image = None
        self.list_num = 0
        self.list_index = -1

        self.messagetimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnMessageTimer, self.messagetimer)
        if ((dbimages.global_little_help == False) and (dbimages.global_more_help == False)):
            self.statusBar = None
        else:
            self.statusBar = self.CreateStatusBar()

        label_size = wx.StaticText(panel, -1, _("Size:"))
        self.text_input_size = wx.TextCtrl(panel, -1, "800*600", size=(80, -1))
        label_or = wx.StaticText(panel, -1, _("Or"))
        self.text_input_percent_size = wx.TextCtrl(panel, -1, "", size=(40, -1))
        label_percent = wx.StaticText(panel, -1, "%")

        label_cols = wx.StaticText(panel, -1, _("Cols:"))
        self.text_input_cols = wx.TextCtrl(panel, -1, "1", size=(30, -1))
        label_filename = wx.StaticText(panel, -1, _("OutFile"))
        self.text_filename = wx.TextCtrl(panel, -1, "merge_files.jpg", size=(180, -1))

        if dbimages.current["image_format"] == "jpg":
            self.text_filename.SetValue("merge_files.jpg")
        elif dbimages.current["image_format"] == "png":
            self.text_filename.SetValue("merge_files.png")
        else:
            self.text_filename.SetValue("merge_files.jpg")

        # wx.LB_EXTENDED wx.LB_SINGLE
        listbox_up = wx.Button(panel, -1, label="↑", size=(30,30))
        listbox_down = wx.Button(panel, -1, label="↓", size=(30,30))
        self.merge_checkbox = wx.CheckBox(panel, -1, _("preview"), (20, 20), (150, 20))
        self.listbox = wx.ListBox(panel, -1, (20, 20), (150, 460), "", wx.LB_SINGLE)
        self.list_label_num = wx.StaticText(panel, -1, "  Num:")
        self.label_image_size = wx.StaticText(panel, -1, "")

        list_merge = wx.Button(panel, -1, label=_("Merge"), size=(60, -1))
        list_close = wx.Button(panel, -1, label=_("Close"), size=(60, -1))

        self.image_view = ImagePanel( panel )

        # start layout
        vbox_top = wx.BoxSizer(wx.HORIZONTAL)
        vbox_left = wx.BoxSizer(wx.VERTICAL)

        vbox_format = wx.BoxSizer(wx.HORIZONTAL)
        vbox_format.Add(label_size, 0, flag=wx.ALIGN_CENTER)
        vbox_format.Add(self.text_input_size, 0, flag=wx.EXPAND)
        vbox_format.Add((5,5))
        vbox_format.Add(label_or, 0, flag=wx.ALIGN_CENTER)
        vbox_format.Add((5,5))
        vbox_format.Add(self.text_input_percent_size, 0, flag=wx.ALIGN_CENTER)
        vbox_format.Add(label_percent, 0, flag=wx.ALIGN_CENTER)
        vbox_format.Add((5,5))
        vbox_format.Add(label_cols, 0, flag=wx.ALIGN_CENTER)
        vbox_format.Add(self.text_input_cols, 0, flag=wx.EXPAND)
        vbox_format.Add((5,5))
        vbox_format.Add(label_filename, 0, flag=wx.ALIGN_CENTER)
        vbox_format.Add(self.text_filename, 0, flag=wx.EXPAND)
        vbox_format.Add((5,5))
        vbox_format.Add(list_merge, 0, wx.ALIGN_CENTER)
        vbox_format.Add((5,5))
        vbox_format.Add(list_close,  0, wx.ALIGN_CENTER)

        vbox_left.Add(vbox_format, 0, flag=wx.ALIGN_LEFT)
        vbox_left.Add(self.image_view, 1, wx.EXPAND)
        vbox_top.Add(vbox_left, 1, wx.EXPAND)


        vbox_listbox_cmd = wx.BoxSizer(wx.VERTICAL)
        vbox_listbox = wx.BoxSizer(wx.VERTICAL)

        vbox_listbox_cmd.Add(listbox_up, 0, wx.ALIGN_CENTER)
        vbox_listbox_cmd.Add(listbox_down, 0, wx.ALIGN_CENTER)

        vbox_listbox.Add(self.merge_checkbox, 0, wx.ALL|wx.EXPAND, border=2)
        vbox_listbox.Add(self.listbox, 0, wx.ALL|wx.EXPAND, border=2)

        vbox_cmd_listbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox_cmd_listbox.Add(vbox_listbox_cmd, 0, flag=wx.ALIGN_CENTER)
        vbox_cmd_listbox.Add(vbox_listbox, 0, flag=wx.ALIGN_CENTER)

        vbox_num = wx.BoxSizer(wx.HORIZONTAL)
        vbox_num.Add(self.list_label_num, 0, flag=wx.ALIGN_LEFT)

        vbox_right = wx.BoxSizer(wx.VERTICAL)
        vbox_right.Add(vbox_cmd_listbox, 0, flag=wx.ALIGN_CENTER)
        vbox_right.Add(vbox_num, 0, flag=wx.ALIGN_LEFT)
        vbox_right.Add((15,15))
        vbox_right.Add(self.label_image_size, 0, flag=wx.ALIGN_LEFT)

        vbox_top.Add(vbox_right, 0, flag=wx.ALL|wx.EXPAND, border=2)

        panel.SetSizer(vbox_top)
        panel.Layout()
        # map event
        self.text_input_percent_size.Bind(wx.EVT_TEXT, self.OnInputText)
        # self.text_input_percent_size.Bind(wx.EVT_TEXT_ENTER, self.OnInputTextEnter)

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox, self.merge_checkbox)
        self.Bind(wx.EVT_LISTBOX, self.OnListBox, self.listbox)
        self.Bind(wx.EVT_BUTTON, self.OnMerge, list_merge)
        self.Bind(wx.EVT_BUTTON, self.OnListBoxUp, listbox_up)
        self.Bind(wx.EVT_BUTTON, self.OnListBoxDown, listbox_down)
        self.Bind(wx.EVT_BUTTON, self.OnClose, list_close)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.merge_ui_listbox_update()
        working_set_mode(IMAGE_SELECT_MERGER_MODE)

        self.view_image_update()

        # self.statusBar.Hide()
        if dbimages.global_more_help == True:
            self.SetMessageValue(_("Please input single image size: 800*600 or 400*300 ... etc, input max cols: 2 or 3 or 4 ..."), True)

    def SetMessageValue(self, text, last=False):
        if ((dbimages.global_little_help == False) and (dbimages.global_more_help == False)):
            return

        self.messagetimer.Stop()
        if self.statusBar:
            self.statusBar.SetStatusText(text)
        # if self.statusBar.IsShown():
        #     self.statusBar.SetStatusText(text)
        # else:
        #     self.statusBar.Show()
        #     self.statusBar.SetStatusText(text)
        # print "message timer start"
        if last == False:
            self.messagetimer.Start(5000)

    def OnMessageTimer(self, event):
        # print "message timer stop"
        self.messagetimer.Stop()
        if self.statusBar:
            self.statusBar.SetStatusText("")
        # self.statusBar.Hide()

    def OnInputText(self, event):
        """True | False"""
        input_string = self.text_input_percent_size.GetValue().strip()
        if input_string.isdigit():
            percent = int(input_string)
            if (self.image_w != 0 and self.image_h != 0):
                im_w = self.image_w * percent / 100
                im_h = self.image_h * percent / 100
                string = str(im_w) + '*' + str(im_h)
                self.text_input_size.SetValue(string)

    def view_image_update(self):
        if (self.merge_checkbox.GetValue() == True):
            # auto display merge image
            self.parse_input_string()
            self.wx_merge_images()
            self.image_view.SetImageObject(self.big_image)
        else:
            select = self.listbox.GetSelection()
            # name = dbimages.image_selects[select]
            name = dbimages.image_selects_get_name(select)
            filename = dbimages.input_path + os.sep + name
            self.image_view.SetValue(filename)
            self.__output_image_size(filename)

    def OnListBoxUp(self, event):
        # print "box up"
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        up_index = select - 1
        # print("total: %d, next_index: %d" % (total, up_index))
        if up_index >= 0:
            # print "goto up"
            name = self.listbox.GetString(select)
            up_name = self.listbox.GetString(up_index)
            self.listbox.SetString(select, up_name)
            self.listbox.SetString(up_index, name)
            dbimages.image_selects[up_index][1] = name 
            dbimages.image_selects[select][1] = up_name 
            self.listbox.SetSelection(up_index)
            string = _("image up: ") + name
            self.SetMessageValue(string)
            if (self.merge_checkbox.GetValue() == True):
                # auto display merge image
                self.parse_input_string()
                self.wx_merge_images()
                self.image_view.SetImageObject(self.big_image)

    def OnListBoxDown(self, event):
        # switch with next item
        # print "box down"
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        next_index = select + 1
        # print("total: %d, next_index: %d" % (total, next_index))
        if next_index < total:
            # print "goto next"
            name = self.listbox.GetString(select)
            next_name = self.listbox.GetString(next_index)
            self.listbox.SetString(select, next_name)
            self.listbox.SetString(next_index, name)
            dbimages.image_selects[next_index][1] = name 
            dbimages.image_selects[select][1] = next_name 
            self.listbox.SetSelection(next_index)
            string = _("image down: ") + name
            self.SetMessageValue(string)
            if (self.merge_checkbox.GetValue() == True):
                # auto display merge image
                self.parse_input_string()
                self.wx_merge_images()
                self.image_view.SetImageObject(self.big_image)

    def OnCheckBox(self, event):
        """True | False"""
        # print "OnCheckBox ---"
        # print self.merge_checkbox.GetValue()
        self.view_image_update()

    def merge_ui_listbox_update(self):
        #grep listbox data
        for element in dbimages.image_selects:
            self.listbox.Append(element[1])
        self.listbox.SetSelection(0)
        self.list_num = dbimages.image_selects_count()
        self.list_label_num.SetLabel("Num: " + str(self.list_num))

    def OnMerge(self, event):
        # print "click on merge start parse"
        self.parse_input_string()
        # print "after parse start merge"
        self.wx_merge_images()
        self.image_view.SetImageObject(self.big_image)
        self.merge_save_to_file()
        self.merge_done = True

    def wx_merge_images(self):
        images_num = dbimages.image_selects_count()
        max_cols = self.max_cols
        result, rest = divmod(images_num, self.max_cols)
        if rest > 0:
            max_rows = result + 1
        else:
            max_rows = result

        max_width = self.input_width * max_cols
        max_height = self.input_height * max_rows
        to_width = self.input_width
        to_height = self.input_height
        
        # image_space = 10
        # use can define merge space
        image_space = dbimages.current["merge_space"]
        # print ("max_width: %d, max_erge_space, pos=(5,1), span=(1,2),flagheight: %d, to_width: %d, to_height: %d, images_num: %d, max_rows: %d, max_cols: %d" % (max_width, max_height, to_width, to_height, images_num, max_rows, max_cols))

        self.big_image = wx.EmptyImage(max_width, max_height)
        self.big_image.Replace(0,0,0,255,255,255)

        x = y = width = height = index = 0
        for i in range(max_rows):
            x = 0
            height += to_height
            for ii in range(max_cols):
                if index < images_num:
                    name = dbimages.image_selects_get_name(index)
                    index += 1
                else:
                    # print "no images file, error"
                    break
                filename = dbimages.input_path + os.sep + name
                # print filename + " ---- " + str(index)
                image = wx.Image(filename, wx.BITMAP_TYPE_ANY)

                iwidth, iheight = image.GetSize()
                new_width, new_height = self.scale_size(iwidth, iheight, to_width-image_space, to_height-image_space)
                sc_image = image.Rescale(new_width, new_height, wx.IMAGE_QUALITY_HIGH)
                # print ("after scale_size, new size: %d, %d" % (new_width, new_height))
                diffx = (to_width - new_width)/2   # center calc
                diffy = (to_height - new_height)/2   # center calc
                if x == 0:
                    width = to_width
                    box_width = new_width
                else:
                    box_width = x + new_width
                    width +=  to_width

                if y == 0:
                    box_height = new_height
                else:
                    box_height = y + new_height

                    # print "sc_image size: ", sc_image.GetSize()
                box1 = (x, y, width, height)
                # print box1
                box = (x+diffx, y+diffy, box_width+diffx, box_height+diffy)
                # print box

                self.big_image.Paste(sc_image,x+diffx, y+diffy)
                x += to_width
                # print "skip to y"
            y += to_height

    def merge_save_to_file(self):
        # print "merge_save_to_file()"
        if self.big_image:
            output_path = dbimages.output_path
            if not os.path.isdir(output_path):
                # print " os.mkdir " + output_path
                os.mkdir(output_path)

            filename = output_path + os.sep + self.out_filename
            name, ext = os.path.splitext(self.out_filename)
            ext = ext.lower()
            if ext == "jpg":
                self.big_image.SaveFile(filename, type=wx.BITMAP_TYPE_JPEG)
            elif ext == "png":
                self.big_image.SaveFile(filename, type=wx.BITMAP_TYPE_PNG)
            else:
                self.big_image.SaveFile(filename, type=wx.BITMAP_TYPE_JPEG)

            self.__output_image_size(filename)

    def __output_image_size(self, filename):
        # print "try get file size"
        try:
            filesize = os.path.getsize(filename)/1024
        except:
            os.error
            return
        im = wx.Image(filename, wx.BITMAP_TYPE_ANY)
        self.image_w, self.image_h = im.GetSize()
        # print "output self.big_image.GetSize()"
        # print filesize
        string = "  " + str(self.image_w) + " * " + str(self.image_h) + "    " + str(filesize) + "k"
        self.label_image_size.SetLabel(string)        

    def parse_input_string(self):
        self.max_width = 0
        self.max_height = 0
        self.input_width = 0
        self.input_height = 0
        self.input_cols = 0
        self.out_filename = ""

        input_string = self.text_input_size.GetValue().strip()
        format_sep = '*'
        if input_string.find('X') > -1:
            format_sep = 'X'
        elif input_string.find('x') > -1:
            format_sep = 'x'

        li_w_h = input_string.split(format_sep)
        str_num = len(li_w_h)
        if str_num >= 2:
            if li_w_h[0].isdigit():
                self.input_width = int(li_w_h[0])
            if li_w_h[1].isdigit():
                self.input_height = int(li_w_h[1])
            if (self.input_width == 0 or self.input_height == 0):
                # print "h else"
                self.input_width = 800
                self.input_height = 600
            self.text_input_size.SetValue(str(self.input_width)+"*"+str(self.input_height))
        else:
            # print "meet error, need fix error data as default"
            self.text_input_size.SetValue(str(self.input_width)+"*"+str(self.input_height))
        # parse self.text_max_cols
        input_string = self.text_input_cols.GetValue().strip()
        # print ("input cols: ", input_string)
        if input_string.isdigit():
            self.max_cols = int(input_string)
            # print self.max_cols
        else:
            # print "max cols is error, set to default value: 2"
            self.text_input_cols.SetValue("2")
            self.max_cols = 2

        # parse self.text_filename
        input_string = self.text_filename.GetValue().strip()
        jpeg_exts = [".jpeg", ".jpg", ".JPEG", ".JPG", ".PNG", "png"]

        if anyTrue(input_string.endswith, jpeg_exts):
            self.out_filename = input_string
        else:
            input_string = input_string.strip()
            if input_string.find('.') > -1:
                li = input_string.split('.')
                if li[0]:
                    self.out_filename = li[0] + ".jpg"
                else:
                    print("list error")
            else:
                self.out_filename = input_string + ".jpg"

                # print "out filename: ", self.out_filename
                # print ("parse result: width, height, cols: ", self.max_width, self.max_height, self.max_cols)

    def scale_size(self, s_width, s_height, to_width, to_height):
        xfactor = float(to_width) / s_width
        yfactor = float(to_height) / s_height

        if xfactor < 1.0 and xfactor < yfactor:
            scale = xfactor
        elif yfactor < 1.0 and yfactor < xfactor:
            scale = yfactor
        else:
            scale = xfactor
            #scale = 1.0

        #print scale
        out_width = int(scale*s_width)
        out_height = int(scale*s_height)

        return (out_width, out_height)

    def OnClose(self, event):
        # print "close merge frame"
        if self.merge_done == True:
            dbimages.image_selects_clear()
            self.main_frame.ListBoxDataUpdate()
            self.merge_done == False
        self.Destroy()
        if self.main_frame:
            self.main_frame.Show(True)
        working_reset_mode()
        # gl.image_object = None

    def OnListBox(self, event):
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        # print "click on listbox, select: ", select, "total: ", total
        if (select == -1):
            #self.image_view.SetValue("")
            return
        if (self.merge_checkbox.GetValue() == True):
            # auto display merge image
            self.parse_input_string()
            self.wx_merge_images()
            self.image_view.SetImageObject(self.big_image)

        else:
            #select = self.listbox.GetSelection()
            name = dbimages.image_selects_get_name(select)
            filename = dbimages.input_path + os.sep + name
            self.image_view.SetValue(filename)
            self.__output_image_size(filename)

class SystemPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(dbimages.sys_color)

        label_lang = wx.StaticText(self, -1, _("Language"))
        self.radio_zh = wx.RadioButton(self, -1, "中文", style=wx.RB_GROUP)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioLanguage, self.radio_zh)
        self.radio_en = wx.RadioButton(self, -1, "English")
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioLanguage, self.radio_en)

        label_format = wx.StaticText(self, -1, _("photo format"))
        self.radio_jpg = wx.RadioButton(self, -1, "jpg", style=wx.RB_GROUP)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioFormat, self.radio_jpg)
        self.radio_png = wx.RadioButton(self, -1, "png")
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioFormat, self.radio_png)

        label_w_h = wx.StaticText(self, -1, _("default width height"))
        self.text_w_h = wx.TextCtrl(self, -1, "", size=(200, -1))

        label_slide_time = wx.StaticText(self, -1, _("default slide time"))
        self.text_slide_time = wx.TextCtrl(self, -1, "", size=(200, -1))

        label_quick_skip_num = wx.StaticText(self, -1, _("Quick skip num"))
        self.text_quick_skip_num = wx.TextCtrl(self, -1, "", size=(200, -1))

        label_merge_space = wx.StaticText(self, -1, _("Merge Space"))
        self.text_merge_space = wx.TextCtrl(self, -1, "", size=(200, -1))

        label_open_help = wx.StaticText(self, -1, _("default open help"))
        self.checkbox_more_help = wx.CheckBox(self, -1, "More")
        self.checkbox_little_help = wx.CheckBox(self, -1, "Little")
        self.Bind(wx.EVT_CHECKBOX, self.OnMoreCheckBox, self.checkbox_more_help)
        self.Bind(wx.EVT_CHECKBOX, self.OnLittleCheckBox, self.checkbox_little_help)

        label_title = wx.StaticText(self, -1, _("System Setup"))
        label_title.SetFont(dbimages.sys_font)
        # button_save = wx.Button(self, -1, label=_("Save"))
        # self.Bind(wx.EVT_BUTTON, self.OnSave, button_save)
        button_close = wx.Button(self, -1, label=_("Close"))
        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)

        vbox_top = wx.BoxSizer(wx.VERTICAL)

        vbox_top.Add((15,15))
        vbox_top.Add(label_title, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_top.Add((15,15))
        vbox_top.Add((15,15))

        vbox = wx.GridBagSizer(hgap=10, vgap=20)
        vbox.Add(label_lang, pos=(0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER, border=5)
        vbox.Add(self.radio_zh, pos=(0,1), flag=wx.ALIGN_LEFT, border=5)
        vbox.Add(self.radio_en, pos=(0,2), flag=wx.ALIGN_LEFT, border=5)
        vbox.Add(label_format, pos=(1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER, border=5)
        vbox.Add(self.radio_jpg, pos=(1,1), flag=wx.ALIGN_LEFT, border=5)
        vbox.Add(self.radio_png, pos=(1,2), flag=wx.ALIGN_LEFT, border=5)

        vbox.Add(label_w_h, pos=(2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER, border=5)
        vbox.Add(self.text_w_h, pos=(2,1), span=(1,2), flag=wx.ALIGN_CENTER, border=5)
        vbox.Add(label_slide_time, pos=(3,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER, border=5)
        vbox.Add(self.text_slide_time, pos=(3,1), span=(1,2), flag=wx.ALIGN_CENTER, border=5)
        vbox.Add(label_quick_skip_num, pos=(4,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER, border=5)
        vbox.Add(self.text_quick_skip_num, pos=(4,1), span=(1,2),flag=wx.ALIGN_CENTER, border=5)
        vbox.Add(label_merge_space, pos=(5,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER, border=5)
        vbox.Add(self.text_merge_space, pos=(5,1), span=(1,2),flag=wx.ALIGN_CENTER, border=5)
        vbox.Add(label_open_help, pos=(6,0), flag=wx.ALIGN_RIGHT, border=5)
        vbox.Add(self.checkbox_more_help, pos=(6,1), flag=wx.ALIGN_LEFT, border=5)
        vbox.Add(self.checkbox_little_help, pos=(6,2), flag=wx.ALIGN_LEFT, border=5)
        # vbox.Add(self.checkbox_more_help, pos=(5,1), span=(1,2), flag=wx.ALIGN_LEFT, border=5)
        # vbox.Add(self.checkbox_little_help, pos=(5,2), span=(1,2), flag=wx.ALIGN_LEFT, border=5)

        vbox_top.Add(vbox, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add((15,15))
        vbox_top.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_top.Add((15,15))

        vbox_top.Add(button_close, 0, flag=wx.ALIGN_CENTER)

        # vbox_cmd = wx.BoxSizer(wx.HORIZONTAL)
        # vbox_cmd.Add(button_save, 0, wx.ALIGN_CENTER)
        # vbox_cmd.Add(button_close, 0, wx.ALIGN_CENTER)

        self.SetSizer(vbox_top)
        self.Layout()
        #vbox_top.Fit(self)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.updateConfigUI()

    def OnClose(self, event):
        # print "setup close"
        self.SaveUIData()
        self.GetTopLevelParent().Destroy()

    def OnRadioLanguage(self, event):
        radioSelected = event.GetEventObject()
        text = radioSelected.GetLabel()
        dbimages.current["lang"] = text
        # print dbimages.current["lang"].encode("utf-8")
        # print text.encode("utf-8")

        # print " change lang "
        # if L:
        #     del L
        #     L = None
        #     L = wx.Locale()
        #     basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
        #     localedir = os.path.join(basepath, "locale")
        #     langid = wx.LANGUAGE_CHINESE_SIMPLIFIED 
        #     domain = "newimages"             # the translation file is messages.mo
        #     # Set locale for wxWidgets
        #     #        mylocale = wx.Locale(langid)
        #     L.Init(wx.LANGUAGE_DEFAULT)
        #     L.AddCatalogLookupPathPrefix(localedir)
        #     L.AddCatalog(domain)

        # if text == u"en":
        #     print "english"
        #     langid = wx.LANGUAGE_DEFAULT
        # elif text == u"中文":
        #     langid = wx.LANGUAGE_CHINESE_SIMPLIFIED
        #     print "chinese"
        # else:
        #     langid = wx.LANGUAGE_DEFAULT
        #     print "default english"

    def OnRadioFormat(self, event):
        radioSelected = event.GetEventObject()
        text = radioSelected.GetLabel()
        # print text.encode("utf-8")
        if dbimages.current["image_format"] != text:
            # print "new radio and set"
            dbimages.current["image_format"] = text
        else :
            # print "on same skip"
            return

        pass

    def OnMoreCheckBox(self, event):
        result = self.checkbox_more_help.GetValue()
        if result:
            dbimages.current["more_help"] = 1
            dbimages.global_more_help = True
            self.checkbox_little_help.SetValue(False)
            dbimages.current["little_help"] = 0
            dbimages.global_little_help = False
        else:
            dbimages.current["more_help"] = 0
            dbimages.global_more_help = False

        # result = self.checkbox_little_help.GetValue()
        # if result:
        #     dbimages.current["little_help"] = 1
        #     dbimages.global_little_help = True
        # else:
        #     dbimages.current["little_help"] = 0
        #     dbimages.global_little_help = False

    def OnLittleCheckBox(self, event):
        result = self.checkbox_little_help.GetValue()
        if result:
            dbimages.current["little_help"] = 1
            dbimages.global_little_help = True
            self.checkbox_more_help.SetValue(False)
            dbimages.current["more_help"] = 0
            dbimages.global_more_help = False
        else:
            dbimages.current["little_help"] = 0
            dbimages.global_little_help = False

        # result = self.checkbox_more_help.GetValue()
        # if result:
        #     dbimages.current["more_help"] = 1
        #     dbimages.global_more_help = True
        # else:
        #     dbimages.current["more_help"] = 0
        #     dbimages.global_more_help = False

    def SaveUIData(self):
        self.SaveUITextValue()
        dbimages.ConfigSave()

    def updateConfigUI(self):
        """update current dict to config window"""
        # print "update config ui"
        if dbimages.current["lang"] == "English":
            self.radio_en.SetValue(True)
            pass
        elif dbimages.current["lang"] == "中文":
            self.radio_zh.SetValue(True)
            pass

        if dbimages.current["image_quality"] == "high":
            pass
        elif dbimages.current["image_quality"] == "middle":
            pass
        elif dbimages.current["image_quality"] == "low":
            pass

        if dbimages.current["image_format"] == "jpg":
            self.radio_jpg.SetValue(True)
            pass
        elif dbimages.current["image_format"] == "png":
            self.radio_png.SetValue(True)
            pass

        self.text_w_h.SetValue(str(dbimages.current["image_width"]) + "*" + str(dbimages.current["image_height"]))
        self.text_slide_time.SetValue(str(dbimages.current["slideshow_timeout"]))
        self.text_quick_skip_num.SetValue(str(dbimages.current["quick_skip_num"]))
        self.text_merge_space.SetValue(str(dbimages.current["merge_space"]))

        if dbimages.current["more_help"] == 0:
            self.checkbox_more_help.SetValue(False)
            pass
        elif dbimages.current["more_help"] == 1:
            self.checkbox_more_help.SetValue(True)
            pass

        if dbimages.current["little_help"] == 0:
            self.checkbox_little_help.SetValue(False)
            pass
        elif dbimages.current["little_help"] == 1:
            self.checkbox_little_help.SetValue(True)
            pass

    def SaveUITextValue(self):
        """update current dict to config window"""
        input_string = self.text_w_h.GetValue()
        format_sep = '*'
        if input_string.find('X') > -1:
            format_sep = 'X'
        elif input_string.find('x') > -1:
            format_sep = 'x'

        input_parts = input_string.split(format_sep)
        input_parts=[input_parts[x].strip() for x in range(len(input_parts))]
        if len(input_parts) >= 2:
            if input_parts[0].isdigit():
                dbimages.current["image_weight"] = int(input_parts[0])
            if input_parts[0].isdigit():
                dbimages.current["image_height"] = int(input_parts[1])

        input_string = self.text_slide_time.GetValue().strip()
        if input_string.isdigit():
            dbimages.current["slideshow_timeout"] = int(input_string)

        input_string = self.text_quick_skip_num.GetValue().strip()
        if input_string.isdigit():
            dbimages.current["quick_skip_num"] = int(input_string)

        input_string = self.text_merge_space.GetValue().strip()
        if input_string.isdigit():
            dbimages.current["merge_space"] = int(input_string)

        if ((dbimages.global_little_help == False) and (dbimages.global_more_help == False)):
            if self.GetTopLevelParent().main_frame.statusBar:
                self.GetTopLevelParent().main_frame.statusBar.Destroy()
                self.GetTopLevelParent().main_frame.statusBar = None
        else:
            if not self.GetTopLevelParent().main_frame.statusBar:
                self.GetTopLevelParent().main_frame.statusBar = self.GetTopLevelParent().main_frame.CreateStatusBar()
                #self.statusBar = self.CreateStatusBar()

class FamousPage(wx.Panel):
    """famous working"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(dbimages.sys_color)
        self.work_edit_state = False
        self.famous_data_changed = False
        self.famous_get_data = False
        self.current_item = 0
        self.total_item = 0
        self.famous_state = 0

        label_title = wx.StaticText(self, -1, _("Famous Info"))
        label_title.SetFont(dbimages.sys_font)
        button_up = wx.Button(self, -1, label=_("Up"))
        button_next = wx.Button(self, -1, label=_("Next"))
        self.text_current_num = wx.TextCtrl(self, -1, "", size=(40, -1), style=wx.TE_PROCESS_ENTER|wx.TE_CENTER)
        self.label_total_num = wx.StaticText(self, -1, "/", size=(40, -1))
        self.button_add = wx.Button(self, -1, label=_("Add"))
        self.button_delete = wx.Button(self, -1, label=_("Delete"))
        self.button_display_all = wx.Button(self, -1, label=_("Display All"))

        button_close = wx.Button(self, -1, label=_("Close"))
        self.text_multi_text = wx.TextCtrl(self, -1, "", size=(650, 480), style=wx.TE_MULTILINE)
        self.text_multi_text.SetFont(dbimages.sys_font)
        # multiText.SetInsertionPoint(0)

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_cmd = wx.BoxSizer(wx.HORIZONTAL)

        vbox_cmd.Add(button_up, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add(button_next, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add(self.text_current_num, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add(self.label_total_num, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add(self.button_add, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add(self.button_delete, 0, wx.ALIGN_CENTER)
        vbox_cmd.Add((15,15))
        vbox_cmd.Add(self.button_display_all, 0, wx.ALIGN_CENTER)

        vbox_top.Add((15,15))
        vbox_top.Add(label_title, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_top.Add(vbox_cmd, 0, wx.ALIGN_CENTER)
        vbox_top.Add(self.text_multi_text, 0, wx.ALIGN_CENTER)
        vbox_top.Add(wx.StaticLine(self), flag=wx.EXPAND)
        vbox_top.Add(button_close, 0, wx.ALIGN_CENTER)

        self.SetSizer(vbox_top)
        self.Layout()
        #vbox_top.Fit(self)

        # map event
        self.Bind(wx.EVT_BUTTON, self.OnFamousUp, button_up)
        self.Bind(wx.EVT_BUTTON, self.OnFamousNext, button_next)
        self.Bind(wx.EVT_BUTTON, self.OnFamousAdd, self.button_add)
        self.Bind(wx.EVT_BUTTON, self.OnFamousDelete, self.button_delete)
        self.Bind(wx.EVT_BUTTON, self.OnFamousDisplayAll, self.button_display_all)
        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)
        self.text_current_num.Bind(wx.EVT_TEXT_ENTER, self.OnInputTextEnter)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

        self.SetFocus()
        # self.FirstStart()

    def OnClose(self, event):
        self.GetTopLevelParent().Destroy()

    def KeyPress(self, event):
        pass
        event.skip()
        # print "key press"
        # if key press 0--9, a-z, set state

    def FirstStart(self):
        dbfamous.parse_famous_file_to_index()
        # print ("====== first start ======", dbfamous.famous_total_item, dbfamous.famous_total_item, len(dbfamous.famous_list))
        self.total_item = dbfamous.famous_total_item
        if (self.total_item > 0):
            self.current_item = 1
        else:
            self.current_item = 0

        self.text_multi_text.SetValue(dbfamous.famous_list_get_text_by_index(self.current_item).decode("utf-8"))
        self.text_current_num.SetValue(str(self.current_item))
        self.label_total_num.SetLabel("/"+str(self.total_item))

    def OnKeyUp(self, event):
        key = event.GetKeyCode()
        # print ("KeyPress: %d"% (key))
        # PageUp 366; PageDown 367
        if (key == wx.WXK_PAGEUP):
            if self.famous_state < 3:
              self.FamousQuickUp()
        elif (key == wx.WXK_PAGEDOWN):
            if self.famous_state < 3:
                self.FamousQuickDown()

        # print(wx.WXK_ESCAPE, wx.WXK_SPACE, wx.WXK_LEFT, wx.WXK_UP, wx.WXK_RIGHT, wx.WXK_DOWN)
        event.Skip()

    def FamousQuickUp(self):
        num = dbimages.current["quick_skip_num"]
        if (self.total_item < num) or (self.current_item == 0):
            return

        if ((self.current_item - num) > 0) and (self.current_item < self.total_item):
            self.current_item -= num
        else:
            self.current_item = 0

        self.text_multi_text.SetValue(dbfamous.famous_list_get_text_by_index(self.current_item).decode("utf-8"))
        self.text_current_num.SetValue(str(self.current_item))

    def FamousQuickDown(self):
        num = dbimages.current["quick_skip_num"]
        if (self.total_item < num) or (self.current_item == self.total_item - 1):
            return

        if ((self.current_item + num) < self.total_item and (self.current_item >= 0)):
            self.current_item += num
        else:
            self.current_item = self.total_item - 1

        self.text_multi_text.SetValue(dbfamous.famous_list_get_text_by_index(self.current_item).decode("utf-8"))
        self.text_current_num.SetValue(str(self.current_item))


    def OnFamousUp(self, event):
        self.famous_state = 1
        self.current_item = self.current_item - 1
        if self.current_item < 1:
            self.current_item = self.total_item

        self.text_multi_text.SetValue(dbfamous.famous_list_get_text_by_index(self.current_item).decode("utf-8"))
        self.text_current_num.SetValue(str(self.current_item))
        pass

    def OnFamousNext(self, event):
        self.famous_state = 2
        self.current_item = self.current_item + 1
        if self.current_item > self.total_item:
            # self.current_item = self.total_item
            self.current_item = 1

        self.text_multi_text.SetValue(dbfamous.famous_list_get_text_by_index(self.current_item).decode("utf-8"))
        self.text_current_num.SetValue(str(self.current_item))

    def OnInputTextEnter(self, event):
        input_string = self.text_current_num.GetValue().strip()
        if input_string.isdigit():
            num = int(input_string)
            if ((num > 0) and (num <= self.total_item)):
                self.current_item = num
                self.text_multi_text.SetValue(dbfamous.famous_list_get_text_by_index(self.current_item).decode("utf-8"))

    def OnFamousAdd(self, event):
        self.famous_state = 3
        if (self.work_edit_state == False):
            self.text_multi_text.SetValue("")
            self.button_add.SetLabel(_("Save"))
            self.total_item += 1
            self.current_item = self.total_item
            self.text_current_num.SetValue(str(self.current_item))
            self.label_total_num.SetLabel("/"+str(self.total_item))
            self.work_edit_state = True
        else:
            # save text to file, call famous_data
            input_string = self.text_multi_text.GetValue() + "\n"
            dbfamous.famous_add_item_by_index(-1, input_string)
            self.button_add.SetLabel(_("Add"))
            self.text_current_num.SetValue(str(self.current_item))
            self.label_total_num.SetLabel("/"+str(self.total_item))
            dbfamous.famous_file_update_by_list()
            self.work_edit_state = False
        pass


    def OnFamousDelete(self, event):
        """get current item, delete current item, back to next item if next is true"""
        # set delete tag for item, file no support delete line
        if self.famous_state == 5:
            return
        # print ("self.work_edit_state: %d" % self.work_edit_state)
        if (self.famous_state == 3) and (self.work_edit_state == True):
            self.total_item -= 1
            self.current_item = self.total_item
            self.text_multi_text.SetValue(dbfamous.famous_list_get_text_by_index(self.current_item).decode("utf-8"))
            self.text_current_num.SetValue(str(self.current_item))
            self.label_total_num.SetLabel("/"+str(self.total_item))
            return
            
        self.famous_state = 4
        self.famous_data_changed = True

        index = self.current_item 
        dbfamous.famous_remove_item_by_index(index)
        if (self.total_item > 1):
            self.total_item = self.total_item - 1
            if self.current_item > self.total_item:
                self.current_item = self.total_item

            if (index != -1):
                self.text_multi_text.SetValue(dbfamous.famous_list_get_text_by_index(self.current_item).decode("utf-8"))
                self.text_current_num.SetValue(str(self.current_item))
            else:
                self.text_multi_text.SetValue("")
                self.current_item = 0
                self.text_current_num.SetValue(str(self.current_item))                    

        # debug mode
        if self.famous_data_changed == True:
            dbfamous.famous_file_update_by_list()

        self.label_total_num.SetLabel("/"+str(self.total_item))

        pass

    def OnFamousDisplayAll(self, event):
        if self.famous_state == 5:
            self.button_display_all.SetLabel(_("Display All"))
            self.text_multi_text.SaveFile(dbimages.famous_file)
            self.FirstStart()
            self.famous_state = 0
        elif self.famous_state != 5:
            self.button_display_all.SetLabel(_("Save All"))
            self.text_multi_text.LoadFile(dbimages.famous_file)
            self.famous_state = 5

    def OnFamousText(self, event):
        pass

    def OnFamousSave(self, event):
        self.work_edit_state = False
        pass

    def OnFamousCancel(self, event):
        self.work_edit_state = False
        pass

class HelpInfoPage(wx.Panel):
    def __init__(self, parent):
        self.current_item = 0;
        self.total_item = 0;
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(dbimages.sys_color)
        if dbimages.current["lang"] == "English":
            self.help_file = os.path.join(dbimages.basepath_doc, "en", "help.txt")
        else:
            self.help_file = os.path.join(dbimages.basepath_doc, "zh", "help.txt")

        button_close = wx.Button(self, -1, label=_("Close"))

        label_title = wx.StaticText(self, -1, _("Help Info"))
        label_title.SetFont(dbimages.sys_font)
        self.text_multi_text = wx.TextCtrl(self, -1, "", size=(500, 450), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.text_multi_text.SetFont(dbimages.sys_font)

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
        vbox_top.Add((10,10))

        self.SetSizer(vbox_top)
        self.Layout()
        #vbox_top.Fit(self)

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

# Version = "1.0.0"
# newimages.info
# get version; download(update, info, package); cp;

class UpdatePage(wx.Panel):
    """this software auto update"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(dbimages.sys_color)
        self.update_path = "update"
        self.version = "1.0"
        self.web_version= "1.0"
        self.url_info = "http://face2group.com/software/newimages/newimages.html"
        # self.url_info = "http://127.0.0.1/software/newimages/newimages.html"
        self.update_url = ""
        self.update_program = ""
        self.platform = ""
        self.enable_update = False

        label_title = wx.StaticText(self, -1, _("Update Online"))
        label_title.SetFont(dbimages.sys_font)
        label_current = wx.StaticText(self, -1, _("Current version:"), size=(120, -1))
        self.text_current_version = wx.TextCtrl(self, -1, "", size=(120, -1))
        label_new = wx.StaticText(self, -1, _("New version:"), size=(120, -1))
        self.text_new_version = wx.TextCtrl(self, -1, "", size=(120, -1))
        label_features = wx.StaticText(self, -1, _("Features:"), size=(80, -1))
        self.text_features = wx.TextCtrl(self, -1, "", size=(350, 300), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.text_features.SetFont(dbimages.sys_font)
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
        self.Layout()
        #vbox_top.Fit(self)

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
            fd = open(dbimages.version_file, 'r')
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
        self.SetBackgroundColour(dbimages.sys_color)
        if dbimages.current["lang"] == "English":
            self.about_file = os.path.join(dbimages.basepath_doc, "en" ,"about.txt")
        else:
            self.about_file = os.path.join(dbimages.basepath_doc, "zh", "about.txt")

        label_title = wx.StaticText(self, -1, _("About NewImages"))
        label_title.SetFont(dbimages.sys_font)
        alipay = wx.StaticText(self, -1, "支付宝: luckrill@163.com", size=(500, -1))
        paypal = wx.StaticText(self, -1, "PayPal: luckrill@163.com", size=(500, -1))
        email = wx.StaticText(self, -1, " Email: luckrill@163.com", size=(500, -1))
        self.text_about = wx.TextCtrl(self, -1, "", size=(500, 400), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.text_about.SetFont(dbimages.sys_font)
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
        self.Layout()
        #vbox_top.Fit(self)

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
        #self.famous_page = FamousPage(self.nb)
        self.helpinfo_page = HelpInfoPage(self.nb)
        self.update_page = UpdatePage(self.nb)
        about_page = AboutPage(self.nb)


        self.nb.AddPage(self.system_page, _("System Setup"))
        #self.nb.AddPage(self.famous_page, _("Famous Setup"))
        self.nb.AddPage(self.helpinfo_page, _("Help Info"))
        self.nb.AddPage(self.update_page, _("Update"))
        self.nb.AddPage(about_page, _("About"))

        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        panel.Layout()
        #sizer.Fit(self)

        self.nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnChanged)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnChanged(self, event):
        # 0 -- 4, 5 items
        if self.current_index == 0:
            self.system_page.SaveUIData()
        self.current_index = self.nb.GetSelection()
        # print "index:" + str(index) + "; total items: " + str(dbfamous.famous_total_item)
        # if self.current_index == 1 and self.famous_page.famous_get_data == False:
        #     self.famous_page.FirstStart()
        #     self.famous_page.famous_get_data = True
        #     pass

    def OnClose(self, event):
        # print "note on close !?"
        self.GetTopLevelParent().Destroy()

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
            if first == True:
                self.mainframe.AddImageFiles(file, True)
                first = False
            else:
                self.mainframe.AddImageFiles(file, False)

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

class App(wx.App):
    """Application class."""
    def OnInit(self):

        dbimages.ConfigLoad()
        # basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
        localedir = os.path.join(dbimages.basepath, "pdoc", "locale")

        if dbimages.current["lang"] == "English":
            # langid = wx.LANGUAGE_DEFAULT
            # langid = wx.LANGUAGE_ENGLISH
            langid = wx.LANGUAGE_ENGLISH_US
        else: 
            langid = wx.LANGUAGE_CHINESE_SIMPLIFIED
        domain = "newimages"             # the translation file is messages.mo
        # Set locale for wxWidgets
        # mylocale = wx.Locale(langid)
        L.Init(langid)
        L.AddCatalogLookupPathPrefix(localedir)
        L.AddCatalog(domain)

        self.frame = Frame(startpath)
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True

# global class data
dbimages = DBimages()
dbfamous = DBfamous()

def main(start):
    app = App()
    app.MainLoop()

if __name__ == '__main__':
    startpath = ""
    # print sys.argv
    if (len(sys.argv) > 1):
        startpath = sys.argv[1]
        if os.path.isdir(startpath):
            startpath = os.path.abspath(startpath)
        else:
            if anyTrue(startpath.endswith, exts):
                startpath = os.path.dirname(startpath)
    main(startpath)