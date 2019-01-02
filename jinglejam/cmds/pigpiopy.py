
try:
    import pigpio

    # global pigpio factory object to cache these connection objects
    pifactory = {}

    def raw_pigpio_cmd(host,pin,cmd):
        if host not in pifactory:
            pifactory[host] = pigpio.pi(host)
        pin = int(pin,10)
        if cmd == "on":
            logger.debug("host %s pin %d -> on",host,pin)
            pifactory[host].write(pin,1)
        else:
            logger.debug("host %s pin %d -> off",host,pin)
            pifactory[host].write(pin,0)

    def pigpio_macro(time,host,*args):
        # this is a preprocessor to make sure the pi factory is created BEFORE
        # the show starts (because it's really slow to create this object)
        if host not in pifactory:
            pifactory[host] = pigpio.pi(host)
        return [[time,('raw_pigpio %s '%(host))+(' '.join(args))]]

    def register(commands,macros,commits):
        commands['raw_pigpio'] = raw_pigpio_cmd
        macros['pigpio'] = pigpio_macro
except ImportError:
    logger.warning("no pigpio libraries found")
    def register(commands,macros,commits):
        pass
