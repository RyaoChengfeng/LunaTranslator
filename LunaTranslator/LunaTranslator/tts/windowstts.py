
from utils.subproc import subproc
from utils.config import globalconfig  
import subprocess,threading
class tts():
    
    def __init__(self,showlist ,_): 
                 
        p=subproc('./files/tts/tts_l.exe',stdout=subprocess.PIPE )
        
        count=str(p.stdout.readline(),encoding='utf8')
        count=count.replace('\r','').replace('\n','')
        count=int(count)
        self.voicelist=[]
        for i in range(count):

             
            res=str(p.stdout.readline(),encoding='utf8').replace('\r','').replace('\n','')
            self.voicelist.append(res.split('\\')[-1]) 
        showlist.emit(self.voicelist)
        if  len(self.voicelist)>0 and globalconfig['reader']['windowstts']['voice'] not in self.voicelist:  
            globalconfig['reader']['windowstts']['voice']=self.voicelist[0]
        self.speaking=None
    def read(self,content):
        threading.Thread(target=self.read_t,args=(content,)).start()
    def read_t(self,content): 
        if len(content)==0:
            return
        if len(self.voicelist)==0:
            return 
        if globalconfig['reader']['windowstts']['voice'] not in self.voicelist:
            return
        i=self.voicelist.index(globalconfig['reader']['windowstts']['voice'])
         
        if self.speaking:
            self.speaking.kill()
                 

        self.speaking=subproc(f'./files/tts/tts_s.exe {i} {globalconfig["ttscommon"]["rate"]} {globalconfig["ttscommon"]["volume"]} "{content}"',stdout=subprocess.PIPE  )
        
      