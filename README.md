![Jingle Jam Logo](logo/JingleJamLogo-web.svg)

Jingle Jam is a Python application to coordinate Christmas lights to music.
It's designed to work with Raspberry Pi GPIO ports but could be easily
extended to control any lights that can be commanded from Python.

## Examples
Ryan's 2018 Display

[![2018 Christmas Lights](https://img.youtube.com/vi/E41gt49GnMo/0.jpg)](https://www.youtube.com/watch?v=E41gt49GnMo)

Ryan's 2017 Display

[![2017 Christmas Lights](https://img.youtube.com/vi/Y4anQM8vMcU/0.jpg)](https://www.youtube.com/watch?v=Y4anQM8vMcU)

## Music
This uses [pygame](https://www.pygame.org/) to play music files. I used OGG files
only. I tried MP3 with mixed results so I always convert my music to OGG.

### Choosing Good Music
Not just any song makes a good sequenced-to-lights song. We need a song with drama. Look for songs with the following characteristics:
* loud & soft sections. even some periods of silence. Lights can be varied to reflect the "scene" of the music
* clear melody and "beat" tones (polyphonic). Some lights can follow the melody while others follow the beat or harmonies.
* repetition (in structure of song and/or in notes/instruments) - helpful for reusing the sequence but also gives audience multiple chances to appreciate the effects
* long runs up and down the scale. Like Joy to the World or Deck the Halls. Lights can move across the house while the scale goes up or down.

Here are some songs that I like:
* [Shout for Joy by Lincoln Brewster (the Christmas mix)](https://www.youtube.com/watch?v=A3dlRO6xt6k)
* [TSO's Christmas Eve in Sarajevo](https://www.youtube.com/watch?v=MHioIlbnS_A)
* [From Heaven to Earth by We Are Messengers](https://www.youtube.com/watch?v=UwVvIIEnCMY)
* [Steven Sharp Nelson's Carol of the Bells (on Cello)](https://www.youtube.com/watch?v=or5YOjy1w2U)

## Latency
### Music
pygame employs a music buffer. In my testing, this resulted in about 600ms of delay on Linux (and Raspbian) and 1150ms on Windows. This affects when to sequence the lights. I'd like to modify the code to account for these delays but I'm not sure there is a good way to auto-detect them.

### Network
I have multiple Raspberry Pis working together and needed a really low-latency way to send commands between them. See [gpioudp](gpioudp/) for a UDP-based daemon that allows for remote control of Raspberry Pis GPIO ports.

## Hardware
TODO

## Sequence Syntax
The sequence files are just simple CSV files with the format: time,comment,commands

The comment is usually inserted by the key you pushed while using `keycatch` but it can be anything.
For songs with words, I usually replace it with the lyrics so I can see where in the song I am.

## HOWTO Sequence
1. Pick the song
2. Listen to it a bunch to get a good feeling for the words and parts of the song
3. Use `keycatch` to capture the overall song structure- mark the intro, the verses, the chorus, the bridge - even if you don’t use commands at these parts, it’ll help later to recall what part of the song you are in
4. Keycatch the melody and beat (drums, bass, harmonies) separately. I liked keeping these in separate files. While using keycatch, play the keyboard like a piano (using your fingers to go up and down) - this makes it easier to spot melodies in the keys captured later
5. Load into Excel or Libreoffice calc - spreadsheet programs make it easier to copy n paste large sections
6. Test often to see what it looks like and to spot bugs

