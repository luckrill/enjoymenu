import os
from datetime import datetime

filename = "quickmenu.txt"
filename2 = "quick2menu.txt"
data = []
def test():
    if os.path.isfile(filename):
        fd = open(filename, 'r')
        while True:
            line = fd.readline().strip()
            if not line:
                break
            #line = line.strip()
            li = line.split("::")
            nli = [str.strip() for str in li]
            if line[0] != '#':
                print(line)
                print(li)
                print(nli)

                print(("::".join(a for a in nli)))
                data.append(nli)
#            self.text_multi_text.AppendText(line)
        fd.close()
        print(data)
        print((data[0]))
        print((data[1]))
        print((data[2]))
        fd = open(filename2, 'w')
        currtime = "quickmenu write at: " + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n"
        print(currtime)
        fd.write(currtime)
        for li in data:
            line = "::".join(ele for ele in li)+"\n"
            fd.write(line)
        fd.close()
test()
