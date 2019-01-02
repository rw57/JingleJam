
def wait(time,duration,*args):
    """
    Delay a command.
    instead of executing it at the time specified, add a delay and then execute
    """
    duration = int(duration,10)
    cmd = '"'+('" "'.join(args))+'"'
    return [(time+duration,cmd)]

def earlyon(time,duration,*args):
    """
    Some lights have a slight delay before they turn on (capacitors that need
    to be charged up?). This takes the current time and subtracts that delay
    so the code looks like they turn on at the right time, but we really send
    the command a little bit early to give the illusion that they're all in
    sync
    """
    duration = int(duration,10)
    cmd = '"'+('" "'.join(args))+'"'
    if args[-1]=="on":
        return [(time-duration,cmd)]
    else:
        return [(time,cmd)]

def register(commands,macros,commits):
    macros['wait'] = wait
    macros['earlyon'] = earlyon

