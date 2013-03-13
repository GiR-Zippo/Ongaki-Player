# encoding: iso-8859-1

import string, cgi, time, MPlayer, os
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class Container():
    def __init__(self):
        self.stations = []
        self.current = 0
        
    def Load(self):
        with open("stations.txt") as f:
            temp = f.readlines()
        
        for x in temp:
            self.stations.append(x.strip())

        return
        
    def getNext(self):
        self.current = self.current +1
        return self.stations[self.current]
    
    def getPrev(self):
        self.current = self.current -1
        print self.stations
        return self.stations[self.current]
        
    def getCurrent(self):
        return self.stations[self.current]
    
    def getPlayList(self):
        return str(self.stations)

class PlayControl:
    def __init__(self):
        self.MPlayer = MPlayer.MPlayer()        
        self.pl = Container()    
        self.pl.Load()
        
        #Controls
        self.playing = 0
        self.volume = 100
        self.trackinfo = []
        
        self.MPlayer.populate()
        self.MPlayer.volume(0,1)
        return
    
    def StoreTrackInfo(self, args):
        self.trackinfo = []
        for x in args:
            if (x.strip().startswith("Name")):
                self.trackinfo.append(x.strip())
            
    def Play(self):
        self.playing = 1
        self.StoreTrackInfo(self.MPlayer.loadfile(str(self.pl.getCurrent())))
        return
        
    def Stop(self):
        self.playing = 0
        self.MPlayer.pause()
        return

    def Next(self):
        self.StoreTrackInfo(self.MPlayer.loadfile(str(self.pl.getNext())))
        return
        
    def Prev(self):
        self.StoreTrackInfo(self.MPlayer.loadfile(str(self.pl.getPrev())))
        return
    
    def SetVolume(self, val):
        self.volume = self.volume + val
        os.system ("amixer set PCM "+ str(self.volume) +"%")
        #self.MPlayer.volume(val)
        return
        
    #Helper
    def GetTitle(self):
        return str(self.pl.getCurrent())
    def GetPlaylist(self):
        return self.pl.getPlayList()
    def IsPlaying(self):
        return str(self.playing)
    def GetVolume(self):
        return str(int(self.volume))
    def GetTrackInfo(self):
        return str(self.trackinfo)
    
mplayctrl = PlayControl()

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-type',        'text/html')
            self.end_headers()
                
            self.idx = self.path[1:]

            if self.idx == "Start":
                mplayctrl.Play()
                self.path="/index.html"
            if self.idx == "Stop":
                mplayctrl.Stop()
                self.path="/index.html"
            if self.idx == "Next":
                mplayctrl.Next()
                self.path="/index.html"
            if self.idx == "Prev":
                mplayctrl.Prev()
                self.path="/index.html"
            if self.idx[:6] == "Volume":
                mplayctrl.SetVolume(float(self.idx[7:]))
                self.path="/index.html"

            if self.path.endswith(".html"):
                f = open(curdir + sep + self.path)
                self.wfile.write(f.read())
                f.close()
                return
            if self.path.endswith(".png"):
                f = open(curdir + sep + self.path) 
                self.wfile.write(f.read())
                f.close()
                return

            #The PlayerStatus
            if self.idx == "status.js":
                self.wfile.write('var mpStatus = ["' + mplayctrl.GetTitle().rstrip() + '", \
                                                  "' + str(mplayctrl.IsPlaying())    + '", \
                                                  "' + str(mplayctrl.GetVolume())    + '"];')
                self.wfile.write("var mpPlList =  "  + str(mplayctrl.GetPlaylist())  + ";")
                self.wfile.write("var mpTrackInfo = "+ str(mplayctrl.GetTrackInfo()) + ";")
            return

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

def main():
    os.system ("amixer set PCM 100%")
    try:
        server = HTTPServer(('', 3010), MyHandler)
        print 'WebPanel started...'
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()

if __name__ == '__main__':
    main()

