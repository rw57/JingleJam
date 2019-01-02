A UDP-based server for controlling Raspberry Pi GPIO ports.

== Why? ==
I want to synchronize Christmas lights to music. I have multiple raspberry Pis
around the house and yard that I want to have in sync together. I tried to use
the built-in [pigpio](http://abyz.me.uk/rpi/pigpio/) daemon and associated
Python library, but the latency turned out to be too much (When turning all the
lights on, you could visibly see them turning on one at a time).

pigpio's protocol (which can do much more complicated things that I didn't
need) appears to send one command per TCP packet. TCP adds a good bit of
overhead. On my wireless network, round-trip time was around 7ms per command.
With 24+ channels, that 7ms per channel turned into well over 100ms. I didn't
test the exact number, but anything over 15-20ms started to become noticeable
to the eye.

This simple service sends multiple commands at once. It's simple: all it can
do is turn on or off channels (for now). But it means I only need to send one
packet (one 3.5ms one-way - remember it's UDP now, not TCP). This saves me
hundreds of milliseconds and, to my eyes, is nearly instantaneous.

== To Install ==
1. Copy `gpioudp.py` somewhere accessible (`/home/pi` ?)
2. Fixup the port if you don't like `2525` (easy to remember: Christmas!)
3. Fixup `gpioudp.service` to reflect the new path
4. Copy `gpioudp.service` into `/lib/systemd/system`
5. Tell systemd the new unit is there: `sudo systemctl daemon-reload`
6. Start the service (to test it): `sudo systemctl start gpioudp.service`
7. Check the service status: `sudo systemctl status gpioudp.service`
8. Finally, make it start on boot: `sudo systemctl enable gpioudp.service`

== Security ==
There is none with this daemon. It provides no authentication. Anyone who can
send packets to it can manipulate your GPIO ports. BE CAREFUL.
