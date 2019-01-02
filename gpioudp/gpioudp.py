import socket, struct
import RPi.GPIO as RPiGPIO
import logging, argparse
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="UDP server for fast, remote GPIO control")
parser.add_argument('--verbose','-v',dest="verbose",action='count')
parser.add_argument('--port',dest="port",default=2525,type=int)
args = parser.parse_args()

RPiGPIO.setmode(RPiGPIO.BCM)
RPiGPIO.setwarnings(False)

# filter out here any pins we don't want to allow control of
PINS = [2,3,4,17,27,22,10,9,11,5,6,13,19,26,14,15,18,24,8,7,12,16,20,21,23,25]
for pin in PINS:
    RPiGPIO.setup(pin,RPiGPIO.OUT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0",args.port))

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)

while True:
    data, addr = sock.recvfrom(12)
    cmd, = struct.unpack(">I", data[0:4])
    logger.debug("command received %08x",cmd)
    if cmd == 0x25250001:
        values, mask = struct.unpack(">II", data[4:12])

        for pin in PINS:
            pinmask = (1<<pin)
            if (mask & pinmask):
                logger.debug("mask set for pin %d",pin)
                if (values & (1<<pin)):
                    logger.debug("on")
                    RPiGPIO.output(pin,RPiGPIO.HIGH)
                else:
                    logger.debug("off")
                    RPiGPIO.output(pin,RPiGPIO.LOW)
    else:
        logger.error("Unknown command %08x",cmd)
