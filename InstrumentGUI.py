r"""
Created by Alexander Yazdani, April 2023
This script was created to act as a GUI application for HP/Agilent/Keysight
multimeters and associated attenuators, power sensors, laser sources, etc.
To make into an application, run:
pyinstaller --onefile --noconsole \...filepath...\InstrumentGUI.py
"""

from tkinter import *
from tkinter import messagebox
from decimal import Decimal
import re
from Instruments import Instrument, Attenuator, PowerMeter

LIGHTWAVE_MULTIMETER_IDNS = ["8163A", "8163B"]
LIGHTWAVE_MEASURMENT_SYSTEM_IDNS = ["8164A", "8164B"]
LIGHTWAVE_MULTICHANNEL_SYSTEM_IDNS = ["8166A", "8166B"]
ATTENUATOR_IDNS = ["81560A", "81578A", "81576A", "81566A"]
POWER_SENSOR_IDNS = ["81630A", "81630B", "81632A", "81632B", "81635A",
                     "81635B", "81536A", "81536B"]
TUNABLE_LASER_SOURCE_IDNS = ["81600B", "81606A", "81607A", "81608A", "81609A",
                             "81602A", "N7776C", "N7778C", "N7779C", "N7711A",
                             "N7714A"]
REFERENCE_TRANSMITTER_IDNS = ["81490A", "81490B"]


