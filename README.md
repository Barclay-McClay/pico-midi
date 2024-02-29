# pico-midi
A cheap and modifiable MIDI controller using Micropython, with a tkinter-based companion app.

## The Pico
The Pico should have [Micropython](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html) installed on it. The code in the [micropython](./micropython) folder is the code that runs on the Pico.

## The Companion App
The companion app is a tkinter-based app that runs on a the computer you plug the Pico into. It is used to translate the serial data from the Pico into MIDI messages. The source code for this is in the [app](./app) folder.

