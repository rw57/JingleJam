# X10 is so slow...
# I ran a web server to let me control X10 lights through a CM11A gateway.
# there's nearly a second of latency per command! on top of that, it just
# wasn't very reliable (some commands would go, some wouldn't).
# I'm not using this code anymore, but left it here if it's helpful to you

import logging, requests, threading, queue
logger = logging.getLogger(__name__)

import os
if 'X10_HTTP_SERVER' in os.environ:
    X10_HTTP_SERVER = os.environ['X10_HTTP_SERVER']
else:
    logger.warning("X10_HTTP_SERVER wasn't specified in the environment... disabling!")
    X10_HTTP_SERVER = None

if X10_HTTP_SERVER is not None:
    x10threadqueue = queue.Queue()
    def x10thread():
        # We run all the X10 web requests on a separate thread because they are
        # so slow we don't want to block the music playing
        logger.debug("x10 thread started")
        while True:
            code,cmd = x10threadqueue.get()
            r = requests.get('http://10.0.0.21:8080/'+code+'/'+cmd)
            logger.debug("x10 response = "+r.text)
            x10threadqueue.task_done()
    thread = threading.Thread(target=x10thread)
    thread.daemon = True
    thread.start()

    X10_DELAY_MS = 850
    # X10 (especially X10 via http request) is extremely inconsistent
    # on timeliness... but this is about how much latency.
    def raw_x10(code,cmd):
        x10threadqueue.put((code,cmd))

    def x10_macro(time,code,cmd):
        """ this macro is to deal with the delay """
        return [(time-X10_DELAY_MS,"raw_x10 %s %s"%(code,cmd))]

    def register(commands,macros,commits):
        macros['x10'] = x10_macro
        commands['raw_x10'] = raw_x10
else:
    def register(commands,macros,commits):
        pass
