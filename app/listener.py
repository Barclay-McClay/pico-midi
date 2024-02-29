import serial

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


"""
# Rotary encoder stuff
encoder_value = "init"      # the value of the encoder as stored on the pi pico
rotary_init = 0             # initial value of the rotary encoder/where it resets to
rotary_mag = 9              # how much each notch on the encoder changes the midi value by
rotary_value = rotary_init  # the value of the rotary encoder
rotary_midi_controller = 10 # the midi controller index for the rotary encoder


    
if ser:
        if ser.inWaiting():
            picoMessage = ser.readline().decode('utf-8').strip()
            # The message will either be "ROTARY_PRESS" or an integer
            if picoMessage == "ROTARY_PRESS":
                rotary_value = rotary_init
                print("Rotary: ", rotary_value)
                midi_message = [CONTROLLER_CHANGE, rotary_midi_controller, rotary_value]
            else: # picoMessage is an integer, convert it to one
                encoder_update = int(picoMessage)
                if encoder_value == "init":
                    encoder_value = encoder_update
                if encoder_value < encoder_update:
                    rotary_value += rotary_mag
                    encoder_value = encoder_update
                elif encoder_value > encoder_update:
                    rotary_value -= rotary_mag
                    encoder_value = encoder_update
                # Midi needs to be between 0 and 127
                if rotary_value < 0:
                    rotary_value = 0
                elif rotary_value > 127:
                    rotary_value = 127
                # Send the midi message
                midi_message = [CONTROLLER_CHANGE, rotary_midi_controller, rotary_value]
                midiOut.send_message(midi_message)
                print("Rotary: ", rotary_value)

"""
        