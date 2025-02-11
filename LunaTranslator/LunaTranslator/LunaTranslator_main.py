
import time
filestart=time.time()    

from utils.somepath import initpath
initpath() 
import os,threading,Levenshtein,sys 
from traceback import  print_exc   
import  win32event,win32con,win32event,win32security,win32pipe,win32file,mmap 
 
from PyQt5.QtGui import QPalette,QColor
from utils.config import globalconfig ,savehook_new_list,savehook_new_data,noundictconfig,transerrorfixdictconfig,setlanguage 
import threading,win32gui 
from PyQt5.QtCore import QCoreApplication ,Qt ,QObject,pyqtSignal
from PyQt5.QtWidgets import  QApplication ,QGraphicsScene,QGraphicsView,QDesktopWidget  
from utils import somedef
from utils.minmaxmove import minmaxmoveobservefunc
from utils.simplekanji import kanjitrans
from utils.wrapper import threader 
from utils import somedef
from gui.showword import searchwordW
from gui.rangeselect    import rangeadjust

from utils.getpidlist import pid_running,getarch,getpidexe ,getpidhwnds

from textsource.copyboard import copyboard   
from textsource.textractor import textractor   
from textsource.embedded import embedded
from textsource.ocrtext import ocrtext
from textsource.txt import txt 
import  gui.selecthook    
from utils.getpidlist import getpidexe,ListProcess,getScreenRate

from utils.getpidlist import getarch
import gui.translatorUI
from queue import Queue
from gui.languageset import languageset
import zhconv,functools
import gui.transhist 
import gui.edittext
import importlib
from functools import partial  
from gui.settin import Settin 
from gui.attachprocessdialog import AttachProcessDialog
import win32event,win32con,win32process,win32api 
import re 
from utils.post import POSTSOLVE
from utils.vnrshareddict import vnrshareddict 

