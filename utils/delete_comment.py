import os
import shutil

filename_zh = "newmenus_zh_CN.po"
filename_en = "newmenus_en_US.po"
filename_messages = "messages.pot"

def delete_comment(filename):
    filetmp = "tmp.po"

    fd = open(filename, 'r')
    fd_tmp = open(filetmp, 'w')

    while True:
        line = fd.readline()
        if not line:
            break
        if line.startswith("#:"):
            continue
        fd_tmp.write(line)

    fd.close()
    fd_tmp.close()
    shutil.copy(filetmp, filename)

if __name__ == "__main__":
    delete_comment(filename_messages)
    delete_comment(filename_zh)
    delete_comment(filename_en)
