#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import shutil
import codecs
import time

mlist = [["/var/www/html/dokuwiki/data/pages/rillmessages.txt", "/var/www/html/dokuwiki/pub/message.html", 0]]
logfile = "/var/www/log/message_log.txt"

class Message():
    def __init__(self):
        for li in mlist:
            li[0] = li[0].strip()
            li[1] = li[1].strip()
            mfile = li[0]
            ofile = li[1]
            if os.path.exists(mfile):
                shutil.copy2(mfile, ofile)
                li[2] = self.get_file_mtime(mfile)
        #print mlist

    def get_file_mtime(self, filename):
        statinfo = os.stat(filename)
        return int(statinfo.st_mtime)

    def compare_mtime(self):
        for li in mlist:
            mfile = li[0]
            ofile = li[1]
            mtime = li[2]
            get_mtime = self.get_file_mtime(mfile)
            if get_mtime > mtime:
                shutil.copy2(mfile, ofile)
                self.file_log(get_mtime, mfile, ofile)

    def file_log(self, mtime, mfile, ofile):
        fd = codecs.open(logfile, mode='a', encoding="utf-8")
        fd.write("time: %s, copy file %s to %s\n" % (mtime, mfile, ofile))
        fd.close()

    def run(self):
        while True:
            time.sleep(60)
            self.compare_mtime()

def main():
    message = Message()
    message.run()

if __name__ == '__main__':
    main()
