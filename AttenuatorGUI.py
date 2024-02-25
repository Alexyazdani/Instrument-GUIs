r"""
Created by Alexander Yazdani, April 2023
This script was created to act as a GUI application for HP/Agilent attenuators
to make into an application, run:
pyinstaller --onefile --noconsole \...filepath...\AttenuatorGUI.py
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
POWER_SENSOR_IDNS = ["81632A", "81632B", "81635A", "81635B", "81536A", "81536B"]
TUNABLE_LASER_SOURCE_IDNS = ["81600B", "81606A", "81607A", "81608A", "81609A", "81602A", "N7776C", "N7778C", "N7779C", "N7711A", "N7714A"]
REFERENCE_TRANSMITTER_IDNS = ["81490A", "81490B"]


class Attenuator_GUI(Frame):

    def __init__(self, master = None):
        Frame.__init__(self, master)
        self.master = master
        self.attenuator = Attenuator()
        self.init_window()

    def init_window(self):
        
        """
        Window:
        """
        self.master.title(f"Attenuator - Not Connected")
        self.pack(fill=BOTH, expand=1)
        name = Label(self, text="Alex Yazdani, ODVT, Cisco Systems, 2023", fg="dark gray")
        name.place(x=3, y=205, anchor="sw")
        self.init_screen()

        """
        Labels:
        """
        GPIB_label = Label(self, text = "GPIB Address:")
        GPIB_label.place(x = 10, y = 5)

        slot_label = Label(self, text = "Slot / Input:")
        slot_label.place(x = 10, y = 50)

        name_label = Label(self, text = "Nickname:")
        name_label.place(x = 10, y = 95)

        """
        Entry Fields:
        """
        self.GPIB_entry = Entry(self)
        self.GPIB_entry.place(x = 10, y = 25)

        self.slot_entry = Entry(self)
        self.slot_entry.place(x = 10, y = 70)

        self.name_entry = Entry(self)
        self.name_entry.place(x = 10, y = 115)

        self.attn_entry = Entry(self)
        self.attn_entry.place(x = 390, y = 20)

        self.wave_entry = Entry(self)
        self.wave_entry.place(x = 390, y = 50)

        self.pset_entry = Entry(self)
        self.pset_entry.place(x = 390, y = 80)

        self.offset_entry = Entry(self)
        self.offset_entry.place(x = 390, y = 110)

        """
        Buttons:
        """
        connect = Button(self, text = "Connect", command=self.connect_device)
        connect_x = 10 + self.name_entry.winfo_reqwidth() / 2 - connect.winfo_reqwidth() / 2
        connect.place(x=connect_x, y=153)

        attn_button = Button(self, text = "Set", command=lambda: self.set_attn(self.slot_number, self.attn_entry.get()))
        attn_button.place(x = 520, y = 18)

        wave_button = Button(self, text = "Set", command=lambda: self.set_wave(self.slot_number, self.wave_entry.get()))
        wave_button.place(x = 520, y = 48)   

        pset_button = Button(self, text = "Set", command=lambda: self.set_pset(self.slot_number, self.pset_entry.get()))
        pset_button.place(x = 520, y = 78) 

        offset_button = Button(self, text = "Set", command=lambda: self.set_offset(self.slot_number, self.offset_entry.get()))
        offset_button.place(x = 520, y = 108) 
        
        disconnect = Button(self, text = "Disconnect", command=self.disconnect_device)
        disconnect.place(x=420, y=153)

        # reset_device = Button(self, text = "Reset Device", command=self.reset_device)
        # reset_device.place(x=220, y=188)

        # quit = Button(self, text = "Quit", command=self.exit_application)
        # quit.place(x= 430, y = 180)

    def init_screen(self):

        self.output_screen = Frame(self, bg="#579500", width=200, height=130, bd=2, relief=SOLID)
        self.output_screen.place(x=160, y=10)

        self.atten_label = Label(self.output_screen, text=f" \u03B1: ", bg='#579500', fg="black", font=("Helvetica", 18, "bold"))
        self.atten_label.place(x=1,y=1) 
        self.atten_val = Label(self.output_screen, text=f"--.--- dB", bg='#579500', fg="black", font=("Helvetica", 18, "bold"))
        self.atten_val.place(relx=1, y=1, anchor = "ne") 

        self.wavelength_label = Label(self.output_screen, text=f" \u03BB: ", bg='#579500', fg="black", font=("Helvetica", 18, "bold"))
        self.wavelength_label.place(x=1,y=35)    
        self.wavelength_val = Label(self.output_screen, text=f"----.--- nm", bg='#579500', fg="black", font=("Helvetica", 18, "bold"))
        self.wavelength_val.place(relx=1,y=35, anchor = "ne")   

        self.power_label = Label(self.output_screen, text=f" Pset: ", bg='#579500', fg="black", font=("Helvetica", 13))
        self.power_label.place(x=1,y=70)    
        self.power_val = Label(self.output_screen, text=f"--.--- dBm", bg='#579500', fg="black", font=("Helvetica", 13))
        self.power_val.place(relx=1,y=70, anchor = "ne")

        self.offset_label = Label(self.output_screen, text=f" Offset: ", bg='#579500', fg="black", font=("Helvetica", 13))
        self.offset_label.place(x=1,y=95)   
        self.offset_val = Label(self.output_screen, text=f"--.--- dB", bg='#579500', fg="black", font=("Helvetica", 13))
        self.offset_val.place(relx=1,y=95, anchor = "ne")           

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
        gpib_address = self.GPIB_entry.get()
        self.slot_number = self.slot_entry.get()
        if self.validate_gpib_address(gpib_address):
            if self.validate_slot(self.slot_number):
                try:
                    self.attenuator.gpib_address = gpib_address
                    self.attenuator.nickname = self.name_entry.get()
                    self.attenuator.connect(self.attenuator.gpib_address)
                except:
                    messagebox.showerror("Error", "Could not connect to instrument.  If issue persists, reset controller and scan for instruments.")
                    self.disconnect_device()
                self.master.title(f"Attenuator - {gpib_address} - Slot {self.slot_number}        {self.name_entry.get()}")
                self.refresh = Button(self, text = "Refresh Values", command=lambda: self.refresh_output(self.slot_number))
                self.refresh.place(x=215, y = 153)
                try:
                    self.attenuator.enable(self.slot_number)
                    self.get_attenuator_values(self.slot_number)
                    self.update_output_values()
                except:
                    messagebox.showerror("Error", "Connection lost, failed, or never established.  If issue persists, reset controller and scan for instruments.")
                    self.reset_device()
                    self.disconnect_device()
            else:
                messagebox.showerror("Error", "Invalid slot entry.")
        else:
            messagebox.showerror("Error", "Invalid GPIB address.  Please use format: GPIB0::00::INSTR")        

    def get_attenuator_values(self, slot):
        try:
            self.attenuation = round(Decimal(self.attenuator.get_attenuation(slot)), 3)
            self.wavelength = round(Decimal(self.attenuator.get_wavelength(slot))*1000000000, 3)
            self.offset = round(Decimal(self.attenuator.get_offset(slot)), 3)
            self.power = round(Decimal(self.attenuator.get_power_out(slot)), 3)
        except:
            self.attenuation = "--.---"
            self.wavelength = "----.---"
            self.offset = "--.---"
            self.power = "--.---"
            self.update_output_values()
            messagebox.showerror("Error", "Connection lost, failed, or never established.")

    def update_output_values(self):
        self.atten_val.config(text=f"{self.attenuation} dB")
        self.wavelength_val.config(text=f"{self.wavelength} nm")
        self.power_val.config(text=f"{self.power} dBm")
        self.offset_val.config(text=f"{self.offset} dB")

    def refresh_output(self, slot):
        self.get_attenuator_values(slot)
        self.update_output_values()

    def set_attn(self, slot, value):
        self.attenuator.set_attenuation(slot, value)
        self.refresh_output(slot)

    def set_wave(self, slot, value):
        self.attenuator.set_wavelength(slot, value)
        self.refresh_output(slot)
    
    def set_pset(self, slot, value):
        self.attenuator.set_power_out(slot, value)
        self.refresh_output(slot)

    def set_offset(self, slot, value):
        self.attenuator.set_offset(slot, value)
        self.refresh_output(slot)
    
    def reset_device(self):
        self.attenuator.reset()
        # self.connect_device()
        self.refresh_output(self.slot_number)

    def disconnect_device(self):
        self.attenuator.close()
        self.master.title(f"Attenuator - Not Connected")
        self.atten_val.config(text=f"--.--- dB")
        self.wavelength_val.config(text=f"----.--- nm")
        self.power_val.config(text=f"--.--- dBm")
        self.offset_val.config(text=f"--.--- dB")
        self.refresh.destroy()

    def exit_application(self):
        exit()


root = Tk()
root.configure(bg='white')
root.geometry("590x235")
root.configure(borderwidth=0, highlightthickness=15, highlightbackground="light grey")
GUI_Window = Attenuator_GUI(root)
root.mainloop()


#GPIB2::21::INSTR

