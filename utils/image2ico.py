#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import os

def image2ico(filename):
    name, ext = os.path.splitext(filename)
    newfilename = name + ".ico"
    im = wx.Image(filename, wx.BITMAP_TYPE_ANY)
    out_im = im
#    out_im = im.Rescale(32, 32, wx.IMAGE_QUALITY_HIGH)
    out_im.SaveFile(newfilename, wx.BITMAP_TYPE_ICO)

if __name__ == '__main__':
    image2ico("d:/develop-icon-orange.png")
