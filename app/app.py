
import rtmidi
import threading
from rtmidi.midiconstants import CONTROLLER_CHANGE
import tkinter as tk
from tkinter import ttk
from listener import ser, serial_listener
import appColours as colours

# Load the MIDI I/O
midiOut = rtmidi.MidiOut()
available_midi_output_ports = midiOut.get_ports()


###########################################################################################################################
# APP THREAD
class App(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.auto_config = False
        self.start()

    def callback(self):
        self.root.quit()


    def open_midi_port(self, *args):
        print("Opening MIDI port: ", self.varOutput.get())
        try:
            midiOut.open_port(self.varOutput.get())
        except Exception as e:
            print(e)
            print("Failed to open MIDI port")

    def auto_config_toggle(self):
        self.auto_config = not self.auto_config
#####################
# Main Tkinter Window Constructor
#####################
    def run(self):
        self.root = tk.Tk()
        self.root.title("🎛 MIDI4MADDY 🛠")
        self.root.configure(bg=colours.BG)

        # FRAMES
        self.frMain = tk.Frame(self.root, bg=colours.BG, relief='groove',  padx=5, pady=5)
        self.frTop = tk.Frame(self.frMain, bg=colours.BG, relief='groove',  padx=5, pady=5)
        self.frOutput = tk.Frame(self.frMain, bg=colours.BG, relief='groove',  padx=5, pady=5)
        self.frConfigMenu = tk.Frame(self.frMain, bg=colours.BG, relief='groove',  padx=5, pady=5)

        # Grid the frames
        self.frMain.grid(row=0,column=0)
        self.frTop.grid(row=0,column=0)
        self.frConfigMenu.grid(row=1,column=0)
        self.frOutput.grid(row=2,column=0)



        # The area for configuring 16 different inputs
        # Each input will have text input for naming, a dropdown for selecting the type of input, and a dropdown for selecting the MIDI channel to output to
        self.lbConfigMenu = tk.Label(self.frConfigMenu, bg=colours.BG, fg=colours.GREEN, font="lucidatypewriter 10", text="CONFIGURE INPUTS:")
        self.lbConfigMenu.grid(row=0,column=0, sticky="ew")
        self.inputs = []
        for i in range(16):
            # Text input for naming
            input_name = tk.Entry(self.frConfigMenu, bg=colours.NAVY, fg=colours.GREEN, width=8, font="lucidatypewriter 10")
            input_name.grid(row=i+1, column=0, sticky="ew")

            # Dropdown for selecting the type of input
            input_type = tk.StringVar(value="Type")
            input_type_dropdown = tk.OptionMenu(self.frConfigMenu, input_type, "Type 1", "Type 2", "Type 3")
            input_type_dropdown.configure(width=15,bg=colours.BG, fg=colours.GREEN, activebackground=colours.BG,highlightbackground=colours.BG, highlightcolor=colours.YELLOW,activeforeground=colours.YELLOW)
            input_type_dropdown.grid(row=i+1, column=1,sticky="ew")

            # Dropdown for selecting the MIDI channel to output to
            midi_channel = tk.StringVar(value="Channel")
            midi_channel_dropdown = tk.OptionMenu(self.frConfigMenu, midi_channel, "Channel 1", "Channel 2", "Channel 3")
            midi_channel_dropdown.configure(bg=colours.BG, fg=colours.GREEN, activebackground=colours.BG,highlightbackground=colours.BG, highlightcolor=colours.YELLOW,activeforeground=colours.YELLOW)
            midi_channel_dropdown.grid(row=i+1, column=2, sticky="ew")

            # Store the inputs in a list
            self.inputs.append((input_name, input_type, midi_channel))

        # 'auto-config' for serial commands button
        self.frOutputLeft = tk.Frame(self.frOutput, bg=colours.BG, relief='groove',  padx=5, pady=5)
        self.frOutputLeft.grid(row=0,column=0)
        # This button will configure the inputs based on the serial commands received from the Pico
        self.bAutoConfig = tk.Button(
            self.frOutputLeft, 
            bg=colours.DARK_GREEN, 
            text="Auto-Config", 
            relief='raised',
            fg=colours.GREEN,
            font="lucidatypewriter 10",
            activebackground=colours.YELLOW,
            highlightbackground=colours.BG,
            highlightcolor=colours.YELLOW,
            activeforeground=colours.YELLOW,
            padx=5,
            pady=5,
            width=15,
            height=4,
            command=self.auto_config_toggle
            )
        self.bAutoConfig.grid(row=0,column=0)

        # Dropdown menu for selecting the MIDI output
        self.lbOutput = tk.Label(self.frOutputLeft, bg=colours.BG, fg=colours.GREEN, font="lucidatypewriter 12", text="SELECT MIDI OUTPUT:")
        self.varOutput = tk.StringVar(value=available_midi_output_ports[0])
        self.varOutput.trace_add("write",self.open_midi_port)  # set up a callback on varOutput
        self.wOutputSelect = tk.OptionMenu(self.frOutputLeft,self.varOutput,*available_midi_output_ports)
        self.wOutputSelect.configure(relief='groove',bg=colours.BG, fg=colours.GREEN, activebackground=colours.BG,highlightbackground=colours.BG, highlightcolor=colours.YELLOW,activeforeground=colours.YELLOW)
        # Grid the MIDI output selector
        self.lbOutput.grid(row=1,column=0)
        self.wOutputSelect.grid(row=2,column=0)

        # Text box for displaying the serial buffer
        self.frOutputRight = tk.Frame(self.frOutput, bg=colours.BG, relief='groove',  padx=5, pady=5)
        self.lbSerialBuffer = tk.Label(self.frOutputRight, font="lucidatypewriter 6", text="INCOMING SERIAL BUFFER", bg=colours.BG, fg=colours.GREEN)
        self.txtSerialBuffer = tk.Text(self.frOutputRight, height=5, width=25, bg="black", fg=colours.GREEN, font="lucidatypewriter 15", wrap="word")
        # Grid the output display
        self.frOutputRight.grid(row=0,column=1, sticky='n')
        self.lbSerialBuffer.grid(row=0,column=0,sticky='n')
        self.txtSerialBuffer.grid(row=1,column=0, sticky='n')


        # MAIN LOOP
        self.root.mainloop()
###################
# RUN THE THREAD
app = App()
############################################################################################################



# MAIN THREAD

while True:
    serial_buffer_line = serial_listener()
    if serial_buffer_line:
        print(serial_buffer_line)
        # Outplut display box ###############################################
        app.txtSerialBuffer.insert(1.0, serial_buffer_line + "\n")
        displayed_lines = app.txtSerialBuffer.get('1.0', tk.END).splitlines()
        if len(displayed_lines) > 5: 
            # delete from the start of the 6th line to the end
            app.txtSerialBuffer.delete('6.0', tk.END)
        #####################################################################

    # Auto-Config #######################################################
    if app.auto_config:
        app.bAutoConfig.configure(bg=colours.DARK_RED, fg=colours.YELLOW, activebackground=colours.YELLOW, text= "Listening for\nserial commands")
        if serial_buffer_line:
            inputAlias = serial_buffer_line.split("_")[0]
    else:
        app.bAutoConfig.configure(bg=colours.DARK_GREEN, fg=colours.GREEN, activebackground=colours.YELLOW, text="Auto-Config")
            

#############################################################################################################
# END


















"""
                                                                                                                         
                                                                                                                         
                  &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&         &&&&&&@         &&&&&&&&&&&&&&&&&&&&&&&&&&&&&                   
  &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&    &&&&&&&&&&&       &&&&&&&@@        &&&&&&&&&      &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&  
    &&&&&&&&&&&&&&&&&&&&    &&&&&&&&&&  &&&&&&&&&       &&&&&&&@@       &&&&&&&&   &&&&&&&&&&    &&&&&&&&&&&&&&&&&&&&    
                  &&&&&&&&&&&&&&   &&&&&& &&&&&&&&&       && @@       &&&&&&&&& &&&&&    &&&&&&&&&&&&&&                  
        &&&&&&&&&&&&&&&&&&&  &&&&&&&&  &&&& && &&&&&&&&    & @    &&&&&&&&.&& &&&&  &&&&&&&    &&&&&&&&&&&&&&&&&&        
         &&&&&&&&&&&    &&&&&&&&&&  &&&&  &&&              & @              &&&  &&&&  &&&&&&&&&      &&&&&&&&&&         
                  &&&&&&&&&&&&   &&&&&   &&    %&&&&&&&    & @    &&&&&&&%   &&&&  &&&&&   &&&&&&&&&&&&                  
                  &&&&&&&    &&&&&&&  &&&&   &&&&&&&&&&&&# & @ #&&&&&&&&&&&    &&&&  &&&&&&     &&&&&&&                  
                          &&&&&&&   &&&&&   &&&&&          & @          &&&&&   &&&&&   &&&&&&&                          
                                  &&&&&     &&&&           & @           &&&&     &&&&&                                  
                                            &&&&&&         & @         &&&&&&                                            
                                             *&&&&&&&      & @      &&&&&&&*                                             
                                                &&&&&&&&&& & @ &&&&&&&&&&                                                
                                                    &&&&&&&&&@&&&&&
                                                   &&&&    & @&&&&&&&&                                                   
                                                 &&&&&     & @     &&&&&                                                 
                                                 &&&&&&    & @    &&&&&                                                  
                                                   &&&&&&&&&&@  &&&&                                                     
                                                        &&&&&&&&&&&&                                                     
                                                    &&&&&  & @  &&&&&                                                    
                                                   &&&&&&  & @   &&&&                                                    
                                                     &&&&&&&&&&&&&&&                                                     
                                                      &&&&   @ &&&&                                                      
                                                       &&&&& @ &&&&
                                                        &&&& &&&&&
                                                         &&& @&&&
                                                         &&& &&&
                                                          && &&
                                                          % @ %
                                                            @
                                                            @
                                                            @

Barclay McClay
"""