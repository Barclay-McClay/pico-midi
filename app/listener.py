import serial
import rtmidi
from rtmidi.midiconstants import CONTROLLER_CHANGE, NOTE_ON, NOTE_OFF

# Load the MIDI I/O
midiOut = rtmidi.MidiOut()
available_midi_output_ports = midiOut.get_ports()

# Define input types
# These are the contoller classes defined in the micropython code
INPUT_TYPES = [
    "ENCODER",
    "SWITCH"
    ]
# Each Input type can have a range of 'behaviours' that alters the way it functions
INPUT_BEHAVIOURS = {
    "ENCODER": [
        "Control 0-127",
        "Note Send"
    ],
    "SWITCH": [
        "Hold",
        "Toggle",
        "Send Value"
    ]
}


ser = None # serial port object
# Load the Pico Controller serial buffer
try:
    ser = serial.Serial('COM4', 9600)  # serial port
except serial.SerialException as e:
    print(e)
    print("No Pico found")

def serial_listener():
    if ser.in_waiting > 0:
        serial_buffer_line = ser.readline().decode('utf-8').rstrip()
        return serial_buffer_line
    else:
        return None

class inputModule():
    def __init__(self, alias="Unknown", input_type="SWITCH", midi_index=0):
        self.alias = alias
        self.input_type = input_type
        self.value = 0
        self.reset_value = 0
        self.magnitude = 1 # how much each action changes the midi value by
        self.midi_index = midi_index
        self.prev_value = "init"
        self.value = self.reset_value  # the value of the rotary encoder
        self.behaviour = "Default"  # what the input does
        if self.input_type == "ENCODER":
            self.magnitude = 9              # how much each notch on the encoder changes the midi value by
            self.midi_constant = CONTROLLER_CHANGE
            self.behaviour = "Control 0-127"
        elif self.input_type == "SWITCH":
            self.behaviour = "Hold"
            self.midi_constant = NOTE_ON

    def updateEncoder(self, serial_value):
        if self.prev_value == "init":
            self.prev_value = serial_value
        if self.prev_value < serial_value:
            self.value += self.magnitude
            self.prev_value = serial_value
        elif self.prev_value > serial_value:
            self.value -= self.magnitude
            self.prev_value = serial_value
        if self.behaviour == "Control 0-127":
            self.midi_constant = CONTROLLER_CHANGE
            print("Rotary Control: ", self.midi_index, self.value)
        elif self.behaviour == "Note Send":
            self.midi_constant = NOTE_ON
            print("Rotary Note: ",  self.midi_index,  self.value)


    def updateSwitch(self, serial_value):
        if self.behaviour == "Hold":
            if serial_value > 0:
                self.midi_constant = NOTE_ON
                self.value = serial_value
                print(self.alias, "Note ON", self.value)
            else:
                self.midi_constant = NOTE_OFF
                self.value = 0
                print(self.alias, "Note OFF", self.value)
        elif self.behaviour == "Toggle":
            if serial_value > 0:
                if self.value == 0:
                    self.value = 1
                    self.midi_constant = NOTE_ON
                    print(self.alias, "Note ON", self.value)
                else:
                    self.value = 0
                    self.midi_constant = NOTE_OFF
                    print(self.alias, "Note OFF", self.value)
        elif self.behaviour == "Send Value":
            # TODO: Send value should control a different module, like directly setting an encoder to a value
            pass

    def update(self, serial_value):
        if self.input_type == "SWITCH":
            self.updateSwitch(serial_value)
        elif self.input_type == "ENCODER":
            self.updateEncoder(serial_value)
        # SEND THE MIDI MESSAGE
        # Midi needs to be between 0 and 127
        if self.value < 0:
            self.value = 0
        elif self.value > 127:
            self.value = 127
        # Send the midi message
        midi_message = [self.midi_constant, self.midi_index, self.value]
        print(midi_message)
        midiOut.send_message(midi_message)
        #

        