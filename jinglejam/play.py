#!/usr/bin/env python
"""
This simple example is used for the line-by-line tutorial
that comes with pygame. It is based on a 'popular' web banner.
Note there are comments here, but for the full explanation,
follow along in the tutorial.
"""


#Import Modules
import os, pygame, sys, errno, os.path
from pygame.locals import *
from pygame.compat import geterror
import csv, shlex
import argparse
import logging
logger = logging.getLogger(__name__)

if not pygame.mixer: print ('Warning, sound disabled')

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

commit_transaction = []
command_handlers = {
        "play":lambda filename: True,
        "end":lambda:True,
        "null":lambda cmd: True,
}

global_macro_handlers = {}
macro_handlers = {}

COMMAND_MODULES = [
        ".cmds.pigpiopy",
        ".cmds.rpilocalgpio",
        ".cmds.gpioudp",
        ".cmds.wait",
        #".cmds.x10",
        ]

import importlib
for module in COMMAND_MODULES:
    mod = importlib.import_module(module,"jinglejam")
    mod.register(command_handlers,global_macro_handlers,commit_transaction)

class Define(object):
    def __init__(self,*args):
        self.args = args
    def preprocess(self,time,*args):
        return [(time,' '.join(list(self.args)+list(args)))]
def define(time,name,*args):
    logger.debug("defining macro %s args %s",name,repr(args))
    macro_handlers[name] = Define(*args)
global_macro_handlers['define'] = define



class Chase(object):
    def __init__(self, names):
        self.names = names
        self.index = -1

    def preprocess(self,time,cmd=None):
        newcmds = []
        if cmd is None or cmd=="next" or cmd=="up":
            # advance
            newcmds.append((time,self.names[self.index]+" off"))
            self.index = (self.index+1)%len(self.names)
            newcmds.append((time,self.names[self.index]+" on"))
        elif cmd=="prev" or cmd=="down":
            # advance
            newcmds.append((time,self.names[self.index]+" off"))
            self.index = (self.index-1)%len(self.names)
            newcmds.append((time,self.names[self.index]+" on"))
        elif cmd == "same":
            # if just L is called, pump the lights on again
            newcmds.append((time-60,self.names[self.index]+" off"))
            newcmds.append((time,self.names[self.index]+" on"))
        elif cmd == "reset":
            # reset chase
            self.index = -1
        elif cmd == "off" or cmd == "on":
            for name in self.names:
                newcmds.append((time,name+" "+cmd))
            # reset chase
            #self.index = -1
        else:
            # try to initializes to a particular value
            oldindex = self.index
            try:
                self.index = int(cmd,10)
                self.index = max(self.index,0)
                self.index = min(self.index,len(self.names))
                newcmds.append((time,self.names[oldindex]+" off"))
                newcmds.append((time,self.names[self.index]+" on"))
            except ValueError:
                logger.exception("bad value for level %s",cmd)
        return newcmds
def definechase(time,name,*names):
    macro_handlers[name.lower()] = Chase(names)
global_macro_handlers['definechase'] = definechase

class Level(object):
    def __init__(self, names):
        self.names = names
        self.index = 0

    def preprocess(self,time,cmd=None,extraarg=None):
        newcmds = []
        if cmd == "off":
            for name in self.names:
                newcmds.append((time,name+" "+cmd))
            return newcmds
        elif cmd == "on" or cmd == "same" or cmd is None:
            # if just L is called, pump the lights on again
            # use this to restore if a previous off has been called
            if self.index>0:
                newcmds.append((time-80,self.names[self.index-1]+" off"))
        elif cmd=="up":
            # advance
            self.index = min(self.index+1,len(self.names))
        elif cmd == "down":
            self.index = max(self.index-1,0)
        else:
            try:
                self.index = int(cmd,10)
                self.index = max(self.index,0)
                self.index = min(self.index,len(self.names))
            except ValueError:
                logger.exception("bad value for level %s",cmd)
        # now issue the new level
        for i in range(0,self.index):
            newcmds.append((time,self.names[i]+" on"))
        for i in range(self.index,len(self.names)):
            newcmds.append((time,self.names[i]+" off"))
        return newcmds
