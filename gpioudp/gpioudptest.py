import socket, struct, binascii, time

DEST = ("10.0.0.34",2525)


PINS = [2,3,4,17,27,22,10,9,11,5,6,13,19,26,14,15,18,24,8,7,12,16,20,21,23,25]
#PINS = [2,4,17,22,27]
#PINS = [23,25]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#data = struct.pack(">III", 0x25250001, 0xffffffff, 0xffffffff)
#sock.sendto(data, DEST)

lastpin = -1
while True:
    for pin in PINS:
        if lastpin != -1:
            print("pin %d"%(pin))
            mask = (1<<pin) | (1<<lastpin)
            values = (1<<pin)
            data = struct.pack(">III", 0x25250001, values, mask)
            print("%08x mask %08x hexlify %s"%(values,mask,binascii.hexlify(data)))
            sock.sendto(data, DEST)
        lastpin = pin
        time.sleep(2)
