r"""
Created by Alexander Yazdani, April 2023
This script was created to act as a GUI application for HP/Agilent Power Meters
to make into an application, run:
pyinstaller --onefile --noconsole \...filepath...\PowerMeterGUI.py
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
        self.powermeter = PowerMeter()
        self.init_window()

    def init_window(self):
        """
        Window:
        """
        self.master.title(f"Power Meter - Not Connected")
        self.pack(fill=BOTH, expand=1)
        name = Label(self, text="Alex Yazdani, ODVT, Cisco Systems, 2023", fg="dark gray")
        name.place(x=3, y=205, anchor="sw")
        self.init_screen()
        """
        Labels:
        """
        GPIB_label = Label(self, text = "GPIB Address:")
        GPIB_label.place(x = 10, y = 5)

        slot_label = Label(self, text = "Slot:")
        slot_label.place(x = 10, y = 50)

        name_label = Label(self, text = "Nickname:")
        name_label.place(x = 10, y = 95)

        unit1_label = Label(self, text = "Units:")
        unit1_label.place(x = 390, y = 17)

        unit2_label = Label(self, text = "Units:")
        unit2_label.place(x = 390, y = 79)

        """
        Entry Fields:
        """
        self.GPIB_entry = Entry(self)
        self.GPIB_entry.place(x = 10, y = 25)

        self.slot_entry = Entry(self)
        self.slot_entry.place(x = 10, y = 70)

        self.name_entry = Entry(self)
        self.name_entry.place(x = 10, y = 115)

        self.wave1_entry = Entry(self)
        self.wave1_entry.place(x = 390, y = 50)

        self.wave2_entry = Entry(self)
        self.wave2_entry.place(x = 390, y = 112)

        """
        Buttons:
        """
        connect = Button(self, text = "Connect", command=self.connect_device)
        connect_x = 10 + self.name_entry.winfo_reqwidth() / 2 - connect.winfo_reqwidth() / 2
        connect.place(x=connect_x, y=153)

        wave1_button = Button(self, text = "Set", command=lambda: self.set_wave1(self.slot_number, self.wave1_entry.get()))
        wave1_button.place(x = 520, y = 48)   

        wave2_button = Button(self, text = "Set", command=lambda: self.set_wave2(self.slot_number, self.wave2_entry.get()))
        wave2_button.place(x = 520, y = 110)  

        disconnect = Button(self, text = "Disconnect", command=self.disconnect_device)
        disconnect.place(x=420, y=153)

        unitW1 = Button(self, text=" W ", command = lambda: self.set_units(self.slot_number, 1, 1) )
        unitW1.place(x = 430, y = 17)

        unitdBm1 = Button(self, text = "dBm", command = lambda: self.set_units(self.slot_number, 1, 0) )
        unitdBm1.place(x = 470, y = 17)

        unitW2 = Button(self, text=" W ", command = lambda: self.set_units(self.slot_number, 2, 1) )
        unitW2.place(x = 430, y = 79)

        unitdBm2 = Button(self, text = "dBm", command = lambda: self.set_units(self.slot_number, 2, 0) )
        unitdBm2.place(x = 470, y = 79)

    def init_screen(self):

        self.output_screen1 = Frame(self, bg="#579500", width=200, height=65, bd=2, relief=SOLID)
        self.output_screen1.place(x=160, y=10)
        self.output_screen2 = Frame(self, bg="#579500", width=200, height=65, bd=2, relief=SOLID)
        self.output_screen2.place(x=160, y=72)

        channel1_label = Label(self, text="1", bg='#579500', fg="black", font=("Helvetica", 8))
        channel1_label.place(x=162, y=12)
        channel2_label = Label(self, text="2", bg='#579500', fg="black", font=("Helvetica", 8))
        channel2_label.place(x=162, y=74)

        P1_label = Label(self, text="P:", bg='#579500', fg="black", font=("Helvetica", 16, "bold"))
        P1_label.place(x=185, y=12)
        W1_label = Label(self, text=" \u03BB:", bg='#579500', fg="black", font=("Helvetica", 16, "bold"))
        W1_label.place(x=180, y=42)

        P2_label = Label(self, text="P:", bg='#579500', fg="black", font=("Helvetica", 16, "bold"))
        P2_label.place(x=185, y=74)
        W2_label = Label(self, text=" \u03BB:", bg='#579500', fg="black", font=("Helvetica", 16, "bold"))
        W2_label.place(x=180, y=104)

        self.P1_val = Label(self.output_screen1, text="--.--- dBm ", bg='#579500', fg="black", font=("Helvetica", 16, "bold"))
        self.P1_val.place(relx=1, y=1, anchor = "ne")
        self.W1_val = Label(self.output_screen1, text="----.--- nm ", bg='#579500', fg="black", font=("Helvetica", 16, "bold"))
        self.W1_val.place(relx=1, y=31, anchor = "ne")

        self.P2_val = Label(self.output_screen2, text="--.--- dBm ", bg='#579500', fg="black", font=("Helvetica", 16, "bold"))
        self.P2_val.place(relx=1, y=1, anchor = "ne")
        self.W2_val = Label(self.output_screen2, text="----.--- nm ", bg='#579500', fg="black", font=("Helvetica", 16, "bold"))
        self.W2_val.place(relx=1, y=31, anchor = "ne")

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
                    self.powermeter.gpib_address = gpib_address
                    self.powermeter.nickname = self.name_entry.get()
                    self.powermeter.connect(self.powermeter.gpib_address)
                except:
                    messagebox.showerror("Error", "Could not connect to instrument.  If issue persists, reset controller and scan for instruments.")
                    self.disconnect_device()
                self.master.title(f"Power Meter - {gpib_address} - Slot {self.slot_number}      {self.name_entry.get()}")
                self.refresh = Button(self, text = "Refresh Values", command=lambda: self.refresh_output(self.slot_number))
                self.refresh.place(x=215, y = 153)
                try:
                    self.get_powermeter_values(self.slot_number)
                    self.update_output_values()
                except:
                    messagebox.showerror("Error", "Connection lost, failed, or never established.  If issue persists, reset controller and scan for instruments.")
                    self.disconnect_device()
            else:
                messagebox.showerror("Error", "Invalid slot entry.")
        else:
            messagebox.showerror("Error", "Invalid GPIB address.  Please use format: GPIB0::00::INSTR")        

    def get_powermeter_values(self, slot):
        try:
            self.wavelength1 = float(self.powermeter.get_wavelength(slot, 1))*1000000000
            if self.wavelength1 > 2000:
                self.wavelength1 = "----.---"
            else:
                self.wavelength1 = round(Decimal(self.wavelength1), 3)
        except:
            self.wavelength1 = "----.---"
            self.powermeter.instrument.clear()

        try:
            self.power1 = float(self.powermeter.get_power(slot, 1))
            if self.power1 > 120:
                self.power1 = "--.---"
            else:
                self.power1 = round(Decimal(self.power1), 3)
        except:
            self.power1 = "--.---"
            self.powermeter.instrument.clear()

        try:
            self.wavelength2 = float(self.powermeter.get_wavelength(slot, 2))*1000000000
            if self.wavelength2 > 2000:
                self.wavelength2 = "----.---"
            else:
                self.wavelength2 = round(Decimal(self.wavelength2), 3) 
        except:
            self.wavelength2 = "----.---"
            self.powermeter.instrument.clear()
        
        try:
            self.power2 = float(self.powermeter.get_power(slot, 2))
            if self.power2 > 120:
                self.power2 = "--.---"
            else:
                self.power2 = round(Decimal(self.power2), 3)
        except:
            self.power2 = "--.---"
            self.powermeter.instrument.clear()
        self.update_output_values()


    def update_output_values(self):
        self.P1_val.config(text=f"{self.power1} {self.powermeter.get_unit(self.slot_number, 1)} ")
        self.W1_val.config(text=f"{self.wavelength1} nm ")
        self.P2_val.config(text=f"{self.power2} {self.powermeter.get_unit(self.slot_number, 2)} ")
        self.W2_val.config(text=f"{self.wavelength2} nm ")

    def refresh_output(self, slot):
        self.get_powermeter_values(slot)
        self.update_output_values()

    def set_wave1(self, slot, value, channel=1):
        self.powermeter.set_wavelength(slot, value, channel)
        self.refresh_output(slot)

    def set_wave2(self, slot, value, channel=2):
        self.powermeter.set_wavelength(slot, value, channel)
        self.refresh_output(slot)
    
    def set_units(self, slot, channel, unit):
        self.powermeter.set_unit(slot, channel, unit)
        self.refresh_output(self.slot_number)

    def reset_device(self):
        self.powermeter.reset()
        self.refresh_output(self.slot_number)

    def disconnect_device(self):
        self.powermeter.close()
        self.master.title(f"Power Meter - Not Connected")
        self.P1_val.config(text=f"--.--- dBm ")
        self.W1_val.config(text=f"----.--- nm ")
        self.P2_val.config(text=f"--.--- dBm ")
        self.W2_val.config(text=f"----.--- nm ")
        self.refresh.destroy()

    def exit_application(self):
        exit()


root = Tk()
root.configure(bg='white')
root.geometry("590x235")
root.configure(borderwidth=0, highlightthickness=15, highlightbackground="light grey")
GUI_Window = Attenuator_GUI(root)
root.mainloop()



