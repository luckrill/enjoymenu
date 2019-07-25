#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import sys

#type = sys.getfilesystemencoding()

ori_path="D:\mywork\dev_down\Links"
out_path="D:\mywork\dev_down\mvess_png"

#print(os.listdir(ori_path)).encode(type)

files = os.listdir(ori_path)

for file in files:
    #print file.decode("gbk")
    name, ext = file.split(".")
    #print name.decode("gbk")
    png_file = name+".png"
    #print(png_file).decode("gbk")
    ori_file = (ori_path + file).decode("gbk")
    out_file = (out_path + os.sep  + png_file).decode("gbk")
    cmd = "convert.exe " + '"'+ ori_file + '" ' + '"'+ "123.png" +  '"'
    print(cmd.decode("gbk"))
    os.system(cmd)

