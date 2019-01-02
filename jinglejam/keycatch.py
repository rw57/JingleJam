#!/usr/bin/env python
"""
Run this program with a OGG file argument. Push keys as you listen
to the music and it'll output the CSV with a timestamp and the key
you pushed. Use this to 'tag' the music.

Based on the included pygame tutorial
"""


#Import Modules
import os, pygame, sys, argparse
from pygame.locals import *
from pygame.compat import geterror

if not pygame.mixer: print ('Warning, sound disabled')

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')



def main(argv):
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""

    parser = argparse.ArgumentParser()
    #parser.add_argument("--verbose","-v",default=0,action="count")
    parser.add_argument("--output","-o",default=None)
    parser.add_argument("--skip","-s",default=None,type=int)
    parser.add_argument("file",nargs='?')
    args = parser.parse_args()

    if args.output is None:
        outfo = sys.stdout
    else:
        outfo = open(args.output,"a")

#Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((468, 260))
    pygame.display.set_caption('Key Catch')
    #pygame.mouse.set_visible(0)

#Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

#Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

    font = pygame.font.SysFont('liberationmono',80)

#Prepare Game Objects
    #clock = pygame.time.Clock()
    #whiff_sound = load_sound('whiff.wav')
    #punch_sound = load_sound('punch.wav')
    #chimp = Chimp()
    #fist = Fist()
    #allsprites = pygame.sprite.RenderPlain((fist, chimp))

    skipoffset = 0
    if args.file is not None:
        #print("loading... %s"%(args.file))
        pygame.mixer.music.load(args.file)
        pygame.mixer.music.set_volume(1.0)
        outfo.write("-,start,play %s\n"%(repr(args.file)))
        pygame.mixer.music.play(0)
        if args.skip:
            print("skipping ahead to %d"%(args.skip))
            pygame.mixer.music.set_pos(args.skip)
            skipoffset = args.skip*1000
        pygame.mixer.music.set_endevent(USEREVENT+1)

    pygame.time.set_timer(USEREVENT,100)

#Main Loop
    starttime = pygame.time.get_ticks()
    going = True
    while going:

        event = pygame.event.wait()
        if args.file is not None and pygame.mixer.music.get_busy():
            currenttime = pygame.mixer.music.get_pos() + skipoffset
        else:
            currenttime = pygame.time.get_ticks() - starttime
        if event.type == QUIT:
            going = False
        elif event.type == USEREVENT:
            s = font.render("%08d"%(currenttime),1,(255,255,255),(0,0,0))
            screen.blit(s,(15,15))
            pygame.display.flip()
        elif event.type == USEREVENT+1:
            #outfo.write("%d,end,end\n"%(pygame.mixer.music.get_pos()+skipoffset))
            going = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                going = False
            if (event.key >= K_a and event.key <= K_z) or \
                    (event.key >= K_0 and event.key <= K_9):
                outfo.write("%d,%s,\n"%(\
                        currenttime,chr(event.key)))


    pygame.quit()



#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main(sys.argv[1:])
