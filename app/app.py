
import threading
import tkinter as tk
import appColours as colours
from listener import (
    midiOut, 
    available_midi_output_ports, 
    serial_listener,
    inputModule,
    INPUT_TYPES,
    INPUT_BEHAVIOURS,
)




###########################################################################################################################
# APP THREAD
class App(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.auto_config = False
        self.selected_input_module_index = None
        self.selected_input_module_alias = None
        self.INPUTS = []
        self.start()

    def callback(self):
        self.root.quit()

    def open_midi_port(self, *args):
        selected = self.varOutput.get()
        index = int(selected.split("|")[0])
        print("Opening MIDI port: ", index)
        try:
            midiOut.open_port(index)
        except Exception as e:
            print(e)
            print("Failed to open MIDI port")

    def add_input_module(self,alias):
        m = {}
        i = len(self.INPUTS)
        m['index'] = i
        # define the input module config row
        # Text input for naming
        m['alias'] = alias
        self.listboxInputList.insert(tk.END, alias)
        self.INPUTS.append(m)

    def remove_input_module(self, index):
        m = self.INPUTS.pop(index)
        SERIAL_INPUTS.pop(m['alias'], None)
        self.selected_input_module_index = None
        self.listboxInputList.delete(index)
        self.select_input_module(None)

    def select_input_module(self, event):
        # Get the index of the currently selected item
        if event:
            if event.widget.curselection():
                try:
                    index = event.widget.curselection()[0]
                except:
                    index = None
                if index is not None:
                    if index < len(self.INPUTS) and index >= 0:
                        self.selected_input_module_index = index
                        moduleAlias = self.INPUTS[index]['alias']
                        self.selected_input_module_alias = moduleAlias
                        selected_module = SERIAL_INPUTS[moduleAlias]
                        self.varConfigAreaTitle.set(f"CONFIGURE {selected_module.alias}")
                        self.varInputModuleTypeLabel.set(f"{selected_module.input_type}")
                        self.varConfigDisplayValue.set(f"{selected_module.value}")
                        self.varConfigDisplayMidiConstant.set(f"{selected_module.midi_constant}")
                        self.varConfigMidi_index.set(f"{selected_module.midi_index}")
                        self.varConfigMagnitude.set(f"{selected_module.magnitude}")
                        self.varConfigDefaultValue.set(f"{selected_module.reset_value}")
                        # Behaviours:
                        menu = self.wConfigBehaviour['menu']
                        menu.delete(0, 'end')
                        self.varConfigBehaviour.set(selected_module.behaviour)
                        new_options = INPUT_BEHAVIOURS[selected_module.input_type]
                        for value in new_options:
                            menu.add_command(label=value, 
                                            command=lambda v=value: self.set_behaviour(v))
                        self.wConfigBehaviour.configure(bg=colours.BG, fg=colours.YELLOW, padx=5, pady=5, font="lucidatypewriter 10", relief='flat', activebackground=colours.HIGHLIGHT1, highlightbackground=colours.BG, highlightcolor=colours.YELLOW, activeforeground=colours.DARK, width=10, height=1)
                        print("Selected input module: ", self.selected_input_module_alias, "Index:", index)
                    else:
                        print("!! An error occured- No module at index ", index)
                else:
                    self.varConfigAreaTitle.set(f"NO MODULE SELECTED")
                    self.varInputModuleTypeLabel.set(f"TYPE")
                    self.varConfigDisplayValue.set(f"---")
                    self.varConfigDisplayMidiConstant.set(f"---")
                    self.varConfigMidi_index.set(f"")
                    self.varConfigMagnitude.set(f"")
                    self.varConfigDefaultValue.set(f"")
                    self.wConfigBehaviour['menu'].delete(0, 'end')
                    self.wConfigBehaviour['menu'].add_command(label='---')
                    self.varConfigBehaviour.set("---")
                    self.wConfigBehaviour.configure(bg=colours.BG, fg=colours.YELLOW, padx=5, pady=5, font="lucidatypewriter 10", relief='flat', activebackground=colours.HIGHLIGHT1, highlightbackground=colours.BG, highlightcolor=colours.YELLOW, activeforeground=colours.DARK, width=10, height=1)
                    print(f"No module at index NONE")
    
    def auto_config_toggle(self):
        self.auto_config = not self.auto_config
        if self.auto_config:
            self.bAutoConfig.configure(bg=colours.DARK_RED, fg=colours.YELLOW, text="Listening for\nserial commands...")
            self.txtSerialBuffer.configure(fg=colours.GREEN)
            app.txtSerialBuffer.delete('1.0', tk.END)
        else:
            self.bAutoConfig.configure(bg=colours.HIGHLIGHT1,fg=colours.DARK, text="Get Inputs")
            self.txtSerialBuffer.configure(fg=colours.YELLOW)
            app.txtSerialBuffer.delete('1.0', tk.END)

    def set_behaviour(self, value):
        self.varConfigBehaviour.set(value)
        moduleAlias = self.INPUTS[self.selected_input_module_index]['alias']
        selected_module = SERIAL_INPUTS[moduleAlias]
        selected_module.behaviour = self.varConfigBehaviour.get()

    def set_midi_noteIndex(self, *args):
        moduleAlias = self.INPUTS[self.selected_input_module_index]['alias']
        selected_module = SERIAL_INPUTS[moduleAlias]
        user_input = self.varConfigMidi_index.get()
        user_input = self.sanitise_user_input(user_input)
        self.varConfigMidi_index.set(user_input)
        selected_module.midi_index = user_input

    def set_magnitude(self, *args):
        moduleAlias = self.INPUTS[self.selected_input_module_index]['alias']
        selected_module = SERIAL_INPUTS[moduleAlias]
        user_input = self.varConfigMagnitude.get()
        user_input = self.sanitise_user_input(user_input)
        self.varConfigMagnitude.set(user_input)
        selected_module.magnitude = user_input

    def set_default_value(self, *args):
        moduleAlias = self.INPUTS[self.selected_input_module_index]['alias']
        selected_module = SERIAL_INPUTS[moduleAlias]
        user_input = self.varConfigDefaultValue.get()
        user_input = self.sanitise_user_input(user_input)
        self.varConfigDefaultValue.set(user_input)
        selected_module.reset_value = user_input

    def sanitise_user_input(self, user_input):
        # sanitize user input
        try:
            user_input = int(user_input)
            if user_input < 0:
                user_input = 0
            elif user_input > 127:
                user_input = 127
            return user_input
        except:
            print("Invalid input")
            return 0

#####################
# Main Tkinter Window Constructor
#####################
    def run(self):
        self.root = tk.Tk()
        self.root.title("🎛 MIDIMADDI")
        self.root.configure(bg=colours.BG)

        # FRAMES
        self.frMain = tk.Frame(self.root, bg=colours.BG, relief='groove',  padx=10, pady=10)
        self.frMain.grid(row=0,column=0)
        # Sub-frames
        self.frTop = tk.Frame(self.frMain, bg=colours.BG, relief='groove',  padx=5, pady=5, width=60)
        self.frMiddle = tk.Frame(self.frMain, bg=colours.BG, relief='groove',  padx=5, pady=5, width=60)
        self.frBottom = tk.Frame(self.frMain, bg=colours.BG, relief='groove',  padx=5, pady=5, width=60)
        self.frTop.grid(row=0,column=0)
        self.frMiddle.grid(row=1,column=0)
        self.frBottom.grid(row=2,column=0)
        # Sub-sub-frames
        # Top
        # -
        # Middle
        self.frInputList = tk.Frame(self.frMiddle, bg=colours.BG, relief='groove',  padx=5, pady=5, width=25)
        self.frConfigArea = tk.Frame(self.frMiddle, bg=colours.BG, relief='groove',  padx=5, pady=5, width=25, height=20)
        self.frInputList.grid(row=0,column=0, sticky= 'w')
        self.frConfigArea.grid(row=0,column=1, sticky='e')
        # Bottom
        self.frBottomLeft = tk.Frame(self.frBottom, bg=colours.BG, relief='groove',  padx=5, pady=5, width=25)
        self.frBottomRight = tk.Frame(self.frBottom, bg=colours.BG, relief='groove',  padx=5, width=25)
        self.frBottomLeft.grid(row=0,column=0)
        self.frBottomRight.grid(row=0,column=1, sticky='n')
        ######################################
        ## TOP --------------------------------------------------------------------------------
        # TODO: Title/toolbar menu for the app
        ## MIDDLE--------------------------------------------------------------------------------
        # The area for configuring the different inputs ('Config Menu')
        # Listbox for displaying the input modules (LEFT) ---------
        self.lbInputList = tk.Label(self.frInputList, bg=colours.BG, fg=colours.TEXT, font="lucidatypewriter 12", text="INPUT MODULES")
        self.varInputList = tk.StringVar(value=[f"{m['alias']}" for m in self.INPUTS])
        self.listboxInputList = tk.Listbox(self.frInputList,
                                           bg=colours.DARK, 
                                           fg=colours.YELLOW, 
                                           font="lucidatypewriter 12", 
                                           width=20, height=20, 
                                           relief='flat', 
                                           selectbackground=colours.HIGHLIGHT1, 
                                           selectforeground=colours.DARK,
                                           highlightbackground=colours.BG,
                                           highlightthickness=0,
                                           selectmode='single', 
                                           listvariable=self.varInputList
        )
        self.listboxInputList.bind("<<ListboxSelect>>", self.select_input_module)
        self.sbInputList = tk.Scrollbar(self.frInputList, bg=colours.DARK, relief='flat', highlightbackground=colours.BG, highlightcolor=colours.YELLOW, activebackground=colours.YELLOW)
        self.sbInputList.config(command=self.listboxInputList.yview)
        self.listboxInputList.config(yscrollcommand=self.sbInputList.set)
        self.listboxInputList.delete(0,tk.END)
        self.lbInputList.grid(row=0,column=0, sticky='n')
        self.sbInputList.grid(row=1,column=1,sticky='nsew')
        self.listboxInputList.grid(row=1,column=0, sticky='nw')
        
        # CONFIG AREA (RIGHT) ----------------
        # Here is where all the 'fine tuning' paramaters can be viewed/configured for each input module
        # Sub-frames
        self.frConfigAreaTitle = tk.Frame(self.frConfigArea, bg=colours.BG)
        self.frConfigAreaBody = tk.Frame(self.frConfigArea, bg=colours.BG)
        self.frConfigAreaTitle.grid(row=0,column=0,sticky='n')
        self.frConfigAreaBody.grid(row=1,column=0,sticky='nw')
        # Top Area ------
        self.varConfigAreaTitle = tk.StringVar(value="CONFIGURE INPUT MODULE")
        self.varInputModuleTypeLabel = tk.StringVar(value="TYPE")
        self.lbConfigArea = tk.Label(self.frConfigAreaTitle, width=25, bg=colours.BG, fg=colours.TEXT, font="lucidatypewriter 12", textvariable=self.varConfigAreaTitle)
        self.lbInputModuleTypeLabel = tk.Label(self.frConfigAreaTitle, bg=colours.BG, fg=colours.GREEN, font="lucidatypewriter 10", textvariable=self.varInputModuleTypeLabel)
        # 'Remove' button
        self.bRemoveModule = tk.Button(
            self.frConfigAreaTitle, 
            bg=colours.DARK_RED, 
            text="REMOVE MODULE",
            relief='groove',
            fg=colours.YELLOW,
            font="lucidatypewriter 10",
            activebackground=colours.YELLOW,
            highlightbackground=colours.BG,
            highlightcolor=colours.YELLOW,
            activeforeground=colours.DARK_RED,
            padx=5,
            pady=5,
            width=20,
            height=1,
            command=lambda: self.remove_input_module(self.listboxInputList.curselection()[0])
            )
        # Grid top area
        self.lbConfigArea.grid(row=0,column=0,sticky='n')
        self.bRemoveModule.grid(row=1,column=0,sticky='n')
        self.lbInputModuleTypeLabel.grid(row=2,column=0,sticky='n')
        # Body -------
        # immutable commands:
        self.lbConfigDisplay_value = tk.Label(self.frConfigAreaBody, padx=5,pady=5, bg=colours.BG, fg=colours.TEXT, font="lucidatypewriter 10", text="CURRENT VALUE:")
        self.varConfigDisplayValue = tk.StringVar(value="---")
        self.wConfigDisplay_value = tk.Label(self.frConfigAreaBody, bg=colours.BG, fg=colours.HIGHLIGHT1, font="lucidatypewriter 10", textvariable=self.varConfigDisplayValue, width=3)
        self.lbConfigDisplay_midiconstant = tk.Label(self.frConfigAreaBody, padx=5,pady=5, bg=colours.BG, fg=colours.TEXT, font="lucidatypewriter 10", text="MIDI CONSTANT:")
        self.varConfigDisplayMidiConstant = tk.StringVar(value="---")
        self.wConfigDisplay_midiconstant = tk.Label(self.frConfigAreaBody, bg=colours.BG, fg=colours.HIGHLIGHT1, font="lucidatypewriter 10", textvariable=self.varConfigDisplayMidiConstant, width=3)
        # Behaviour Dropdown:
        self.lbConfigBehaviour = tk.Label(self.frConfigAreaBody, padx=5,pady=5, bg=colours.BG, fg=colours.TEXT, font="lucidatypewriter 10", text="BEHAVIOUR:")
        self.varConfigBehaviour = tk.StringVar(value="---")
        self.wConfigBehaviour = tk.OptionMenu(self.frConfigAreaBody, self.varConfigBehaviour,'---')
        self.wConfigBehaviour.configure(bg=colours.BG, fg=colours.YELLOW, padx=5, pady=5, font="lucidatypewriter 10", relief='flat', activebackground=colours.HIGHLIGHT1, highlightbackground=colours.BG, highlightcolor=colours.YELLOW, activeforeground=colours.DARK, width=10, height=1)
        # cc/note index
        self.lbConfigMidi_index = tk.Label(self.frConfigAreaBody, padx=5,pady=5, bg=colours.BG, fg=colours.TEXT, font="lucidatypewriter 10", text="CC/NOTE INDEX:")
        self.varConfigMidi_index = tk.StringVar(value="")
        self.wConfigMidi_index = tk.Entry(self.frConfigAreaBody, bg=colours.DARK, fg=colours.YELLOW, font="lucidatypewriter 10", textvariable=self.varConfigMidi_index, width=3)
        self.wConfigMidi_index.bind("<KeyRelease>",self.set_midi_noteIndex) # bind the function to the entry widget's KeyRelease event
        # magnitude
        self.lbConfigMagnitude = tk.Label(self.frConfigAreaBody, padx=5,pady=5, bg=colours.BG, fg=colours.TEXT, font="lucidatypewriter 10", text="MAGNITUDE:")
        self.varConfigMagnitude = tk.StringVar(value="")
        self.wConfigMagnitude = tk.Entry(self.frConfigAreaBody, bg=colours.DARK, fg=colours.YELLOW, font="lucidatypewriter 10", textvariable=self.varConfigMagnitude, width=3)
        self.wConfigMagnitude.bind("<KeyRelease>",self.set_magnitude) # bind the function to the entry widget's KeyRelease event
        # default, or 'reset' value
        self.lbConfigDefault_value = tk.Label(self.frConfigAreaBody, padx=5,pady=5, bg=colours.BG, fg=colours.TEXT, font="lucidatypewriter 10", text="DEFAULT VALUE:" )
        self.varConfigDefaultValue = tk.StringVar(value="")
        self.wConfigDefault_value = tk.Entry(self.frConfigAreaBody, bg=colours.DARK, fg=colours.YELLOW, font="lucidatypewriter 10", textvariable=self.varConfigDefaultValue, width=3)
        self.wConfigDefault_value.bind("<KeyRelease>",self.set_default_value) # bind the function to the entry widget's KeyRelease event
        # Grid
        r = 0
        self.lbConfigBehaviour.grid(row=r,column=0,sticky='nw')
        self.wConfigBehaviour.grid(row=r,column=1,sticky='nw'); r+=1
        self.lbConfigDisplay_value.grid(row=r,column=0,sticky='nw')
        self.wConfigDisplay_value.grid(row=r,column=1,sticky='nw'); r+=1
        self.lbConfigDisplay_midiconstant.grid(row=r,column=0,sticky='nw')
        self.wConfigDisplay_midiconstant.grid(row=r,column=1,sticky='nw'); r+=1
        self.lbConfigMidi_index.grid(row=r,column=0,sticky='nw')
        self.wConfigMidi_index.grid(row=r,column=1,sticky='nw'); r+=1
        self.lbConfigMagnitude.grid(row=r,column=0,sticky='nw')
        self.wConfigMagnitude.grid(row=r,column=1,sticky='nw'); r+=1
        self.lbConfigDefault_value.grid(row=r,column=0,sticky='nw')
        self.wConfigDefault_value.grid(row=r,column=1,sticky='nw'); r+=1
        # MIDI CHANNEL DROPDOWN
        ## BOTTOM --------------------------------------------------------------------------------
        # LEFT -------------
        # This button will configure the inputs based on the serial commands received from the Pico
        self.bAutoConfig = tk.Button(
            self.frBottomLeft, 
            bg=colours.HIGHLIGHT1, 
            text="Get Inputs",
            relief='groove',
            fg=colours.DARK,
            font="lucidatypewriter 10",
            activebackground=colours.YELLOW,
            highlightbackground=colours.BG,
            highlightcolor=colours.YELLOW,
            activeforeground=colours.YELLOW,
            padx=5,
            pady=2,
            width=20,
            height=2,
            command=self.auto_config_toggle
            )
        self.bAutoConfig.grid(row=0,column=0)
        # Dropdown menu for selecting the MIDI output
        self.lbOutput = tk.Label(self.frBottomLeft, bg=colours.BG, fg=colours.TEXT, font="lucidatypewriter 12", text="MIDI PORT:")
        self.varOutput = tk.StringVar(value="Select port to open...")
        arr = []
        for i, port in enumerate(available_midi_output_ports):
            arr.append(f"{i} | {port}")
        self.varOutput.trace_add("write",self.open_midi_port)  # set up a callback on varOutput
        self.wOutputSelect = tk.OptionMenu(self.frBottomLeft,self.varOutput,*arr)
        self.wOutputSelect.configure(relief='groove',bg=colours.BG, fg=colours.TEXT, activebackground=colours.BG,highlightbackground=colours.BG, highlightcolor=colours.YELLOW,activeforeground=colours.YELLOW, width=25, height=1)
        # Grid the MIDI output selector
        self.lbOutput.grid(row=1,column=0)
        self.wOutputSelect.grid(row=2,column=0)
        # RIGHT -------------
        # Text box for displaying the serial buffer
        self.lbSerialBuffer = tk.Label(self.frBottomRight, font="lucidatypewriter 6", text="INCOMING SERIAL BUFFER", bg=colours.BG, fg=colours.TEXT)
        self.txtSerialBuffer = tk.Text(self.frBottomRight, height=5, width=20, bg=colours.DARK, fg=colours.YELLOW, font="lucidatypewriter 15", wrap="word")
        # Grid the output display
        self.lbSerialBuffer.grid(row=0,column=0,sticky='n')
        self.txtSerialBuffer.grid(row=1,column=0, sticky='n')
        # MAIN LOOP
        self.root.mainloop()
###################
# RUN THE THREAD
app = App()
############################################################################################################



# MAIN THREAD
SERIAL_INPUTS = {}

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
        if app.auto_config:
            # Parse the serial buffer line and configure the inputs accordingly
            try:
                alias = serial_buffer_line.split("_")[0] # ie 'VOLUME'
                input_type = serial_buffer_line.split("_")[1] # ie 'KNOB'
                value = serial_buffer_line.split("_")[2] # ie <an integer>
                value = int(value)
            except:
                print("Failed to convert serial buffer line to command value.")
            for m in app.INPUTS:
                if m['alias'] == alias:
                    print(f"Already matched input module {m['index']} to {alias}")
                    break
            else:
                app.add_input_module(alias)
                m = app.INPUTS[-1]
                # Let's match the type of input module to one of the types in midimaddi
                if input_type in INPUT_TYPES:
                    ## TODO: Add the midi index channel (note/cc index) to the input module
                    instance_inputModule = inputModule(alias, input_type, 0)
                    SERIAL_INPUTS[alias] =  instance_inputModule # < -- this is where we add the input module to the serial inputs dictionary
                    print(f"Added input module {alias} at index {m['index']}")
                else:
                    print(f"Input type {input_type} not recognised. IT needs to be one of: {INPUT_TYPES}")
                    break
                
        # WE AREN'T CONFIGURING INPUTS ################################################
        else:
            command_alias = serial_buffer_line.split("_")[0] # ie 'VOLUME'
            for alias, input_module in SERIAL_INPUTS.items():
                if input_module.alias == command_alias:
                    try:
                        value = serial_buffer_line.split("_")[2] # ie <an integer>
                        value = int(value)
                        input_module.update(value) # <------- PASS THE VALUE TO THE MIDI CONVERTER InputModule (listener.py)
                    except:
                        print("Failed to convert serial buffer line to command value.")
                    break
            if app.selected_input_module_alias == command_alias:
                app.varConfigDisplayValue.set(input_module.value)

    # Get Inputs #######################################################


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