class Instrument_GUI(Frame):

    """
    Main Window Init Methods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.inst = Instrument()
        self.init_window()
        self.attenuator_window_dict = {}
        self.power_meter_window_dict = {}
        self.tunable_laser_window_dict = {}
        self.reference_transmitter_window_dict = {}

    def init_window(self):
        """
        Window:
        """
        self.master.title("Instrument GUI")
        self.pack(fill=BOTH, expand=1)
        name = Label(self, text="Alex Yazdani, ODVT, Cisco Systems, 2023", fg="dark gray")
        name.place(x=3, y=150, anchor="sw")

        """
        Labels:
        """
        GPIB_label = Label(self, text="GPIB Address:")
        GPIB_label.place(relx=0.5, y=10, anchor="center")

        name_label = Label(self, text="Nickname:")
        name_label.place(relx=0.5, y=55, anchor="center")

        """
        Entry Fields:
        """
        self.GPIB_entry = Entry(self)
        self.GPIB_entry.place(relx=0.5, y=30, anchor="center")

        self.name_entry = Entry(self)
        self.name_entry.place(relx=0.5, y=75, anchor="center")

        """
        Buttons
        """
        connect = Button(self, text="Connect", command=self.connect_device)
        connect.place(relx=0.43, y=108, anchor="center")

        disconnect = Button(self, text="Disconnect", command=self.disconnect_device)
        disconnect.place(relx=0.555, y=108, anchor="center")

    """
    General Methods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    def validate_gpib_address(self, GPIB_address):
        try:
            gpib_match = re.search(r'GPIB\d+::\d+::INSTR', GPIB_address)
            if gpib_match:
                return True
            else:
                raise ValueError
        except ValueError:
            return False

    def validate_slot(self, slot):
        try:
            input_slot = int(slot)
            if input_slot < 0:
                return False
            return True
        except:
            return False

    def connect_device(self):
        try:
            self.disconnect_device()
        except:
            pass
        self.gpib_address = self.GPIB_entry.get()
        if self.validate_gpib_address(self.gpib_address):
            try:
                self.inst.gpib_address = self.gpib_address
                self.inst.nickname = self.name_entry.get()
                self.inst.connect(self.inst.gpib_address)
            except:
                messagebox.showerror("Error", "Could not connect to instrument.  If issue persists, reset controller and scan for instruments.")
                self.inst.reset()
                self.disconnect_device()
            self.master.title(f"Instrument - {self.gpib_address}       {self.inst.nickname}")
        else:
            messagebox.showerror("Error", "Invalid GPIB address.  Please use format: GPIB0::00::INSTR")  
        self.identify_instruments()
        self.open_instrument_windows()

    def disconnect_device(self):
        for slot in self.slot_dict:
            if self.slot_dict[slot] == "Attenuator":
                self.close_attenuator(slot)
            elif self.slot_dict[slot] == "Power Meter":
                self.close_power_meter(slot)
            elif self.slot_dict[slot] == "Tunable Laser Source":
                self.close_tunable_laser(slot)
            elif self.slot_dict[slot] == "Reference Transmitter":
                self.close_reference_transmitter(slot)
        self.inst.close()
        self.master.title(f"Instrument - Not Connected")
        self.attenuator_window_dict = {}
        self.power_meter_window_dict = {}
        self.tunable_laser_window_dict = {}
        self.reference_transmitter_window_dict = {}

    # def identify_instruments(self):
    #     self.slot_dict = {}
    #     chassis_IDN = self.inst.get_IDN().split(",")[1].replace("HP", "") 
    #     if (chassis_IDN in LIGHTWAVE_MULTIMETER_IDNS):
    #         self.chassis = "Lightwave Multimeter"
    #     elif (chassis_IDN in LIGHTWAVE_MEASURMENT_SYSTEM_IDNS):
    #         self.chassis = "Lightwave Measurement System"
    #     elif (chassis_IDN in LIGHTWAVE_MULTICHANNEL_SYSTEM_IDNS):
    #         self.chassis = "Lightwave Mutlichannel System"
    #     else:
    #         self.chassis = "Unknown"
    #     self.master.title(f"{self.chassis} - {self.gpib_address}       {self.inst.nickname}")
    #     IDN_list = ((self.inst.get_slot_IDNs()).replace(" ", "").replace("\n", "")).replace("HP", "").split(",")
    #     for slot in range(len(IDN_list)):
    #         if (self.chassis != "Lightwave Measurement System"):
    #             """
    #             This conditional corrects the value of the first slot, since some instruments use base 1 versus base 0
    #             """
    #             shifted_slot = slot + 1
    #         else:
    #             shifted_slot = slot
    #         if IDN_list[slot] == "":
    #             self.slot_dict[shifted_slot] = "Empty"
    #         elif IDN_list[slot] in ATTENUATOR_IDNS:
    #             self.slot_dict[shifted_slot] = "Attenuator"
    #         elif IDN_list[slot] in POWER_SENSOR_IDNS:
    #             self.slot_dict[shifted_slot] = "Power Meter"
    #         elif IDN_list[slot] in TUNABLE_LASER_SOURCE_IDNS:
    #             self.slot_dict[shifted_slot] = "Tunable Laser Source"
    #         elif IDN_list[slot] in REFERENCE_TRANSMITTER_IDNS:
    #             self.slot_dict[shifted_slot] = "Reference Transmitter"
    #         else:
    #             self.slot_dict[shifted_slot] = "Unknown"
    #         print(f"IDN List: {IDN_list}")

    def identify_instruments(self):
        self.slot_dict = {}
        chassis_IDN = self.inst.get_IDN().split(",")[1].replace("HP", "") 
        switcher = {
            True: "Lightwave Multimeter",
            chassis_IDN in LIGHTWAVE_MEASURMENT_SYSTEM_IDNS: "Lightwave Measurement System",
            chassis_IDN in LIGHTWAVE_MULTICHANNEL_SYSTEM_IDNS: "Lightwave Mutlichannel System",
        }
        self.chassis = switcher.get(True, "Unknown")
        self.master.title(f"{self.chassis} - {self.gpib_address}       {self.inst.nickname}")
        IDN_list = ((self.inst.get_slot_IDNs()).replace(" ", "").replace("\n", "")).replace("HP", "").split(",")
        for slot in range(len(IDN_list)):
            if (self.chassis != "Lightwave Measurement System"):
                """
                This conditional corrects the value of the first slot, since some instruments use base 1 versus base 0
                """
                shifted_slot = slot + 1
            else:
                shifted_slot = slot
            idn = IDN_list[slot]
            switcher = {
                idn == "": "Empty",
                idn in ATTENUATOR_IDNS: "Attenuator",
                idn in POWER_SENSOR_IDNS: "Power Meter",
                idn in TUNABLE_LASER_SOURCE_IDNS: "Tunable Laser Source",
                idn in REFERENCE_TRANSMITTER_IDNS: "Reference Transmitter",
            }
            self.slot_dict[shifted_slot] = switcher.get(True, "Unknown")
        print()
        print(f"IDN List: {IDN_list}")

    def open_instrument_windows(self):
        for slot in self.slot_dict:
            print(f"Slot {slot}: {self.slot_dict[slot]}")
            if self.slot_dict[slot] == "Attenuator":
                self.open_attenuator(slot)
            elif self.slot_dict[slot] == "Power Meter":
                self.open_power_meter(slot)
            elif self.slot_dict[slot] == "Tunable Laser Source":
                self.open_tunable_laser_source(slot)
            elif self.slot_dict[slot] == "Reference Transmitter":
                self.open_reference_transmitter(slot)
            # else:
            #     print(f"Slot {slot} is empty or unknown")


    """
    Attenuator Methods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    def open_attenuator(self, slot):
        self.attenuator_window_dict[slot] = Toplevel(root)
        self.attenuator_window_dict[slot].geometry("440x235")
        self.attenuator_window_dict[slot].configure(bg='#E6E6E6')
        self.attenuator_window_dict[slot].configure(borderwidth=0, highlightthickness=15, highlightbackground="light grey")
        self.attenuator_window_dict[slot].title(f"Attenuator - {self.gpib_address} - Slot {slot}      {self.inst.nickname}")
        self.attenuator_window_dict[slot].name = Label(self.attenuator_window_dict[slot], text="Alex Yazdani, ODVT, Cisco Systems, 2023", bg = "#E6E6E6", fg="dark gray")
        self.attenuator_window_dict[slot].name.place(x=3, y=205, anchor="sw")
        """
        Attenuator Screen
        """
        self.attenuator_window_dict[slot].output_screen = Frame(self.attenuator_window_dict[slot], bg="#579500", width=200, height=130, bd=2, relief=SOLID)
        self.attenuator_window_dict[slot].output_screen.place(x=10, y=10)

        self.attenuator_window_dict[slot].atten_label = Label(self.attenuator_window_dict[slot].output_screen, text=f" \u03B1: ", bg='#579500', fg="black", font=("Helvetica", 18, "bold"))
        self.attenuator_window_dict[slot].atten_label.place(x=1, y=1) 
        self.attenuator_window_dict[slot].atten_val = Label(self.attenuator_window_dict[slot].output_screen, text=f"--.--- dB", bg='#579500', fg="black", font=("Helvetica", 18, "bold"))
        self.attenuator_window_dict[slot].atten_val.place(relx=1, y=1, anchor="ne") 

        self.attenuator_window_dict[slot].wavelength_label = Label(self.attenuator_window_dict[slot].output_screen, text=f" \u03BB: ", bg='#579500', fg="black", font=("Helvetica", 18, "bold"))
        self.attenuator_window_dict[slot].wavelength_label.place(x=1, y=35)    
        self.attenuator_window_dict[slot].wavelength_val = Label(self.attenuator_window_dict[slot].output_screen, text=f"----.--- nm", bg='#579500', fg="black", font=("Helvetica", 18, "bold"))
        self.attenuator_window_dict[slot].wavelength_val.place(relx=1, y=35, anchor="ne")   

        self.attenuator_window_dict[slot].power_label = Label(self.attenuator_window_dict[slot].output_screen, text=f" Pset: ", bg='#579500', fg="black", font=("Helvetica", 13))
        self.attenuator_window_dict[slot].power_label.place(x=1, y=70)    
        self.attenuator_window_dict[slot].power_val = Label(self.attenuator_window_dict[slot].output_screen, text=f"--.--- dBm", bg='#579500', fg="black", font=("Helvetica", 13))
        self.attenuator_window_dict[slot].power_val.place(relx=1, y=70, anchor="ne")

        self.attenuator_window_dict[slot].offset_label = Label(self.attenuator_window_dict[slot].output_screen, text=f" Offset: ", bg='#579500', fg="black", font=("Helvetica", 13))
        self.attenuator_window_dict[slot].offset_label.place(x=1, y=95)   
        self.attenuator_window_dict[slot].offset_val = Label(self.attenuator_window_dict[slot].output_screen, text=f"--.--- dB", bg='#579500', fg="black", font=("Helvetica", 13))
        self.attenuator_window_dict[slot].offset_val.place(relx=1, y=95, anchor="ne")           

        """
        Attenuator Entry Fields
        """
        self.attenuator_window_dict[slot].attn_entry = Entry(self.attenuator_window_dict[slot])
        self.attenuator_window_dict[slot].attn_entry.place(x=240, y=20)
        self.attenuator_window_dict[slot].wave_entry = Entry(self.attenuator_window_dict[slot])
        self.attenuator_window_dict[slot].wave_entry.place(x=240, y=50)
        self.attenuator_window_dict[slot].pset_entry = Entry(self.attenuator_window_dict[slot])
        self.attenuator_window_dict[slot].pset_entry.place(x=240, y=80)
        self.attenuator_window_dict[slot].offset_entry = Entry(self.attenuator_window_dict[slot])
        self.attenuator_window_dict[slot].offset_entry.place(x=240, y=110)

        """
        Attenuator Buttons
        """
        self.attenuator_window_dict[slot].attenuator_attn_button = Button(self.attenuator_window_dict[slot], text="Set", command=lambda: self.attenuator_set_attn(slot, self.attenuator_window_dict[slot].attn_entry.get()))
        self.attenuator_window_dict[slot].attenuator_attn_button.place(relx=0.95, y=28, anchor="center")

        self.attenuator_window_dict[slot].attenuator_wave_button = Button(self.attenuator_window_dict[slot], text="Set", command=lambda: self.attenuator_set_wave(slot, self.attenuator_window_dict[slot].wave_entry.get()))
        self.attenuator_window_dict[slot].attenuator_wave_button.place(relx=0.95, y=58, anchor="center")   

        self.attenuator_window_dict[slot].attenuator_pset_button = Button(self.attenuator_window_dict[slot], text="Set", command=lambda: self.attenuator_set_pset(slot, self.attenuator_window_dict[slot].pset_entry.get()))
        self.attenuator_window_dict[slot].attenuator_pset_button.place(relx=0.95, y=88, anchor="center") 

        self.attenuator_window_dict[slot].attenuator_offset_button = Button(self.attenuator_window_dict[slot], text="Set", command=lambda: self.attenuator_set_offset(slot, self.attenuator_window_dict[slot].offset_entry.get()))
        self.attenuator_window_dict[slot].attenuator_offset_button.place(relx=0.95, y=118, anchor="center") 

        self.attenuator_window_dict[slot].attenuator_refresh = Button(self.attenuator_window_dict[slot], text="Refresh Values", command=lambda: self.attenuator_refresh_output(slot))
        self.attenuator_window_dict[slot].attenuator_refresh.place(relx=0.5, y=163, anchor="center")

        """
        Update the output
        """
        self.attenuator_refresh_output(slot)

    def close_attenuator(self, slot):
        self.attenuator_window_dict[slot].destroy()

    def get_attenuator_values(self, slot):
        try:
            self.attenuator_window_dict[slot].attenuation = round(Decimal(self.inst.attenuator_get_attenuation(slot)), 3)
            self.attenuator_window_dict[slot].wavelength = round(Decimal(self.inst.attenuator_get_wavelength(slot))*1000000000, 3)
            self.attenuator_window_dict[slot].offset = round(Decimal(self.inst.attenuator_get_offset(slot)), 3)
            self.attenuator_window_dict[slot].power = round(Decimal(self.inst.attenuator_get_power_out(slot)), 3)
        except:
            self.inst.reset()
            self.attenuator_window_dict[slot].attenuation = "--.---"
            self.attenuator_window_dict[slot].wavelength = "----.---"
            self.attenuator_window_dict[slot].offset = "--.---"
            self.attenuator_window_dict[slot].power = "--.---"
            self.update_attenuator_output_values(slot)
            messagebox.showerror("Error", "Connection Interrupted.")

    def update_attenuator_output_values(self, slot):
        self.attenuator_window_dict[slot].atten_val.config(text=f"{self.attenuator_window_dict[slot].attenuation} dB")
        self.attenuator_window_dict[slot].wavelength_val.config(text=f"{self.attenuator_window_dict[slot].wavelength} nm")
        self.attenuator_window_dict[slot].power_val.config(text=f"{self.attenuator_window_dict[slot].power} dBm")
        self.attenuator_window_dict[slot].offset_val.config(text=f"{self.attenuator_window_dict[slot].offset} dB")

    def attenuator_refresh_output(self, slot):
        self.get_attenuator_values(slot)
        self.update_attenuator_output_values(slot)

    def attenuator_set_attn(self, slot, value):
        self.inst.attenuator_set_attenuation(slot, value)
        self.attenuator_refresh_output(slot)

    def attenuator_set_wave(self, slot, value):
        self.inst.attenuator_set_wavelength(slot, value)
        self.attenuator_refresh_output(slot)
    
    def attenuator_set_pset(self, slot, value):
        self.inst.attenuator_set_power_out(slot, value)
        self.attenuator_refresh_output(slot)

    def attenuator_set_offset(self, slot, value):
        self.inst.attenuator_set_offset(slot, value)
        self.attenuator_refresh_output(slot)
    
    def attenuator_reset_device(self, slot):
        self.inst.reset()
        self.attenuator_refresh_output(slot)


    """
    Power Meter Methods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    def open_power_meter(self, slot):
        self.power_meter_window_dict[slot] = Toplevel(root)
        self.power_meter_window_dict[slot].geometry("440x235")
        self.power_meter_window_dict[slot].configure(bg='#E6E6E6')
        self.power_meter_window_dict[slot].configure(borderwidth=0, highlightthickness=15, highlightbackground="light grey")
        self.power_meter_window_dict[slot].title(f"Power Meter - {self.gpib_address} - Slot {slot}      {self.name_entry.get()}")
        self.power_meter_window_dict[slot].name = Label(self.power_meter_window_dict[slot], text="Alex Yazdani, ODVT, Cisco Systems, 2023", bg = "#E6E6E6", fg="dark gray")
        self.power_meter_window_dict[slot].name.place(x=3, y=205, anchor="sw")
        """
        Power Meter Screen
        """
        self.power_meter_window_dict[slot].power_meter_output_screen1 = Frame(self.power_meter_window_dict[slot], bg="#579500", width=200, height=65, bd=2, relief=SOLID)
        self.power_meter_window_dict[slot].power_meter_output_screen1.place(x=10, y=10)
        self.power_meter_window_dict[slot].power_meter_output_screen2 = Frame(self.power_meter_window_dict[slot], bg="#579500", width=200, height=65, bd=2, relief=SOLID)
        self.power_meter_window_dict[slot].power_meter_output_screen2.place(x=10, y=72)

        self.power_meter_window_dict[slot].power_meter_channel1_label = Label(self.power_meter_window_dict[slot], text="1", bg='#579500', fg="black", font=("Helvetica", 8))
        self.power_meter_window_dict[slot].power_meter_channel1_label.place(x=12, y=12)
        self.power_meter_window_dict[slot].power_meter_channel2_label = Label(self.power_meter_window_dict[slot], text="2", bg='#579500', fg="black", font=("Helvetica", 8))
        self.power_meter_window_dict[slot].power_meter_channel2_label.place(x=12, y=74)

        self.power_meter_window_dict[slot].power_meter_P1_label = Label(self.power_meter_window_dict[slot], text="P:", bg='#579500', fg="black", font=("Helvetica", 16, "bold"))
        self.power_meter_window_dict[slot].power_meter_P1_label.place(x=35, y=12)
        self.power_meter_window_dict[slot].power_meter_W1_label = Label(self.power_meter_window_dict[slot], text=" \u03BB:", bg='#579500', fg="black", font=("Helvetica", 16, "bold"))
        self.power_meter_window_dict[slot].power_meter_W1_label.place(x=30, y=42)

        self.power_meter_window_dict[slot].power_meter_P2_label = Label(self.power_meter_window_dict[slot], text="P:", bg='#579500', fg="black", font=("Helvetica", 16, "bold"))
        self.power_meter_window_dict[slot].power_meter_P2_label.place(x=35, y=74)
        self.power_meter_window_dict[slot].power_meter_W2_label = Label(self.power_meter_window_dict[slot], text=" \u03BB:", bg='#579500', fg="black", font=("Helvetica", 16, "bold"))
        self.power_meter_window_dict[slot].power_meter_W2_label.place(x=30, y=104)

        self.power_meter_window_dict[slot].power_meter_P1_val = Label(self.power_meter_window_dict[slot].power_meter_output_screen1, text="--.--- dBm ", bg='#579500', fg="black", font=("Helvetica", 16, "bold"))
        self.power_meter_window_dict[slot].power_meter_P1_val.place(relx=1, y=1, anchor = "ne")
        self.power_meter_window_dict[slot].power_meter_W1_val = Label(self.power_meter_window_dict[slot].power_meter_output_screen1, text="----.--- nm ", bg='#579500', fg="black", font=("Helvetica", 16, "bold"))
        self.power_meter_window_dict[slot].power_meter_W1_val.place(relx=1, y=31, anchor = "ne")

        self.power_meter_window_dict[slot].power_meter_P2_val = Label(self.power_meter_window_dict[slot].power_meter_output_screen2, text="--.--- dBm ", bg='#579500', fg="black", font=("Helvetica", 16, "bold"))
        self.power_meter_window_dict[slot].power_meter_P2_val.place(relx=1, y=1, anchor = "ne")
        self.power_meter_window_dict[slot].power_meter_W2_val = Label(self.power_meter_window_dict[slot].power_meter_output_screen2, text="----.--- nm ", bg='#579500', fg="black", font=("Helvetica", 16, "bold"))
        self.power_meter_window_dict[slot].power_meter_W2_val.place(relx=1, y=31, anchor = "ne")

        """
        Power Meter Labels:
        """
        self.power_meter_window_dict[slot].power_meter_unit1_label = Label(self.power_meter_window_dict[slot], bg = "#E6E6E6", text = "Units:")
        self.power_meter_window_dict[slot].power_meter_unit1_label.place(x = 240, y = 17)

        self.power_meter_window_dict[slot].power_meter_unit2_label = Label(self.power_meter_window_dict[slot], bg = "#E6E6E6", text = "Units:")
        self.power_meter_window_dict[slot].power_meter_unit2_label.place(x = 240, y = 79)

        """
        Power Meter Entry Fields:
        """
        self.power_meter_window_dict[slot].power_meter_wave1_entry = Entry(self.power_meter_window_dict[slot])
        self.power_meter_window_dict[slot].power_meter_wave1_entry.place(x = 240, y = 50)

        self.power_meter_window_dict[slot].power_meter_wave2_entry = Entry(self.power_meter_window_dict[slot])
        self.power_meter_window_dict[slot].power_meter_wave2_entry.place(x = 240, y = 112)

        """
        Power Meter Buttons:
        """
        self.power_meter_window_dict[slot].power_meter_wave1_button = Button(self.power_meter_window_dict[slot], text = "Set", command=lambda: self.power_meter_set_wave1(slot, self.power_meter_window_dict[slot].power_meter_wave1_entry.get()))
        self.power_meter_window_dict[slot].power_meter_wave1_button.place(x = 375, y = 48) 

        self.power_meter_window_dict[slot].power_meter_wave2_button = Button(self.power_meter_window_dict[slot], text = "Set", command=lambda: self.power_meter_set_wave2(slot, self.power_meter_window_dict[slot].power_meter_wave2_entry.get()))
        self.power_meter_window_dict[slot].power_meter_wave2_button.place(x = 375, y = 110)  

        self.power_meter_window_dict[slot].power_meter_unitW1 = Button(self.power_meter_window_dict[slot], text=" W ", command = lambda: self.power_meter_set_units(slot, 1, 1) )
        self.power_meter_window_dict[slot].power_meter_unitW1.place(x = 280, y = 17)

        self.power_meter_window_dict[slot].power_meter_unitdBm1 = Button(self.power_meter_window_dict[slot], text = "dBm", command = lambda: self.power_meter_set_units(slot, 1, 0) )
        self.power_meter_window_dict[slot].power_meter_unitdBm1.place(x = 320, y = 17)

        self.power_meter_window_dict[slot].power_meter_unitW2 = Button(self.power_meter_window_dict[slot], text=" W ", command = lambda: self.power_meter_set_units(slot, 2, 1) )
        self.power_meter_window_dict[slot].power_meter_unitW2.place(x = 280, y = 79)

        self.power_meter_window_dict[slot].power_meter_unitdBm2 = Button(self.power_meter_window_dict[slot], text = "dBm", command = lambda: self.power_meter_set_units(slot, 2, 0) )
        self.power_meter_window_dict[slot].power_meter_unitdBm2.place(x = 320, y = 79)

        self.power_meter_window_dict[slot].power_meter_refresh = Button(self.power_meter_window_dict[slot], text = "Refresh Values", command=lambda: self.power_meter_refresh_output(slot))
        self.power_meter_window_dict[slot].power_meter_refresh.place(relx=0.5, y = 163, anchor="center")
        
        """
        Update the Output:
        """
        self.power_meter_refresh_output(slot)

    def get_powermeter_values(self, slot):

        try:
            self.wavelength1 = float(self.inst.power_meter_get_wavelength(slot, 1))*1000000000
            if self.wavelength1 > 2000:
                self.wavelength1 = "----.---"
            else:
                self.wavelength1 = round(Decimal(self.wavelength1), 3)
        except:
            self.wavelength1 = "----.---"
            self.inst.reset()

        try:
            self.power1 = float(self.inst.power_meter_get_power(slot, 1))
            if self.power1 > 120:
                self.power1 = "--.---"
            else:
                self.power1 = Decimal(self.power1)
        except:
            self.power1 = "--.---"
            self.inst.reset()

        try:
            self.wavelength2 = float(self.inst.power_meter_get_wavelength(slot, 2))*1000000000
            if self.wavelength2 > 2000:
                self.wavelength2 = "----.---"
            else:
                self.wavelength2 = round(Decimal(self.wavelength2), 3) 
        except:
            self.wavelength2 = "----.---"
            self.inst.reset()
        
        try:
            self.power2 = float(self.inst.power_meter_get_power(slot, 2))
            if self.power2 > 120:
                self.power2 = "--.---"
            else:
                self.power2 = Decimal(self.power2)
        except:
            self.power2 = "--.---"
            self.inst.reset()

        self.power_meter_window_dict[slot].unit1 = self.inst.power_meter_get_unit(slot, 1)
        if self.power_meter_window_dict[slot].unit1 == "W":
            if abs(self.power1) < 0.01:
                self.power1 *=1000
                self.power_meter_window_dict[slot].unit1 ="mW"
            if abs(self.power1) < 0.01:
                self.power1 *=1000
                self.power_meter_window_dict[slot].unit1 ="uW"
            if abs(self.power1) < 0.01:
                self.power1 *=1000
                self.power_meter_window_dict[slot].unit1 ="nW"
        if type(self.power1) != str:
            self.power1 = round(self.power1, 4)

        self.power_meter_window_dict[slot].unit2 = self.inst.power_meter_get_unit(slot, 2)
        if self.power_meter_window_dict[slot].unit2 == "W":
            if abs(self.power2) < 0.01:
                self.power2 *=1000
                self.power_meter_window_dict[slot].unit2 ="mW"
            if abs(self.power2) < 0.01:
                self.power2 *=1000
                self.power_meter_window_dict[slot].unit2="uW"
            if abs(self.power2) < 0.01:
                self.power2 *=1000
                self.power_meter_window_dict[slot].unit2 ="nW"
        if type(self.power2) != str:
            self.power2 = round(self.power2, 4)


    def update_power_meter_output_values(self, slot):
        self.power_meter_window_dict[slot].power_meter_P1_val.config(text=f"{self.power1} {self.power_meter_window_dict[slot].unit1} ")
        self.power_meter_window_dict[slot].power_meter_W1_val.config(text=f"{self.wavelength1} nm ")
        self.power_meter_window_dict[slot].power_meter_P2_val.config(text=f"{self.power2} {self.power_meter_window_dict[slot].unit2} ")
        self.power_meter_window_dict[slot].power_meter_W2_val.config(text=f"{self.wavelength2} nm ")

    def power_meter_refresh_output(self, slot):
        self.get_powermeter_values(slot)
        self.update_power_meter_output_values(slot)

    def power_meter_set_wave1(self, slot, value, channel=1):
        self.inst.power_meter_set_wavelength(slot, value, channel)
        self.power_meter_refresh_output(slot)

    def power_meter_set_wave2(self, slot, value, channel=2):
        self.inst.power_meter_set_wavelength(slot, value, channel)
        self.power_meter_refresh_output(slot)
    
    def power_meter_set_units(self, slot, channel, unit):
        self.inst.power_meter_set_unit(slot, channel, unit)
        self.power_meter_refresh_output(slot)

    def close_power_meter(self, slot):
        self.power_meter_window_dict[slot].destroy()

    """
    Tunable Laser Source Methods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    def open_tunable_laser_source(self, slot):
        self.tunable_laser_window_dict[slot] = Toplevel(root)
        self.tunable_laser_window_dict[slot].geometry("440x203")
        self.tunable_laser_window_dict[slot].configure(bg='#E6E6E6')
        self.tunable_laser_window_dict[slot].configure(borderwidth=0, highlightthickness=15, highlightbackground="light grey")
        self.tunable_laser_window_dict[slot].title(f"Tunable Laser - {self.gpib_address} - Slot {slot}      {self.inst.nickname}")
        self.tunable_laser_window_dict[slot].name = Label(self.tunable_laser_window_dict[slot], text="Alex Yazdani, ODVT, Cisco Systems, 2023", bg = "#E6E6E6", fg="dark gray")
        self.tunable_laser_window_dict[slot].name.place(x=3, y=173, anchor="sw")

        """
        Tunable Laser Source Screen:
        """
        self.tunable_laser_window_dict[slot].output_screen = Frame(self.tunable_laser_window_dict[slot], bg="white", width=200, height=98, bd=2, relief=SOLID)
        self.tunable_laser_window_dict[slot].output_screen.place(x=10, y=10)

        self.tunable_laser_window_dict[slot].wavelength_label = Label(self.tunable_laser_window_dict[slot].output_screen, text=f" \u03BB: ", bg='white', fg="black", font=("Helvetica", 18, "bold"))
        self.tunable_laser_window_dict[slot].wavelength_label.place(x=1, y=1) 
        self.tunable_laser_window_dict[slot].wavelength_val = Label(self.tunable_laser_window_dict[slot].output_screen, text=f"--.--- nm", bg='white', fg="black", font=("Helvetica", 18, "bold"))
        self.tunable_laser_window_dict[slot].wavelength_val.place(relx=1, y=1, anchor="ne")

        self.tunable_laser_window_dict[slot].power_label = Label(self.tunable_laser_window_dict[slot].output_screen, text=f" P: ", bg='white', fg="black", font=("Helvetica", 18, "bold"))
        self.tunable_laser_window_dict[slot].power_label.place(x=1, y=30) 
        self.tunable_laser_window_dict[slot].power_val = Label(self.tunable_laser_window_dict[slot].output_screen, text=f"--.--- dBm", bg='white', fg="black", font=("Helvetica", 18, "bold"))
        self.tunable_laser_window_dict[slot].power_val.place(relx=1, y=30, anchor="ne")

        self.tunable_laser_window_dict[slot].state_label = Label(self.tunable_laser_window_dict[slot].output_screen, text=f" State: ", bg='white', fg="black", font=("Helvetica", 18, "bold"))
        self.tunable_laser_window_dict[slot].state_label.place(x=1, y=59) 
        self.tunable_laser_window_dict[slot].state_val = Label(self.tunable_laser_window_dict[slot].output_screen, text=f"----- ", bg='white', fg="black", font=("Helvetica", 18, "bold"))
        self.tunable_laser_window_dict[slot].state_val.place(relx=1, y=59, anchor="ne")

        """
        Tunable Laser Source Buttons:
        """
        self.tunable_laser_window_dict[slot].tunable_laser_source_refresh = Button(self.tunable_laser_window_dict[slot], text = "Refresh Values", command=lambda: self.tunable_laser_source_refresh_output(slot))
        self.tunable_laser_window_dict[slot].tunable_laser_source_refresh.place(relx=0.5, y = 131, anchor="center")

        self.tunable_laser_window_dict[slot].tunable_laser_source_enable = Button(self.tunable_laser_window_dict[slot], text = "Enable", command=lambda: self.tunable_laser_source_enable(slot))
        self.tunable_laser_window_dict[slot].tunable_laser_source_enable.place(relx=0.58, rely=0.33, anchor="center")

        self.tunable_laser_window_dict[slot].tunable_laser_source_disable = Button(self.tunable_laser_window_dict[slot], text = "Disable", command=lambda: self.tunable_laser_source_disable(slot))
        self.tunable_laser_window_dict[slot].tunable_laser_source_disable.place(relx=0.58, rely=0.5, anchor="center")

        self.tunable_laser_window_dict[slot].tunable_laser_source_wavelength_button = Button(self.tunable_laser_window_dict[slot], text = "Set", command=lambda: self.tunable_laser_source_set_wavelength(slot, self.tunable_laser_window_dict[slot].tunable_laser_source_wavelength_entry.get()))
        self.tunable_laser_window_dict[slot].tunable_laser_source_wavelength_button.place(x = 345, y = 16) 

        """
        Tunable Laser Source Entry Fields:
        """
        self.tunable_laser_window_dict[slot].tunable_laser_source_wavelength_entry = Entry(self.tunable_laser_window_dict[slot])
        self.tunable_laser_window_dict[slot].tunable_laser_source_wavelength_entry.place(x = 215, y = 20)

        """
        Update the Output:
        """
        self.tunable_laser_source_refresh_output(slot)


    def get_tunable_laser_values(self, slot):
        self.tunable_laser_window_dict[slot].wavelength = round(Decimal(self.inst.tunable_laser_get_wavelength(slot))*1000000000, 4)
        self.tunable_laser_window_dict[slot].power = round(Decimal(self.inst.tunable_laser_get_power(slot)), 3)
        self.tunable_laser_window_dict[slot].state = self.inst.tunable_laser_get_state(slot)

    def update_tunable_laser_source_values(self, slot):
        self.tunable_laser_window_dict[slot].wavelength_val.config(text = f"{self.tunable_laser_window_dict[slot].wavelength} nm")
        self.tunable_laser_window_dict[slot].power_val.config(text = f"{self.tunable_laser_window_dict[slot].power} dBm")
        self.tunable_laser_window_dict[slot].state_val.config(text = f"{self.tunable_laser_window_dict[slot].state} ")

    def tunable_laser_source_refresh_output(self, slot):
        self.get_tunable_laser_values(slot)
        self.update_tunable_laser_source_values(slot)

    def tunable_laser_source_enable(self, slot):
        self.inst.enable(slot)
        self.tunable_laser_source_refresh_output(slot)
    
    def tunable_laser_source_disable(self, slot):
        self.inst.disable(slot)
        self.tunable_laser_source_refresh_output(slot)

    def tunable_laser_source_set_wavelength(self, slot, wavelength):
        self.inst.tunable_laser_set_wavelength(slot, wavelength)
        self.tunable_laser_source_refresh_output(slot)

    def close_tunable_laser(self, slot):
        self.tunable_laser_window_dict[slot].destroy()
    """
    Reference Transmitter Methods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    def open_reference_transmitter(self, slot):
        self.reference_transmitter_window_dict[slot] = Toplevel(root)
        self.reference_transmitter_window_dict[slot].geometry("400x170")
        self.reference_transmitter_window_dict[slot].configure(bg='#E6E6E6')
        self.reference_transmitter_window_dict[slot].configure(borderwidth=0, highlightthickness=15, highlightbackground="light grey")
        self.reference_transmitter_window_dict[slot].title(f"Reference Transmitter - {self.gpib_address} - Slot {slot}      {self.inst.nickname}")
        self.reference_transmitter_window_dict[slot].name = Label(self.reference_transmitter_window_dict[slot], text="Alex Yazdani, ODVT, Cisco Systems, 2023", bg = "#E6E6E6", fg="dark gray")
        self.reference_transmitter_window_dict[slot].name.place(x=3, y=140, anchor="sw")
    
        """
        Reference Transmitter Screen
        """
        self.reference_transmitter_window_dict[slot].output_screen = Frame(self.reference_transmitter_window_dict[slot], bg="white", width=200, height=70, bd=2, relief=SOLID)
        self.reference_transmitter_window_dict[slot].output_screen.place(x=10, y=10)

        self.reference_transmitter_window_dict[slot].wavelength_label = Label(self.reference_transmitter_window_dict[slot].output_screen, text=f" \u03BB: ", bg='white', fg="black", font=("Helvetica", 18, "bold"))
        self.reference_transmitter_window_dict[slot].wavelength_label.place(x=1, y=1)
        self.reference_transmitter_window_dict[slot].wavelength_val = Label(self.reference_transmitter_window_dict[slot].output_screen, text=f"--.--- nm", bg='white', fg="black", font=("Helvetica", 18, "bold"))
        self.reference_transmitter_window_dict[slot].wavelength_val.place(relx=1, y=1, anchor="ne")

        self.reference_transmitter_window_dict[slot].state_label = Label(self.reference_transmitter_window_dict[slot].output_screen, text=f"State: ",  bg='white', fg="black", font=("Helvetica", 18, "bold"))
        self.reference_transmitter_window_dict[slot].state_label.place(x=1, y=30)
        self.reference_transmitter_window_dict[slot].state_val = Label(self.reference_transmitter_window_dict[slot].output_screen, text=f"----- ",  bg='white', fg="black", font=("Helvetica", 18, "bold"))
        self.reference_transmitter_window_dict[slot].state_val.place(relx=1, y=30, anchor="ne")

        """
        Reference Transmitter Buttons:
        """
        self.reference_transmitter_window_dict[slot].reference_transmitter_refresh = Button(self.reference_transmitter_window_dict[slot], text = "Refresh Values", command=lambda: self.reference_transmitter_refresh_output(slot))
        self.reference_transmitter_window_dict[slot].reference_transmitter_refresh.place(relx=0.5, y = 103, anchor="center")

        self.reference_transmitter_window_dict[slot].reference_transmitter_enable = Button(self.reference_transmitter_window_dict[slot], text = "Enable", command=lambda: self.reference_transmitter_enable(slot))
        self.reference_transmitter_window_dict[slot].reference_transmitter_enable.place(relx=0.75, rely=0.2, anchor="center")

        self.reference_transmitter_window_dict[slot].reference_transmitter_disable = Button(self.reference_transmitter_window_dict[slot], text = "Disable", command=lambda: self.reference_transmitter_disable(slot))
        self.reference_transmitter_window_dict[slot].reference_transmitter_disable.place(relx=0.75, rely=0.4, anchor="center")

        self.reference_transmitter_window_dict[slot].reference_transmitter_disable = Button(self.reference_transmitter_window_dict[slot], text = "Tx Recal", command=lambda: self.inst.instrument.write(f"SOUR{slot}:TRAN:REC"))
        self.reference_transmitter_window_dict[slot].reference_transmitter_disable.place(relx=0.91, rely=0.3, anchor="center")

        """
        Update the Output:
        """
        self.reference_transmitter_refresh_output(slot)

    def get_reference_transmitter_values(self, slot):
        self.reference_transmitter_window_dict[slot].wavelength = round(Decimal(self.inst.reference_transmitter_get_wavelength(slot))*1000000000, 1)
        self.reference_transmitter_window_dict[slot].state = self.inst.reference_transmitter_get_state(slot)

    def update_reference_transmitter_values(self, slot):
        self.reference_transmitter_window_dict[slot].wavelength_val.config(text = f"{self.reference_transmitter_window_dict[slot].wavelength} nm")
        self.reference_transmitter_window_dict[slot].state_val.config(text = f"{self.reference_transmitter_window_dict[slot].state}")

    def reference_transmitter_refresh_output(self, slot):
        self.get_reference_transmitter_values(slot)
        self.update_reference_transmitter_values(slot)

    def reference_transmitter_enable(self, slot):
        self.inst.enable(slot)
        self.reference_transmitter_refresh_output(slot)
    
    def reference_transmitter_disable(self, slot):
        self.inst.disable(slot)
        self.reference_transmitter_refresh_output(slot)
    
    def reference_transmitter_tx_recal(self, slot):
        self.inst.reference_transmitter_tx_recal(slot)
        self.reference_transmitter_refresh_output(slot)

    def close_reference_transmitter(self, slot):
        self.reference_transmitter_window_dict[slot].destroy()

"""
Main Window Startup and config ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
root = Tk()
root.configure(bg='white')
root.geometry("590x180")
root.configure(borderwidth=0, highlightthickness=15, highlightbackground="light grey")
GUI_Window = Instrument_GUI(root)
root.mainloop()
