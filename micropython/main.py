# Barclay McClay 2024
import time
from controllers import pushPot

# Here's where you define all the modules you've wired up to the Pico.
# Everying added to the 'parts' array will be 'armed' in the main loop.
parts = [ pushPot(potAlias="KNOB1",switchAlias="SWITCH1",sw=2,dt=1,clk=0) ]


while True:
    try:
        for part in parts:
            part.armed()
        time.sleep_ms(1)
    except Exception as e:
        print(e)
        break
