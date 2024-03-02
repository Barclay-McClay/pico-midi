# Barclay McClay 2024
from rotary_irq_rp2 import RotaryIRQ
from machine import Pin

# Parent class for all modules
class PART():
    def __init__(self):
        self.alias = "NOALIAS"
        pass
    
    def armed(self):
        pass
###########################################################################################################
# A 5-pin rotary encoder. It's endless in its rotation, and acts as a momentary switch if pushed (sw pin).
class pushPot(PART):
    def __init__(self, potAlias, switchAlias, sw, dt, clk):
        super().__init__()
        self.potAlias = potAlias
        self.switchAlias = switchAlias
        self.SW = Pin(sw,Pin.IN,Pin.PULL_UP)
        self.DT = dt
        self.CLK = clk
        self.pot = RotaryIRQ(pin_num_dt=self.DT,
                             pin_num_clk=self.CLK,
                             min_val = 0,
                             reverse = False,
                             range_mode = RotaryIRQ.RANGE_UNBOUNDED)
        self.prev_val = self.pot.value()
        self.button_press = self.SW.value()
    
    def armed(self):
        try:
            self.value = self.pot.value()
            if self.SW.value()==0 and self.button_press == 0:  
                print(str(self.switchAlias) + "_" + "SWITCH" + "_" + "1") # < --------- OUTPUT
                self.button_press = 1
            elif self.SW.value()==1:
                if self.button_press != 0:
                    print(str(self.switchAlias) + "_" + "SWITCH" + "_" + "0") # < --------- OUTPUT
                    self.button_press = 0
            if self.prev_val != self.value:
                print(str(self.potAlias) +  "_" + "ENCODER" + "_" + str(self.value))  # <------------------------- OUTPUT
                self.prev_val = self.value
        except Exception as e:
            print(e)
###########################################################################################################
