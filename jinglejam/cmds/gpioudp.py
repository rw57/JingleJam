# See the gpioudp server in the top directory of this project
# It's meant to be a fast (low-latency) way to remotely control Raspberry Pi's
# GPIO ports.

import logging
import socket, struct

logger = logging.getLogger(__name__)

udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
class GPIOUDP(object):
    def __init__(self,host):
        host,port = host.split(':')
        port = int(port)
        self.hostport = host,port
        self.mask = 0
        self.value = 0
    def setpin(self,pin,on):
        self.mask |= (1<<pin)
        if on:
            self.value |= (1<<pin)
    def send(self):
        if self.mask != 0:  #we're dirty, send!
            data = struct.pack(">III", 0x25250001, self.value, self.mask)
            udpsock.sendto(data, self.hostport)
            self.mask =0 
            self.value = 0
udphosts = []
udphostsdict = {}

def gpioudp_cmd(host,pin,cmd):
    try:
        gudp = udphostsdict[host]
    except KeyError:
        gudp = GPIOUDP(host)
        udphosts.append(gudp)
        udphostsdict[host] = gudp
    gudp.setpin(int(pin),cmd=="on")

def gpioudp_send():
    """
    Queue up all the requests and send them all at once

    The play() main loop should call this whenever the next command's
    time is in the future (when we would wait a little bit)
    """
    logger.debug("gpioudp_send")
    for gudp in udphosts:
        gudp.send()

def register(commands,macros,commits):
    commands['gpioudp'] = gpioudp_cmd
    commits.append(gpioudp_send)
