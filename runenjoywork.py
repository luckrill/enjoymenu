import os
import sys
import subprocess

class RunEnjoyWork():
    def __init__(self):
        basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
        exeable = "enjoywork.exe"
        self.app = ""
        if os.path.exists(os.path.join(basepath, exeable)):
            self.app = os.path.join(basepath, exeable)
        elif os.path.exists(os.path.join(basepath, "packages", exeable)):
            self.app = os.path.join(basepath, "packages", exeable)
        else:
            print("no found " + exeable + " error!")

    def run(self):
        if (self.app):
            subprocess.Popen(self.app.encode("gbk"), shell=True)

def main():
    runapp = RunEnjoyWork()
    runapp.run()

if __name__ == '__main__':
    main()
