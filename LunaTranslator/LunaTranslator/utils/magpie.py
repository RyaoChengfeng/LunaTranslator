import json
  
import win32process,win32con
import os 
from utils.subproc import subproc
class Dict2Obj(dict):
    
    def __getattr__(self, key): 
        if key not in self:
            return None
        else:
            value = self[key]
            if isinstance(value,dict):
                value = Dict2Obj(value)
            return value 
 
def callmagpie( cwd,hwnd,ScaleMode,flags,captureMode):# 0x2000|\0x2|\0x200):  
         

    FlagMasks={ 
          "NoCursor":0x1,
          "AdjustCursorSpeed":0x2,
          "SaveEffectSources":0x4,
          "SimulateExclusiveFullscreen":0x8,
          "DisableLowLatency":0x10,
          "BreakpointMode":0x20,
          "DisableWindowResizing":0x40,
          "DisableDirectFlip":0x80,
          "Is3DMode":0x100,
          "CropTitleBarOfUWP":0x200,
          "DisableEffectCache":0x400,
          "DisableVSync":0x800,
          "WarningsAreErrors":0x1000,
          "ShowFPS":0x2000,
    }
    FlagMasks=Dict2Obj(FlagMasks) 
 
            
    settings=Dict2Obj(flags)
    flags=settings.NoCursor *FlagMasks.NoCursor   |\
                    settings.AdjustCursorSpeed *FlagMasks.AdjustCursorSpeed   |\
                    settings.DebugSaveEffectSources *FlagMasks.SaveEffectSources   |\
                    settings.DisableLowLatency *FlagMasks.DisableLowLatency   |\
                    settings.DebugBreakpointMode *FlagMasks.BreakpointMode   |\
                    settings.DisableWindowResizing *FlagMasks.DisableWindowResizing   |\
                    settings.DisableDirectFlip *FlagMasks.DisableDirectFlip   |\
                    settings.Is3DMode *FlagMasks.Is3DMode   |\
                    settings.CropTitleBarOfUWP *FlagMasks.CropTitleBarOfUWP   |\
                    settings.DebugDisableEffectCache *FlagMasks.DisableEffectCache   |\
                    settings.SimulateExclusiveFullscreen *FlagMasks.SimulateExclusiveFullscreen   |\
                    settings.DebugWarningsAreErrors *FlagMasks.WarningsAreErrors   |\
                    (1-settings.VSync)*FlagMasks.DisableVSync   | \
                    settings.ShowFPS *FlagMasks.ShowFPS  
      
    cwd=os.path.abspath(cwd) 
    with open(os.path.join(cwd,'ScaleModels.json'),'r')as ff:
        effectsJson= json.load(ff)    

    with open("./cache/magpieparam.txt",'w',encoding='utf8') as ff:
        ff.write(f"{cwd}\n{hwnd}\n{json.dumps(effectsJson[ScaleMode]['effects'])}\n{flags},{captureMode},{settings.CursorZoomFactor},{settings.CursorInterpolationMode},{settings.AdapterIdx},{settings.MultiMonitorUsage}")
    s=subproc('./files/magpiecmdrunner.exe  ./cache/magpieparam.txt')
    return s.pid
    # info=win32process.STARTUPINFO()
    # info.wShowWindow=win32con.SW_HIDE
    # handle=win32process.CreateProcess('./files/magpiecmdrunner.exe', './files/magpiecmdrunner.exe  ./cache/magpieparam.txt', None , None , 0 ,False , None , None ,info)
     
    # return handle[2]