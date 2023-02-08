import threading ,hashlib
import time,sqlite3,json,os
from traceback import print_exc
from utils.config import globalconfig
class basetext:
    def __init__(self,textgetmethod,md5,prefix)  :  
        self.textgetmethod=textgetmethod  
        self.ending=False
        self.md5,self.prefix=md5,prefix
        self.t=threading.Thread(target=self.gettextthread_)
        self.t.setDaemon(True)
        self.t.start()
        #self.sqlfname='./transkiroku/'+self.prefix+'.sqlite'
        self.sqlfname_all='./translation_record/'+self.prefix+'.pretrans_common.sqlite'
        
        try:
            
            # self.sqlwrite=sqlite3.connect(self.sqlfname,check_same_thread = False, isolation_level=None)
            self.sqlwrite2=sqlite3.connect(self.sqlfname_all,check_same_thread = False, isolation_level=None)
            # try:
            #     self.sqlwrite.execute('CREATE TABLE artificialtrans(id INTEGER PRIMARY KEY AUTOINCREMENT,source TEXT,machineTrans TEXT,userTrans TEXT);')
            # except:
            #     pass
            try:
                self.sqlwrite2.execute('CREATE TABLE artificialtrans(id INTEGER PRIMARY KEY AUTOINCREMENT,source TEXT,machineTrans TEXT);')
            except:
                pass
        except:
            print_exc
    def checkmd5prefix(self,pname):
        with open(pname,'rb') as ff:
            bs=ff.read() 
        md5=hashlib.md5(bs).hexdigest()
        prefix= md5+'_'+os.path.basename(pname).replace('.'+os.path.basename(pname).split('.')[-1],'') 
        return md5,prefix
    def gettextthread_(self):
        while True:
            if self.ending: 
                break 
            if globalconfig['autorun']==False  :
                self.ignoretext()
                time.sleep(0.1)
                continue

            #print(globalconfig['autorun'])
            try:
                t=self.gettextthread()
                if t and globalconfig['autorun']:
                    if type(t)==str:
                        self.textgetmethod(t) 
                    else:
                        self.textgetmethod(*t)
            except: 
                print_exc() 
            
            
    def ignoretext(self):
        pass
    def gettextthread(self):
        pass
    def runonce(self):
        pass
    def end(self):
        self.ending=True
 