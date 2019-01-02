# This uses the official raspberry pi GPIO libraries
# they're very fast, but only work locally on the same system

import logging
logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as RPiGPIO
    RPiGPIO.setmode(RPiGPIO.BCM)
    RPiGPIO.setwarnings(False)
    pinsetup = []
    def raw_gpio(pin,cmd):
        pin = int(pin,10)
        if cmd == "on":
            logger.debug("pin %d -> on",pin)
            RPiGPIO.output(pin,RPiGPIO.HIGH)
        else:
            logger.debug("pin %d -> off",pin)
            RPiGPIO.output(pin,RPiGPIO.LOW)
    def gpio_macro(time,pin,cmd):
        """
        This macro just makes sure that the setup per pin is done
        so that the raw_gpio command can be really fast
        """
        pin = int(pin,10)
        if pin not in pinsetup:
            RPiGPIO.setup(pin,RPiGPIO.OUT)
            # we could set everything low, but I'd rather have full control in
            # the lightshow code to leave a scene up at the end of each song
            #RPiGPIO.output(self.pin,RPiGPIO.LOW)
            pinsetup.append(pin)
        return [(time,"raw_gpio %d %s"%(pin,cmd))]
except ImportError:
    logger.warning("no raspberry pi GPIO libraries found - using stub version")
    def raw_gpio(pin,cmd):
        pin = int(pin,10)
        if cmd == "on":
            logger.debug("pin %d -> on",pin)
        else:
            logger.debug("pin %d -> off",pin)
    def gpio_macro(time,pin,cmd):
        """
        This macro just makes sure that the setup per pin is done
        so that the raw_gpio command can be really fast
        """
        pin = int(pin,10)
        return [(time,"raw_gpio %d %s"%(pin,cmd))]

def register(commands,macros,commits):
    commands['raw_gpio'] = raw_gpio
    macros['gpio'] = gpio_macro