import pyperclip
from utils.simplekanji import kanjitrans
from embedded.rpcman3 import RpcServer
from embedded.gameagent3 import GameAgent 

 
class MAINUI(QObject) :
    startembedsignal=pyqtSignal(int,embedded)
    def startembed(self,pid,engine:embedded):  
        self.ga.hostengine=engine 
        self.ga.attachProcess(pid)  
    def startembedservice(self):
            self.rpc=RpcServer()  
            self.ga=GameAgent(self.rpc ) 
            self.rpc.engineTextReceived.connect(self.ga.sendEmbeddedTranslation)
            self.rpc.start() 
            self.startembedsignal.connect(self.startembed)
    def __init__(self,app) -> None:
        super().__init__()
        self.app=app  
        self.startembedservice()
        self.translators={}
        self.cishus={}
        self.reader=None
        self.textsource=None 
        self.rect=None  
        self.last_paste_str=''
        self.lastshowedstr=''
        self.textsource=None     
    @threader  
    def loadvnrshareddict(self,_=None):
        vnrshareddict(self)  
    def solvebeforetrans(self,content):
    
        zhanweifu=0
        mp1={} 
        mp2={}
        mp3={}
        if noundictconfig['use'] :
            for key in noundictconfig['dict']: 
                usedict=False
                if type(noundictconfig['dict'][key])==str:
                    usedict=True
                else:

                    if noundictconfig['dict'][key][0]=='0' :
                        usedict=True
                
                    if noundictconfig['dict'][key][0]==self.textsource.md5:
                        usedict=True
                     
                if usedict and  key in content:
                    xx=f'ZX{chr(ord("B")+zhanweifu)}Z'
                    content=content.replace(key,xx)
                    mp1[xx]=key
                    zhanweifu+=1
        if globalconfig['gongxiangcishu']['use']:
            for key,value in self.sorted_vnrshareddict_pre:
                
                if key in content:
                    content=content.replace(key,value['text']) 
            for key,value in self.sorted_vnrshareddict:
                
                if key in content:
                    # print(key)
                    # if self.vnrshareddict[key]['src']==self.vnrshareddict[key]['tgt']:
                    #     content=content.replace(key,self.vnrshareddict[key]['text'])
                    # else:
                    xx=f'ZX{chr(ord("B")+zhanweifu)}Z'
                    content=content.replace(key,xx)
                    mp2[xx]=key
                    zhanweifu+=1
        
        return content,(mp1,mp2,mp3)
    def solveaftertrans(self,res,mp): 
        mp1,mp2,mp3=mp
        #print(res,mp)#hello
        if noundictconfig['use'] :
            for key in mp1: 
                reg=re.compile(re.escape(key), re.IGNORECASE)
                if type(noundictconfig['dict'][mp1[key]])==str:
                    v=noundictconfig['dict'][mp1[key]]
                elif type(noundictconfig['dict'][mp1[key]])==list:
                    v=noundictconfig['dict'][mp1[key]][1]
                res=reg.sub(v,res)
        if globalconfig['gongxiangcishu']['use']:
            for key in mp2: 
                reg=re.compile(re.escape(key), re.IGNORECASE)
                res=reg.sub(self.vnrshareddict[mp2[key]]['text'],res)
            for key,value in self.sorted_vnrshareddict_post: 
                if key in res:
                    res=res.replace(key,value['text']) 
        if transerrorfixdictconfig['use']:
            for key in transerrorfixdictconfig['dict']:
                res=res.replace(key,transerrorfixdictconfig['dict'][key])
        return res

    
    def textgetmethod(self,paste_str,shortlongskip=True,embedcallback=None): 
        if type(paste_str)==str:
            if paste_str[:len('<notrans>')]=='<notrans>':
                self.translation_ui.displayraw1.emit([],paste_str[len('<notrans>'):],globalconfig['rawtextcolor'],1)
                return   
            elif paste_str[:len('<msg>')]=='<msg>':
                self.translation_ui.displaystatus.emit(paste_str[len('<msg>'):],'red',False)
                return   
        if type(paste_str)==list: 
            _paste_str='\n'.join(paste_str)
        else:
            _paste_str=paste_str
        
        if _paste_str=='' or len(_paste_str)>100000:
            if embedcallback:
                embedcallback('zhs', _paste_str) 
            return 
 
        
        if type(paste_str)==list:
            paste_str=[POSTSOLVE(_) for _ in paste_str] 
            _paste_str='\n'.join(paste_str)
        else:
            _paste_str=POSTSOLVE(paste_str) 
             
        while len(_paste_str) and _paste_str[-1] in '\r\n \t':  #在后处理之后在去除换行，这样换行符可以当作行结束符给后处理用
            _paste_str=_paste_str[:-1]  

        if _paste_str=='' or len(_paste_str)>1000 :
            if embedcallback:
                embedcallback('zhs', _paste_str) 
            return  
        if shortlongskip and _paste_str==self.last_paste_str:
            if embedcallback:
                embedcallback('zhs', _paste_str) 
            return 
        self.last_paste_str=_paste_str  
        if globalconfig['outputtopasteboard'] and globalconfig['sourcestatus']['copy']['use']==False:  
            pyperclip.copy(_paste_str)
        self.translation_ui.original=_paste_str 
        try:
            hira=self.hira_.fy(_paste_str)
        except:
            hira=[]
        self.lastshowedstr=_paste_str
        if globalconfig['isshowhira'] and globalconfig['isshowrawtext']:
              
            self.translation_ui.displayraw1.emit(hira,_paste_str,globalconfig['rawtextcolor'],2)
        elif globalconfig['isshowrawtext']:
            self.translation_ui.displayraw1.emit(hira,_paste_str,globalconfig['rawtextcolor'],1)
        else:
            self.translation_ui.displayraw1.emit(hira,_paste_str,globalconfig['rawtextcolor'],0)
        try:
            if globalconfig['autoread']:
                self.reader.read(_paste_str)
        except:
            pass
            
        skip=False 
        paste_str_solve= self.solvebeforetrans(_paste_str) 
        if shortlongskip and  (len(paste_str_solve[0])<globalconfig['minlength'] or len(paste_str_solve[0])>globalconfig['maxlength'] ):
            skip=True  
         
        
        if skip==False :  
            self.textsource.put((_paste_str,)) 
            for engine in self.translators:  
                self.translators[engine].gettask((_paste_str,paste_str_solve,skip,embedcallback)) 
        
    
         
        
    @threader
    def startreader(self,use=None,checked=True):
        if checked:
            from tts.windowstts import tts  as windowstts
            from tts.huoshantts import tts as huoshantts
            from tts.azuretts import tts as azuretts
            from tts.voiceroid2 import tts as voiceroid2
            from tts.voicevox import tts as voicevox
            ttss={'windowstts':windowstts,
                    'huoshantts':huoshantts,
                    'azuretts':azuretts,
                    'voiceroid2':voiceroid2,
                    'voicevox':voicevox}
            if use is None:
                
                for key in ttss:
                    if globalconfig['reader'][key]['use']:
                        use=key  
                        break
            if use:
                self.reader_usevoice=use
                self.reader=ttss[use]( self.settin_ui.voicelistsignal,self.settin_ui.mp3playsignal) 
            else:
                self.reader=None
        else:
            self.reader=None
    def selectprocess(self,selectedp): 
            #self.object.textsource=None
            pid,pexe,hwnd=(  selectedp)   
        
            arch=getarch(pid)
            if arch is None:
                return
            if self.textsource:
                try:
                    self.textsource.end()  
                except:
                    print_exc()
            #   
            if globalconfig['sourcestatus']['textractor']['use']:
                self.textsource=textractor(self.textgetmethod,self.hookselectdialog,pid,hwnd,pexe )  
            elif globalconfig['sourcestatus']['embedded']['use']:
                self.textsource=embedded(self.textgetmethod,self.hookselectdialog,pid,hwnd,pexe, self)  
            
            if pexe not in savehook_new_list:
                savehook_new_list.insert(0,pexe)  
            if pexe not in savehook_new_data:
                savehook_new_data[pexe]={'leuse':True,'title':os.path.basename(os.path.dirname(pexe))+'/'+ os.path.basename(pexe),'hook':[] }  
     
    #@threader
    def starttextsource(self,use=None,checked=True,waitforautoinit=False):   
        self.rect=None 
        self.translation_ui.showhidestate=False 
        self.translation_ui.refreshtooliconsignal.emit()
        self.range_ui.hide() 
        self.settin_ui.selectbutton.setEnabled(globalconfig['sourcestatus']['textractor']['use'] or globalconfig['sourcestatus']['embedded']['use']) 
        self.settin_ui.selecthookbutton.setEnabled(globalconfig['sourcestatus']['textractor']['use'] or globalconfig['sourcestatus']['embedded']['use']) 
         
        if  self.textsource: 
            if self.textsource.ending==False :
                self.textsource.end()  
            self.textsource=None
        if checked: 
            classes={'ocr':ocrtext,'copy':copyboard,'textractor':None,'embedded':None,'txt':txt} 
            if use is None:
                use=list(filter(lambda _ :globalconfig['sourcestatus'][_]['use'],classes.keys()) )
                use=None if len(use)==0 else use[0]
            if use is None:
                return
            elif use=='textractor' or use=='embedded':
                if waitforautoinit==False:     
                    self.AttachProcessDialog.showNormal() 
            elif use=='ocr':
                self.textsource=classes[use](self.textgetmethod,self)   
            else:
                self.textsource=classes[use](self.textgetmethod)
        
     
    @threader
    def starthira(self,use=None,checked=True): 
        if checked:
            hirasettingbase=globalconfig['hirasetting']
            if hirasettingbase['local']['use']:
                from hiraparse.localhira import hira 
            elif hirasettingbase['mecab']['use']:
                from hiraparse.mecab import hira 
                
            elif hirasettingbase['mojinlt']['use']:
                from hiraparse.mojinlt import hira 
             
            try:
                self.hira_=hira()  
            except:
                self.hira_=None
        else:
            self.hira_=None
    def fanyiinitmethod(self,classname):
        if os.path.exists('./LunaTranslator/translator/'+classname+'.py')==False:
            return None
        aclass=importlib.import_module('translator.'+classname).TS  
        return aclass(classname,partial(self._maybeyrengong,classname))   
     
    def prepare(self,now=None,_=None):    
        self.commonloader('fanyi',self.translators,self.fanyiinitmethod,now)
         
    def commonloader(self,fanyiorcishu,dictobject,initmethod,_type=None):
        if _type:
            self.commonloader_warp(fanyiorcishu,dictobject,initmethod,_type)
        else:
            for key in globalconfig[fanyiorcishu]: 
                self.commonloader_warp(fanyiorcishu,dictobject,initmethod,key)
    @threader
    def commonloader_warp(self,fanyiorcishu,dictobject,initmethod,_type):
        try:
            if _type in dictobject: 
                try: dictobject[_type].end() 
                except:print_exc()
                try:  del dictobject[_type]
                except:print_exc()
            if globalconfig[fanyiorcishu][_type]['use']==False:
                return
            item=initmethod(_type)
            if item:
                dictobject[_type]=item
        except:
            print_exc()
 
    def startxiaoxueguan(self,type_=None,_=None):  
        self.commonloader('cishu',self.cishus,self.cishuinitmethod,type_) 
    def cishuinitmethod(self,type_):
                try:
                    aclass=importlib.import_module('cishu.'+type_)
                    aclass=getattr(aclass,type_)
                except:
                    print_exc()
                    return 
                class cishuwrapper:
                    def __init__(self,_type) -> None:
                        self._=_type() 
                    @threader
                    def search(self,sentence):
                        try:
                            res=self._.search(sentence) 
                            if res is None or res=='':  
                                return 
                            self.callback(res)
                        except:
                            pass 
                _=cishuwrapper(aclass)
                return _
    def _singletrans(self,contentraw, needja ,res,cls ): 
                if contentraw==self.lastshowedstr:
                    self.translation_ui.displayres.emit(cls,res)
                if needja:
                    res=zhconv.convert(res,  'zh-tw' )    
                    res=kanjitrans(res)
                return res
    def _maybeyrengong(self,classname,contentraw,_,embedcallback):
        
        classname,res,mp=_
        if classname not in somedef.fanyi_pre: 
            res=self.solveaftertrans(res,mp)
        #print(classname,contentraw,_)
 
        if  globalconfig['embedded']['trans_kanji']   and embedcallback: 
            needja=True
        else:
            needja=False
        
        if classname=='premt':
            for k in res:
                self._singletrans(contentraw, needja ,res[k],k ) 
        else:
            res=self._singletrans(contentraw, needja ,res,classname)  
            if embedcallback: 
                if globalconfig['embedded']['as_fast_as_posible'] or classname==list(globalconfig['fanyi'])[globalconfig['embedded']['translator']]:    
                    embedcallback('zhs', res) 
            
        if classname not in somedef.fanyi_pre:
              
            self.textsource.put((contentraw,classname,res))
            
      

    def onwindowloadautohook(self): 
        if not(globalconfig['autostarthook'] and (globalconfig['sourcestatus']['textractor']['use'] or globalconfig['sourcestatus']['embedded']['use'])):
            return 
            
        elif self.AttachProcessDialog.isVisible():
                return 
        else:
            try:
                
                
                if   self.textsource is None:   
                        hwnd=win32gui.GetForegroundWindow()
                        pid=win32process.GetWindowThreadProcessId(hwnd)[1]
                        name_=getpidexe(pid)
                          
                
                        if name_  in savehook_new_list:   
                            lps=ListProcess()
                            for pid_real,_exe,_ in lps:
                                if _exe==name_: 
                                    
                                    if globalconfig['sourcestatus']['textractor']['use']:
                                        if 'needinserthookcode' in savehook_new_data[name_] and globalconfig['autoinserthook']:
                                            needinserthookcode=savehook_new_data[name_]['needinserthookcode']
                                        else:
                                            needinserthookcode=[]
                                        self.textsource=textractor(self.textgetmethod,self.hookselectdialog,pid_real,hwnd,name_ ,autostarthookcode=savehook_new_data[name_]['hook'],needinserthookcode=needinserthookcode)
                                    elif globalconfig['sourcestatus']['embedded']['use']:
                                        self.textsource=embedded(self.textgetmethod,self.hookselectdialog,pid_real,hwnd,name_  ,self)
                                    break
                
                else: 
                    pid=self.textsource.pid
                    hwnd=self.textsource.hwnd
                    needend=False 
                    if pid_running(pid)==False :
                        needend=True
                    elif win32process.GetWindowThreadProcessId( hwnd )[0]==0: 
                            time.sleep(0.5)
                            if self.textsource.pid==pid and   pid_running(pid)==False:
                                needend=True
                            else: 
                                fhwnd=win32gui.GetForegroundWindow()
                                if win32process.GetWindowThreadProcessId( fhwnd )[0]==pid:
                                    self.textsource.hwnd=fhwnd
                                else:
                                    pidhwnd=getpidhwnds(pid)
                                    if len(pidhwnd)==1:
                                        self.textsource.hwnd=pidhwnd[0]
                    if needend:
                        self.textsource.end( )  
                        self.textsource=None  
            except:
                        pass
                        #print_exc()
    def setontopthread(self):
        while True:
            #self.translation_ui.keeptopsignal.emit() 
            
            try:  
               
                if globalconfig['forcekeepontop']:
                    hwnd=win32gui.GetForegroundWindow()
                    pid=win32process.GetWindowThreadProcessId(hwnd)[1] 
                    if pid ==os.getpid():
                        continue
                     
                    win32gui.SetWindowPos(int(self.translation_ui.winId()), win32con.HWND_TOPMOST, 0, 0, 0, 0,win32con. SWP_NOACTIVATE |win32con. SWP_NOSIZE | win32con.SWP_NOMOVE)  
                #win32gui.BringWindowToTop(int(self.translation_ui.winId())) 
            except:
                print_exc() 
            time.sleep(0.5)            
    def autohookmonitorthread(self):
        while True:
            self.onwindowloadautohook()
            time.sleep(0.5)#太短了的话，中间存在一瞬间，后台进程比前台窗口内存占用要大。。。
    def aa(self):   
        self.translation_ui =gui.translatorUI.QUnFrameWindow(self)   
        if globalconfig['rotation']==0:
            self.translation_ui.show() 
        else:
            self.scene = QGraphicsScene()
            
            self.oneTestWidget = self.scene.addWidget(self.translation_ui) 
            self.oneTestWidget.setRotation(globalconfig['rotation']*90)
            self.view = QGraphicsView(self.scene)
            self.view.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.Tool)
            self.view.setAttribute(Qt.WA_TranslucentBackground) 
            self.view.setStyleSheet('background-color: rgba(255, 255, 255, 0);')
            self.view.setGeometry(QDesktopWidget().screenGeometry())
            self.view.show()        
            
         
        self.mainuiloadafter()
        threading.Thread(target=self.setontopthread).start() 
    def mainuiloadafter(self):    
        self.localocrstarted=False 
        self.loadvnrshareddict()
        self.prepare()  
        self.startxiaoxueguan()
        self.starthira()      
        
        self.settin_ui = Settin(self)  
        
        self.startreader()  
        self.transhis=gui.transhist.transhist(self.translation_ui)  
        self.edittextui=gui.edittext.edittext(self.translation_ui)  
        self.searchwordW=searchwordW(self.translation_ui)
        self.range_ui = rangeadjust(self)   
        self.hookselectdialog=gui.selecthook.hookselect(self ,self.settin_ui) 
        self.AttachProcessDialog=AttachProcessDialog(self.settin_ui,self.selectprocess,self.hookselectdialog)
          
        threading.Thread(target=self.autohookmonitorthread).start()    
        threading.Thread(target=minmaxmoveobservefunc,args=(self.translation_ui,)).start()   
        
        self.starttextsource(waitforautoinit=True)  
    def checklang(self):
        if  globalconfig['language_setted_2.4.5']==False:
            
            x=languageset(somedef.language_list_show)
            x.exec()
            globalconfig['language_setted_2.4.5']=True
            globalconfig['languageuse']=x.current
            globalconfig['tgtlang3']=x.current
            setlanguage()
    def settheme(self):
        if globalconfig['darktheme']: 
            self.app.setStyle("fusion") 
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            self.app.setPalette(palette) 
         
if __name__ == "__main__" :
    
    
    screen_scale_rate = getScreenRate()   
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv) 
    app.setQuitOnLastWindowClosed(False)
    

    main = MAINUI(app) 
    main.screen_scale_rate =screen_scale_rate  
    
    main.settheme()
    main.checklang() 
    main.aa()


    app.exit(app.exec_())
