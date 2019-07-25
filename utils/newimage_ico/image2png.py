#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import os

def image2png(filename):
    name, ext = os.path.splitext(filename)
    im = wx.Image(filename, wx.BITMAP_TYPE_ANY)

    newfilename = name + "_128" + ".png"
    out_im = im.Rescale(128, 128, wx.IMAGE_QUALITY_HIGH)
    out_im.SaveFile(newfilename, wx.BITMAP_TYPE_PNG)

    newfilename = name + "_64" + ".png"
    out_im = im.Rescale(64, 64, wx.IMAGE_QUALITY_HIGH)
    out_im.SaveFile(newfilename, wx.BITMAP_TYPE_PNG)

    newfilename = name + "_48" + ".png"
    out_im = im.Rescale(48, 48, wx.IMAGE_QUALITY_HIGH)
    out_im.SaveFile(newfilename, wx.BITMAP_TYPE_PNG)

    newfilename = name + "_32" + ".png"
    out_im = im.Rescale(32, 32, wx.IMAGE_QUALITY_HIGH)
    out_im.SaveFile(newfilename, wx.BITMAP_TYPE_PNG)

    newfilename = name + "_16" + ".png"
    out_im = im.Rescale(16, 16, wx.IMAGE_QUALITY_HIGH)
    out_im.SaveFile(newfilename, wx.BITMAP_TYPE_PNG)

if __name__ == '__main__':
    image2png("newimages.jpg")