def definelevel(time,name,*names):
    macro_handlers[name.lower()] = Level(names)
global_macro_handlers['definelevel'] = definelevel

class Beat(object):
    def __init__(self, names):
        self.names = names
    def preprocess(self,time,duration):
        newcmds = []
        duration = int(duration,10)
        for name in self.names:
            newcmds.append((time,name+" on"))
            newcmds.append((time+duration,name+" off"))
        return newcmds
def definebeat(time,name,*names):
    logger.debug("definebeat name %s",name)
    macro_handlers[name.lower()] = Beat(names)
global_macro_handlers['definebeat'] = definebeat
def beat(time,duration,name,*args):
    duration = int(duration,10)
    if len(args):
        cmdon = name+' "'+('" "'.join(args))+'"'
    else:
        cmdon = name+" on"
    return [(time,cmdon),(time+duration,name+" off")]
global_macro_handlers['beat'] = beat

def parsecommand(cmdstr):
    cmdparse = shlex.split(cmdstr)
    if len(cmdparse)<1: return None, []
    cmd = cmdparse[0].lower()
    args = cmdparse[1:]
    return cmd, args

def preprocesscmd(filename,line,time,cmdstr):
    try:
        cmd,args = parsecommand(cmdstr)
        if cmd is None or cmd[0:1]=="#":
            return []
        elif cmd in command_handlers:
            logger.debug("preprocess command - raw command - '%s'", cmdstr)
            return [(filename,line,time,cmdstr)]
        elif cmd in macro_handlers:
            logger.debug("preprocess command - '%s'", cmdstr)
            if hasattr(macro_handlers[cmd],"preprocess"):
                newcmds = macro_handlers[cmd].preprocess(time,*args)
            else:
                newcmds = macro_handlers[cmd](time,*args)
            if newcmds is None: newcmds = []
            newcmds2 = []
            for time,cmdstr in newcmds:
                newcmds2.extend(preprocesscmd(filename,line,time,cmdstr))
            return newcmds2
        else:
            raise ValueError("cmd %s not found! filename %s line %d"%(cmd,filename,line))
    except:
        logger.exception("error processing %s filename %s line %s",repr(cmdstr),filename,line)
        raise

def preprocess(cmds):
    newcmds = []
    for filename,line,time,cmdstr in cmds:
        newcmds.extend(preprocesscmd(filename,line,time,cmdstr))
    newcmds.sort(key=lambda obj:obj[2])
    return newcmds


def loadfile(filename):
    logger.info("load file %s",filename)
    filedir = os.path.dirname(filename)
    csvin = csv.reader(open(filename,"r"))

    line = 0
    cmds = []
    for row in csvin:
        line+=1
        try:
            if (row[0] == "-" or row[0]==""): time = -1
            elif row[0] == "#include":
                cmds.extend(loadfile(os.path.join(filedir,row[1])))
                continue
            elif row[0][0:1] == "#":
                # commented out
                continue
            else: time = int(row[0],10)
            logger.debug("loading commands at time %d"%(time))
            for cmdstr in row[2:]:
                cmds.append((filename,line,time,cmdstr))
        except KeyboardInterrupt:
            raise
        except:
            logger.exception("error caught on line %d", line)
    return cmds

