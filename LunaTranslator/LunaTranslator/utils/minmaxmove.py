import os,win32gui,subprocess,win32con,time ,win32process,win32api
from traceback import print_exc
from utils.config import globalconfig 
def minmaxmoveobservefunc(self): 
        
        self.lasthwnd=None
        self.lastfocus=None
        while(True):
                 
                
                try:
                    if self.object.textsource.pid: 
                        hwnd=self.object.textsource.hwnd
                        if hwnd!=self.lasthwnd:
                                self.lastminmax=None
                                self.lastpos=None
                        self.lasthwnd=hwnd
                        #print( win32process.GetWindowThreadProcessId(hwnd))
                        tup = win32gui.GetWindowPlacement(hwnd)
                        #print(tup)
                        rect=win32gui.GetWindowRect( hwnd) 
                        if globalconfig['focusfollow']:
                                focus=win32gui.GetForegroundWindow()
                                _focusp=win32process.GetWindowThreadProcessId(focus)[1]
                                if _focusp ==self.object.textsource.pid: 
                                        self.hookfollowsignal.emit(3,(hwnd,))
                                elif _focusp ==os.getpid():
                                        pass
                                else:
                                        self.hookfollowsignal.emit(4,(0,0)) 
                                
                        if globalconfig['minifollow']:
                                if self.lastminmax and  tup[1]!=self.lastminmax:
                                        if tup[1] == win32con.SW_SHOWMINIMIZED:
                                                self.hookfollowsignal.emit(4,(0,0)) 
                                        elif tup[1] == win32con.SW_SHOWNORMAL:
                                                self.hookfollowsignal.emit(3,(hwnd,))
                                self.lastminmax=tup[1]
                                
                        if globalconfig['movefollow']:
                                if tup[1] == win32con.SW_SHOWNORMAL:
                                        if self.lastpos and rect!=self.lastpos:  
                                                self.hookfollowsignal.emit(5,(rect[0]-self.lastpos[0],rect[1]-self.lastpos[1]))
                                        self.lastpos=rect 
                except:
                        #print_exc()
                        pass
                  
                time.sleep(0.1)