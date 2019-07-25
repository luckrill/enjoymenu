import os
import sys
import subprocess

class RunNewMenus():
    def __init__(self):
        basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
        exeable = "newmenus.exe"
        self.newmenus = ""
        if os.path.exists(os.path.join(basepath, exeable)):
            self.newmenus = os.path.join(basepath, exeable)
        elif os.path.exists(os.path.join(basepath, "packages", exeable)):
            self.newmenus = os.path.join(basepath, "packages", exeable)
        else:
            print("no found " + exeable + " error!")

    def run(self):
        if (self.newmenus):
            subprocess.Popen(self.newmenus.encode("gbk"), shell=True)

def main():
    runnewmenus = RunNewMenus()
    runnewmenus.run()

if __name__ == '__main__':
    main()