def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
    global macro_handlers

    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose","-v",default=0,action="count")
    parser.add_argument("--preprocess-only",action="store_true")
    parser.add_argument("--loop",action="store_true")
    parser.add_argument("--music-latency",default=0,type=int,help="latency in ms")
    parser.add_argument("--lock-file",
            default="/var/lock/lightshowplay")
    parser.add_argument("files",nargs="*")
    args = parser.parse_args()

    #print(repr(args))
    if args.verbose>0:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    if len(args.files)<1:
        raise SystemExit("no file to play specified!")

    # We don't really need the lock till later... but should we do it now?
    lock_file = None
    if args.lock_file:
        lock_file = args.lock_file
        try:
            lockfd = os.open(args.lock_file, os.O_CREAT | os.O_EXCL)
        except OSError as e:
            if e.errno == errno.EEXIST:
                logger.warning("lock exists! exiting...")
                sys.exit(2)
            else:
                raise
        os.close(lockfd)

    try:
        songs = []
        for filename in args.files:
            cmds = loadfile(filename)

            songs.append(cmds)

        newsongs = []
        for cmds in songs:
            logger.info("preprocessing")
            # create macro handlers for each song (to keep the
            # namespace more clean)
            macro_handlers = global_macro_handlers.copy()
            cmds = preprocess(cmds)
            newsongs.append(cmds)
            logger.info("done preprocessing")
            if args.preprocess_only:
                for filename,line,time,cmdstr in cmds:
                    sys.stdout.write("%d,,%s\n"%(time,cmdstr))
        songs = newsongs
        if args.preprocess_only:
            sys.exit(1)
                
        import platform
        if platform.system() == "Windows":
            # I get weird delays in Windows. This didn't really help but is
            # how I tested it.
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
        pygame.init()
        if platform.system() == "Windows":
            # this is necessary on windows for sound to work
            screen = pygame.display.set_mode((468, 260))
            #pygame.display.set_caption('Key Catch')
            #background = pygame.Surface(screen.get_size())
            #background = background.convert()
            #background.fill((250, 250, 250))
            #screen.blit(background, (0, 0))
            #pygame.display.flip()
#
            #font = pygame.font.SysFont('liberationmono',80)
        else:
            screen = None

        firstrun = True
        while args.loop or firstrun:
            firstrun = False
            for cmds in songs:
                starttime = pygame.time.get_ticks()
                abort = False
                playingmusic = False
                
                for filename,line,time,cmdstr in cmds:
                    cmd,cargs = parsecommand(cmdstr)
                    # on song-to-song transitions, the music can still be
                    # "playing" from the previous song so we have a flag to
                    # see if the music is playing in this song
                    if playingmusic and pygame.mixer.music.get_busy():
                        currenttime = pygame.mixer.music.get_pos() + args.music_latency
                    else:
                        currenttime = pygame.time.get_ticks() - starttime
                    if time > currenttime:
                        # We're going to delay processing, run all waiting transactions
                        for cb in commit_transaction: cb()
                        # check for a quit event
                        if screen is not None:
                            event = pygame.event.poll()
                            if event.type == pygame.QUIT:
                                abort = True
                                break

                        # need to wait
                        logger.debug("waiting for time %d",time)
                        pygame.time.delay(time-currenttime)
                    logger.debug("running cmd = %s",cmd)
                    if cmd == "play":
                        logger.info("loading %s",cargs[0])
                        pygame.mixer.music.load(cargs[0])
                        pygame.mixer.music.set_volume(1.0)
                        logger.info("playing %s",cargs[0])
                        pygame.mixer.music.play(0)
                        playingmusic = True
                    elif cmd == "fadeout":
                        sys.stdout.write("fadeing out...\n")
                        pygame.mixer.music.fadeout(2000)
                    elif cmd == "end":
                        sys.stdout.write("end!\n")
                        abort = True
                    elif cmd in command_handlers:
                        cmdhandler = command_handlers[cmd]
                        if hasattr(cmdhandler,"do"):
                            cmdhandler.do(*cargs)
                        else:
                            cmdhandler(*cargs)
                    else:
                        logger.error("unknown command %s",cmd)
            
                    if abort:
                        break
            
                if not abort:
                    # we didn't force exit...
                    # run any pending transactions
                    for cb in commit_transaction: cb()
                    # keep playing while the music is playing
                    while pygame.mixer.music.get_busy():
                        pygame.time.wait(250)

    finally:
        if lock_file:
            os.unlink(lock_file)
    pygame.quit()



#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()
