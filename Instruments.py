"""
Created by Alexander Yazdani, Spring/Summer 2023.
To install pyvisa library, run 'pip install pyvisa' in command prompt or terminal
This source file acts as a class definition for general lab instruments.
Additionally, child classes are defined for each instrument for their specific operations.

GPIB Format:        GPIB__::__::INSTR
TCP/IP Format:      TCPIP0::___.___.___.___::5025::SOCKET

Current Support List:

    - Attenuator:                   EXFO/HP/Agilent/Keysight
    - Power Meter:                  HP/Agilent/Keysight
    - Tunable Laser Source:         HP/Agilent/Keysight
    - Reference Transmitter:        HP/Agilent/Keysight
    - OSNR Generator:               YY Labs / OZ Optics (New model only)
    - OSA:                          Yokogawa (Uses old commands for AQ6317B)
    - Oscilloscope:                 HP/Agilent/Keysight
    - Optical Switch:               Polatis
    - Frequency Counter:            HP/Agilent/Keysight (53220A & 53132A)
    - BERT:                         Keysight M8000 BERT, M9505 Chassis

"""

from PIL import Image   # pip install pillow
import pyvisa
import time
import math
import matplotlib.pyplot as plt
import os
import io

LIGHTWAVE_MULTIMETER_IDNS = ["8163A", "8163B"]
LIGHTWAVE_MEASURMENT_SYSTEM_IDNS = ["8164A", "8164B"]
LIGHTWAVE_MULTICHANNEL_SYSTEM_IDNS = ["8166A", "8166B"]
ATTENUATOR_IDNS = ["81560A", "81578A", "81576A", "81566A"]
POWER_SENSOR_IDNS = ["81630A", "81630B", "81632A", "81632B",
                     "81635A", "81635B", "81536A", "81536B"]
TUNABLE_LASER_SOURCE_IDNS = ["81600B", "81606A", "81607A",
                             "81608A", "81609A", "81602A",
                             "N7776C", "N7778C", "N7779C",
                             "N7711A", "N7714A"]
REFERENCE_TRANSMITTER_IDNS = ["81490A", "81490B"]


class Instrument:

    class ConnectionError(Exception):
        pass

    class UnknownInstrumentError(Exception):
        pass

    def __init__(self, address=None, nickname="Instrument"):
        self.address = address
        self.nickname = nickname
        self.instrument = None
        try:
            self.connect()
        except:
            print("Failed to Connect.")
            raise Instrument.ConnectionError

    def connect(self):
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(self.address)
        self.clear()

    def refresh_connection(self):
        if not self.instrument.query("*IDN?"):
            self.instrument.close()
            self.instrument = self.rm.open_resource(self.address)

    def get_IDN(self):
        self.clear()
        try:
            self.IDN = self.instrument.query("*IDN?")
            return self.IDN
        except:
            raise Instrument.UnknownInstrumentError

    def get_slot_IDNs(self):
        self.refresh_connection()
        self.clear()
        self.slot_IDNs = self.instrument.query("*OPT?")
        return self.slot_IDNs

    def close(self):
        self.instrument.close()
        self.instrument = None
        self.rm.close()
        self.rm = None

    def clear(self):
        self.instrument.clear()
        time.sleep(0.5)

    def reset(self):
        self.instrument.write("*RST")


class Attenuator(Instrument):
    """
    Compatible with EXFO and HP/Agilent/Keysight
    EXFO requires chassis number
    If attenuator is HP/Agilent/Keysight, chassis number is still needed for method input but will not be used.
    """

    def __init__(self, address=None, nickname="Attenuator"):
        super().__init__(address, nickname)
        if (self.get_IDN().replace(" ", "")[:4].upper() == "EXFO"):
            if self.get_IDN().split()[1].split("-")[1] == "3150":
                self.type = "EXFO_module"
            else:
                self.type = "EXFO_chassis"
        else:
            self.type = "HP"

    def get_attenuation(self, chassis, slot):
        if self.type == "EXFO_chassis":
            command = f"LINS00{chassis}{slot}:INP:RATT?"
        elif self.type == "EXFO_module":
            command = "INP:ATT?"
        else:
            command = f"INP{slot}:ATT?"
        try:
            response = self.instrument.query(command)
        except:
            self.refresh_connection()
            response = self.instrument.query(command)
        if self.type == "EXFO_module":
            response = str('{:.6E}'.format(float(response)*(-1)))
        return response.replace("\n", "").replace("\r", "")

    def set_attenuation(self, chassis, slot, value):
        if self.type == "EXFO_chassis":
            command = f"LINS00{chassis}{slot}:INP:RATT {value}"
        elif self.type == "EXFO_module":
            command = f"INP:ATT {-1*value}"
        else:
            command = f"INP{slot}:ATT {value}"
        self.instrument.write(command)

    def get_offset(self, chassis, slot):
        if self.type == "EXFO_chassis":
            command = f"LINS00{chassis}{slot}:INP:OFFS?"
        elif self.type == "EXFO_module":
            command = "INP:OFFS?"
        else:
            command = f"INP{slot}:OFFS?"
        try:
            response = self.instrument.query(command)
        except:
            self.refresh_connection()
            response = self.instrument.query(command)
        if self.type == "EXFO_module":
            response = str('{:.6E}'.format(float(response)))
        return response.replace("\n", "").replace("\r", "")

    def set_offset(self, chassis, slot, value):
        if self.type == "EXFO_chassis":
            command = f"LINS00{chassis}{slot}:INP:OFFs {value} DB"
        elif self.type == "EXFO_module":
            command = f"INP:OFFS {value}"
        else:
            command = f"INP{slot}:OFFS {value}"
        self.instrument.write(command)

    def get_wavelength(self, chassis, slot):
        if self.type == "EXFO_chassis":
            command = f"LINS00{chassis}{slot}:INP:WAV?"
        elif self.type == "EXFO_module":
            command = "INP:WAVE?"
        else:
            command = f":INP{slot}:WAV?"
        try:
            response = self.instrument.query(command)
        except:
            self.refresh_connection()
            response = self.instrument.query(command)
        if self.type == "EXFO_module":
            response = str('{:.6E}'.format(float(response)*(1E-9)))
        try:
            if float(response) > 2e-06:
                response = self.instrument.query(command)
            if float(response) > 2e-06:
                response = self.instrument.query(command)
        except:
            response = self.instrument.query(command)
        return response.replace("\n", "").replace("\r", "")

    def set_wavelength(self, chassis, slot, value):
        if self.type == "EXFO_chassis":
            command = f"LINS00{chassis}{slot}:INP:WAV {value} NM"
        elif self.type == "EXFO_module":
            command = f"INP:WAVE {value}"
        else:
            command = f":INP{slot}:WAV {value}nm"
        self.refresh_connection()
        self.instrument.write(command)

    def get_pset(self, chassis, slot):
        if self.type == "EXFO_chassis":
            command = f"LINS00{chassis}{slot}:INP:ATT?"
        elif self.type == "EXFO_module":
            command = f"INP:ATT?"
        else:
            command = f"OUTP{slot}:POW?"
        try:
            response = self.instrument.query(command)
        except:
            self.clear()
            response = self.instrument.query(command)
        if self.type == "EXFO_chassis":
            response = str('{:.6E}'.format(float(response)*-1))
        elif self.type == "EXFO_module":
            response = str('{:.6E}'.format(-1*((float(response)*-1) - float(self.get_offset(chassis, slot)))))
        return response.replace("\n", "").replace("\r", "")

    def set_pset(self, chassis, slot, value):
        if self.type == "EXFO_chassis":
            command = f"LINS00{chassis}{slot}:INP:ATT {-1*value}"
        elif self.type == "EXFO_module":
            offset = float(self.get_offset(chassis, slot))
            atten = (-1*value) + offset
            command = f"INP:ATT {-1*atten}"
        else:
            command = f"OUTP{slot}:POW {value}"
        self.refresh_connection()
        self.instrument.write(command)

    """
    Below will only work for Agilent/HP/Keysignt:
    """

    def enable(self, slot, channel=1):
        command = f"OUTP{slot}:CHAN{channel}:STAT 1"
        self.instrument.write(command)

    def disable(self, slot, channel=1):
        command = f"OUTP{slot}:CHAN{channel}:STAT 0"
        self.instrument.write(command)

    def get_state(self, slot, channel=1):
        """
        result of 1 indicates enabled, 0 indicates disabled
        """
        command = f"OUTP{slot}:CHAN{channel}:STAT?"
        response = self.instrument.query(command)
        return response


class PowerMeter(Instrument):

    def __init__(self, address=None, nickname="Power Meter"):
        super().__init__(address, nickname)

    def set_unit(self, input_num, channel=1, unit=0):
        self.refresh_connection()
        command = f":SENS{input_num}:CHAN{channel}:POW:UNIT {unit}"
        self.instrument.write(command)

    def get_unit(self, input_num, channel=1):
        try:
            self.refresh_connection()
            command = f":SENS{input_num}:CHAN{channel}:POW:UNIT?"
            result = self.instrument.query(command)
            if int(result) == 1:
                return "W"
            elif int(result) == 0:
                return "dBm"
            else:
                return "---"
        except:
            return "---"

    def set_wavelength(self, input_num, value, channel=1):
        self.refresh_connection()
        command = f"SENSE{input_num}:CHAN{channel}:POWER:WAVELENGTH {value}nm"
        self.instrument.write(command)

    def get_wavelength(self, input_num, channel=1):
        try:
            self.refresh_connection()
            command = f"SENSE{input_num}:CHAN{channel}:POWER:WAVELENGTH?"
            response = self.instrument.query(command)
            return response
        except:
            self.instrument.clear()
            self.refresh_connection()
            command = f"SENSE{input_num}:CHAN{channel}:POWER:WAVELENGTH?"
            response = self.instrument.query(command)
            return response

    def get_power(self, input_num, channel=1):
        try:
            self.refresh_connection()
            command = f":FETC{input_num}:CHAN{channel}:POW?"
            response = self.instrument.query(command)
            return response
        except:
            self.instrument.clear()
            self.refresh_connection()
            command = f":FETC{input_num}:CHAN{channel}:POW?"
            response = self.instrument.query(command)
            return response

    def enable(self, slot, channel=1):
        command = f"OUTP{slot}:CHAN{channel}:STAT 1"
        self.instrument.write(command)

    def disable(self, slot, channel=1):
        command = f"OUTP{slot}:CHAN{channel}:STAT 0"
        self.instrument.write(command)

    def get_state(self, slot, channel=1):
        """
        result of 1 indicates enabled, 0 indicates disabled
        """
        command = f"OUTP{slot}:CHAN{channel}:STAT?"
        response = self.instrument.query(command)
        return response


class Tunable_Laser(Instrument):

    def __init__(self, address=None, nickname="Tunable Laser"):
        super().__init__(address, nickname)

    def set_wavelength(self, slot, wavelength, channel=1):
        command = f":SOUR{slot}:CHAN{channel}:WAV {wavelength}nm"
        self.instrument.write(command)

    def get_wavelength(self, slot, channel=1):
        command = f":SOUR{slot}:CHAN{channel}:WAV?"
        response = self.instrument.query(command)
        return response

    def get_power(self, slot, channel=1):
        command = f":SOUR{slot}:CHAN{channel}:POW?"
        response = self.instrument.query(command)
        return response

    def get_state(self, slot, channel=1):
        command = f":OUTP{slot}:CHAN{channel}:STAT?"
        response = self.instrument.query(command)
        if int(response) == 1:
            return "ON"
        elif int(response) == 0:
            return "OFF"
        else:
            return "ERROR"

    def enable(self, slot, channel=1):
        command = f"OUTP{slot}:CHAN{channel}:STAT 1"
        self.instrument.write(command)

    def disable(self, slot, channel=1):
        command = f"OUTP{slot}:CHAN{channel}:STAT 0"
        self.instrument.write(command)

    def get_state(self, slot, channel=1):
        """
        result of 1 indicates enabled, 0 indicates disabled
        """
        command = f"OUTP{slot}:CHAN{channel}:STAT?"
        response = self.instrument.query(command)
        return response


class Reference_Transmitter(Instrument):

    def __init__(self, address=None, nickname="Reference Transmitter"):
        super().__init__(address, nickname)

    def get_wavelength(self, slot, channel=1):
        command = f":SOUR{slot}:CHAN{channel}:WAV?"
        response = self.instrument.query(command)
        return response

    def tx_recal(self, slot):
        command = f"SOUR{slot}:TRAN:REC"
        self.instrument.write(command)

    def get_state(self, slot, channel=1):
        command = f":OUTP{slot}:CHAN{channel}:STAT?"
        response = self.instrument.query(command)
        if int(response) == 1:
            return "ON"
        elif int(response) == 0:
            return "OFF"
        else:
            return "ERROR"

    def enable(self, slot, channel=1):
        command = f"OUTP{slot}:CHAN{channel}:STAT 1"
        self.instrument.write(command)

    def disable(self, slot, channel=1):
        command = f"OUTP{slot}:CHAN{channel}:STAT 0"
        self.instrument.write(command)

    def get_state(self, slot, channel=1):
        """
        result of 1 indicates enabled, 0 indicates disabled
        """
        command = f"OUTP{slot}:CHAN{channel}:STAT?"
        response = self.instrument.query(command)
        return response


class OSNR(Instrument):

    def __init__(self, address=None, nickname="OSNR"):
        super().__init__(address, nickname)

    def enable_ASE(self):
        command = "ASE1"
        self.instrument.write(command)

    def disable_ASE(self):
        command = "ASE0"
        self.instrument.write(command)

    def enable_EDFA(self):
        command = "EDFA1"
        self.instrument.write(command)

    def disable_EDFA(self):
        command = "EDFA0"
        self.instrument.write(command)

    def enable(self):
        self.enable_ASE()
        self.enable_EDFA()

    def disable(self):
        self.disable_ASE()
        self.disable_EDFA()

    def set_itu_channel(self, itu_channel):
        command = f"CH{itu_channel}"
        self.instrument.write(command)

    def get_itu_channel(self):
        command = "CH?"
        response = self.instrument.query(command)
        return response

    def set_osnr(self, osnr):
        command = f"RL{osnr}DB"
        self.instrument.write(command)

    def get_osnr(self):                 # DO NOT USE
        """
        Unstable command, need to report ot OZ Optics / YY Labs
        """
        command = "R?DB"
        response = self.instrument.query(command).split()[4][0:5]
        return response

    def increment_osnr_coarse(self):    # DO NOT USE
        current_osnr = self.get_osnr()
        new_osnr = current_osnr + 1
        self.set_osnr(new_osnr)

    def decrement_osnr_coarse(self):    # DO NOT USE
        current_osnr = self.get_osnr()
        new_osnr = current_osnr - 1
        self.set_osnr(new_osnr)

    def increment_osnr_fine(self):      # DO NOT USE
        current_osnr = self.get_osnr()
        new_osnr = current_osnr + 0.2
        self.set_osnr(new_osnr)

    def decrement_osnr_fine(self):      # DO NOT USE
        current_osnr = self.get_osnr()
        new_osnr = current_osnr - 0.2
        self.set_osnr(new_osnr)

    def set_input_power_ref(self, pi):
        command = f"RP{pi}"
        self.instrument.write(command)

    def get_input_power_ref(self):
        command = "RP?"
        response = self.instrument.query(command)
        return response

    def set_output_power(self, po):
        command = f"PL{po}DBM"
        self.instrument.write(command)

    def get_output_power(self):
        command = "PO?"
        response = self.instrument.query(command)
        return response

    def lock_input_power(self):
        command = "LPI"
        self.instrument.write(command)


class OSA(Instrument):

    def __init__(self, address=None, nickname="OSA"):
        super().__init__(address, nickname)

    # Check if it's in AQ6317 Compatible Mode
    def command_mode(self):
        command2 = ":SYSTem:COMMunicate:CFORmat AQ6317"
        self.instrument.write(command2)
        command1 = "CFORM?"
        response1 = self.instrument.query(command1)

        # 0 for AQ6317 mode, 1 for AQ6370 mode
        if str(response1).rstrip() != "0":
            self.instrument.write(command2)

    # Read setup file stored internal
    def read_set(self, filename):
        # Change to AQ6370 Mode for loading internal setting files
        command1 = "CFORM1"
        self.instrument.write(command1)

        # file name format: Sxxxx.ST6
        command2 = f"MMEMORY:LOAD:SETTING \"{filename}\",INTERNAL"
        self.instrument.write(command2)

    # Save setup file internal
    def save_set(self, filename):
        # Change to AQ6370 Mode for saving internal setting files
        command1 = "CFORM1"
        self.instrument.write(command1)

        # file name format: Sxxxx, no need to add .ST6
        command2 = f":MMEMORY:STORE:SETTING \"{filename}\",INTERNAL"
        self.instrument.write(command2)

    # Delete setup file internal
    def delete_set(self, filename):
        # Change to AQ6370 Mode for deleting internal setting files
        command1 = "CFORM1"
        self.instrument.write(command1)

        # file name format: Sxxxx.ST6
        command2 = f":MMEMORY:DELETE \"{filename}\",INTERNAL"
        self.instrument.write(command2)

    def auto_sweep(self):
        command = "AUTO"
        self.instrument.write(command)

    def repeat_sweep(self):
        command = "RPT"
        self.instrument.write(command)

    def single_sweep(self):
        command = "SGL"
        self.instrument.write(command)

    def stop_sweep(self):
        command = "STP"
        self.instrument.write(command)

    def set_center(self, wl):
        command = f"CTRWL{wl}"
        self.instrument.write(command)

    def set_start(self, wl):
        command = f"STAWL{wl}"
        self.instrument.write(command)

    def set_stop(self, wl):
        command = f"STPWL{wl}"
        self.instrument.write(command)

    def set_span(self, wl):
        command = f"SPAN{wl}"
        self.instrument.write(command)

    def set_resolution(self, rsln):
        command = f"RESLN{rsln}"
        self.instrument.write(command)

    def set_noise_bw(self, nbw):
        command = f"WDMNOIBW{nbw}"
        self.instrument.write(command)

    def get_center(self):
        command = "CTRWL?"
        response = self.instrument.query(command)
        return response

    def get_start(self):
        command = "STAWL?"
        response = self.instrument.query(command)
        return response

    def get_stop(self):
        command = "STPWL?"
        response = self.instrument.query(command)
        return response

    def get_span(self):
        command = "SPAN?"
        response = self.instrument.query(command)
        return response

    def get_resolution(self):
        command = "RESLN?"
        response = self.instrument.query(command)
        return response

    def get_noise_bw(self):
        command = "WDMNOIBW?"
        response = self.instrument.query(command)
        return response

    def set_smsr_mode(self):
        command = f"SMSR1"
        self.instrument.write(command)

    def set_wdm_mode(self):
        command = f"WDMAN"
        self.instrument.write(command)

    def get_osnr_values(self):
        self.set_wdm_mode()
        command = "ANA?"
        response = self.instrument.query(command).replace(
            " ", "").replace("\r", "").replace("\n", "").split(",")
        return response

    def get_osnr(self):
        response = self.get_osnr_values()[3]
        return response

    def get_smsr_values(self):
        """
        Method returns a list, mapping shown below, can be easily modified to output dict.
        peak_wavelength = response[0]
        peak_level = response[1]
        side_mode_wa velength = response[2]
        side_mode_level = response[3]
        wavelength_difference = response[4]
        level_difference = response[5]
        """
        self.set_smsr_mode()
        command = "ANA?"
        response = self.instrument.query(command).replace(" ", "").split(",")
        response = [float(val) for val in response]
        response_dict = {"peak_wavelength": response[0],
                         "peak_level": response[1],
                         "side_mode_wavelength": response[2],
                         "side_mode_level": response[3],
                         "wavelength_difference": response[4],
                         "level_difference": response[5]}
        return response

    def fetch_screen(self):
        amplitude = self.instrument.query(
            "LDATA").replace(" ", "").split(",")[1:]
        wavelength = self.instrument.query(
            "WDATA").replace(" ", "").split(",")[1:]
        amplitude = [float(val) for val in amplitude]
        wavelength = [float(val) for val in wavelength]
        plt.plot(wavelength, amplitude)
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Amplitude (dBm)')
        plt.title('Amplitude vs. Wavelength')
        num_ticks = 5
        step = len(wavelength) // (num_ticks - 1)
        x_ticks = wavelength[::step]
        x_tick_labels = [f'{value:.1f}' for value in x_ticks]
        plt.xticks(x_ticks, x_tick_labels)
        plt.gca().xaxis.set_major_formatter('{:.3f}'.format)
        if min(amplitude) < -100:
            plt.ylim(-100, (max(amplitude) + 10))
        else:
            plt.ylim((min(amplitude) - 10), (max(amplitude) + 10))
        plt.grid(True)
        save_dir = 'OSA_plots'
        os.makedirs(save_dir, exist_ok=True)
        # Specify the desired file name and format
        save_path = os.path.join(save_dir, f'OSA_plot_{time.time()}.png')
        plt.savefig(save_path, dpi=300)
        plt.close()

    def fetch_dwdm_screen(self):
        """
        Assumes OSA is already in WDM Mode
        """
        amplitude = self.instrument.query(
            "LDATA").replace(" ", "").split(",")[1:]
        wavelength = self.instrument.query(
            "WDATA").replace(" ", "").split(",")[1:]
        amplitude = [float(val) for val in amplitude]
        wavelength = [float(val) for val in wavelength]
        fig, (ax1, ax2) = plt.subplots(
            2, 1, gridspec_kw={'height_ratios': [3, 1]})
        ax1.plot(wavelength, amplitude)
        ax1.set_xlabel('Wavelength (nm)')
        ax1.set_ylabel('Amplitude (dBm)')
        ax1.set_title('Amplitude vs. Wavelength')
        num_ticks = 5
        step = len(wavelength) // (num_ticks - 1)
        x_ticks = wavelength[::step]
        x_tick_labels = [f'{value:.1f}' for value in x_ticks]
        ax1.set_xticks(x_ticks)
        ax1.set_xticklabels(x_tick_labels)
        ax1.xaxis.set_major_formatter('{:.3f}'.format)
        if min(amplitude) < -100:
            ax1.set_ylim(-100, max(amplitude) + 10)
        else:
            ax1.set_ylim(min(amplitude) - 10, max(amplitude) + 10)
        ax1.grid(True)
        wdm_analysis = self.get_osnr_values()[1:4]
        ax2.axis('off')
        table_data = [wdm_analysis]
        table_cols = ['Peak Wavelength [nm]', 'Peak Level [dBm]', 'SNR [dB]']
        ax2.table(cellText=table_data, colLabels=table_cols, loc='center')
        plt.tight_layout()
        # plt.show()
        save_dir = 'OSA_plots/DWDM_plots'
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f'OSA_plot_{time.time()}.png')
        plt.savefig(save_path, dpi=300)
        plt.close()

    def fetch_smsr_screen(self):
        """
        Assumes OSA is already in SMSR Mode
        """
        amplitude = self.instrument.query(
            "LDATA").replace(" ", "").split(",")[1:]
        wavelength = self.instrument.query(
            "WDATA").replace(" ", "").split(",")[1:]
        amplitude = [float(val) for val in amplitude]
        wavelength = [float(val) for val in wavelength]
        fig, (ax1, ax2) = plt.subplots(
            2, 1, gridspec_kw={'height_ratios': [3, 1]})
        ax1.plot(wavelength, amplitude)
        ax1.set_xlabel('Wavelength (nm)')
        ax1.set_ylabel('Amplitude (dBm)')
        ax1.set_title('Amplitude vs. Wavelength')
        num_ticks = 5
        step = len(wavelength) // (num_ticks - 1)
        x_ticks = wavelength[::step]
        x_tick_labels = [f'{value:.1f}' for value in x_ticks]
        ax1.set_xticks(x_ticks)
        ax1.set_xticklabels(x_tick_labels)
        ax1.xaxis.set_major_formatter('{:.3f}'.format)
        if min(amplitude) < -100:
            ax1.set_ylim(-100, max(amplitude) + 10)
        else:
            ax1.set_ylim(min(amplitude) - 10, max(amplitude) + 10)
        ax1.grid(True)
        smsr_analysis = self.get_smsr_values()
        ax2.axis('off')
        table_data = [smsr_analysis]
        table_cols = ['Peak Wavelength [nm]', 'Peak Level [dBm]', '2nd Peak Wavelength [nm]',
                      '2nd Peak Level [dBm]', 'Wavelength Difference (nm)', 'Level Difference (SMSR) [dB]']
        table = ax2.table(cellText=table_data,
                          colLabels=table_cols, loc='center')
        for i in range(0, len(table_data[0])):
            table[0, i].set_fontsize(4)
        for i in range(0, len(table_data[0])):
            table[1, i].set_fontsize(8)
        table.auto_set_font_size(False)
        plt.tight_layout()
        # plt.show()
        save_dir = 'OSA_plots\SMSR_plots'
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f'OSA_plot_{time.time()}.png')
        plt.savefig(save_path, dpi=300)
        plt.close()


class Oscilloscope(Instrument):
    def __init__(self, address=None, nickname="Oscilloscope"):
        super().__init__(address, nickname)

    def fetch_screen(self):
        filename = rf'oscilloscop_capture_{time.time()}.png'
        filepath = rf'D:\User Files\python_instruments_images\{filename}'
        self.instrument.write(":DISK:SIMage:INVert 1")
        self.instrument.write(fr':DISK:SIMage:FNAMe "{filepath}"')
        self.instrument.write(":DISPlay:TOVerlap 0")
        self.instrument.write(":DISK:SIMage:SAVE")
        time.sleep(5)
        image_data = self.instrument.query_binary_values(
            f':DISK:BFILe? "{filepath}"', datatype='B', container=bytes)
        image = Image.open(io.BytesIO(image_data))
        save_dir = 'Oscilloscope_Plots'
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)
        image.save(save_path)

    def autoscale(self):
        command = ":SYSTem:AUToscale"
        self.instrument.write(command)
        time.sleep(5)

    def run(self):
        command = ":ACQuire:RUN"
        self.instrument.write(command)

    def stop(self):
        command = ":ACQuire:STOP"
        self.instrument.write(command)

    def oscilloscope_mode(self):
        command = ":SYSTem:MODE OSCilloscope"
        self.instrument.write(command)
        time.sleep(3)

    def jitter_mode(self):
        command = ":SYSTem:MODE JITTer"
        self.instrument.write(command)
        time.sleep(3)

    def tdr_mode(self):
        command = ":SYSTem:MODE TDR"
        self.instrument.write(command)
        time.sleep(3)

    def eye_mode(self):
        command = ":SYSTem:MODE EYE"
        self.instrument.write(command)
        time.sleep(3)

    def enable_pattern_lock(self):
        command = ":TRIGger:PLOCk ON"
        self.instrument.write(command)
        time.sleep(5)

    def disable_pattern_lock(self):
        command = ":TRIGger:PLOCk OFF"
        self.instrument.write(command)

    def enable_filter(self, channel):
        command = f":CHAN{channel}A:FILTer ON"
        self.instrument.write(command)

    def disable_filter(self, channel):
        command = f":CHAN{channel}A:FILTer OFF"
        self.instrument.write(command)

    def set_filter_speed(self, channel, speed):
        """
        Speeds include:
        1.2500000E+9
        1.0312500E+10
        2.5781250E+10
        2.6562500E+10
        5.3125000E+10
        """
        command = f":CHAN{channel}A:FSELect:RATe {speed}"
        self.instrument.write(command)

    def enable_input(self, channel):
        command = f":CHAN{channel}A:DISlay ON"
        self.instrument.write(command)

    def disable_input(self, channel):
        command = f":CHAN{channel}A:DISlay OFF"
        self.instrument.write(command)

    def CDR_relock(self, channel):
        command = f":CRECovery{channel}:RELock"
        self.instrument.write(command)

    def CDR_lock(self, channel, speed):
        """
        Speeds include:
        1.2500000E+9
        1.0312500E+10
        2.5781250E+10
        2.6562500E+10
        5.3125000E+10
        """
        command = f":CRECovery{channel}CRATe {speed}"
        self.instrument.write(command)
        self.CDR_relock()

    def measure_jitter(self):
        self.instrument.write(":MEASure:JITTer:DEFine:UNITs UINTerval")
        tj = self.instrument.query(":MEASure:JITTer:TJ?")
        ddj = self.instrument.query(":MEASure:JITTer:DDJ?")
        return tj, ddj

    def display_rise_fall_times(self):
        self.instrument.write(":MEASure:OSCilloscope:FALLtime")
        self.instrument.write(":MEASure:OSCilloscope:RISetime")

    def measure_rise_fall_times(self):
        fall_time = self.instrument.query(
            ":MEASure:OSCilloscope:FALLtime:Mean?")
        rise_time = self.instrument.query(
            ":MEASure:OSCilloscope:RISetime:Mean?")
        return rise_time, fall_time

    def check_acquisition(self):
        command = ":MEASure:LTESt:ACQuire:COUNt?"
        count = self.instrument.query(command)
        return count

    def wait_for_acquisition(self):
        count1 = -1
        count2 = -2
        while count1 != count2:
            count1 = self.check_acquisition()
            time.sleep(5)
            count2 = self.check_acquisition()
            time.sleep(5)

    def get_margin(self):
        command = "MEAS:MTES:MARG?"
        response = self.instrument.query(command)
        return response

    def get_extinction_ratio(self):
        command = ":MEASure:CGRade:ERATio?"
        response = self.instrument.query(command)
        return response

    def get_crossing_point(self):
        command = ":MEASure:CGRade:CROSsing?"
        response = self.instrument.query(command)
        return response

    def get_tdec(self):
        command = ":MEASure:CGRade:TDEc?"
        response = self.instrument.query(command)
        return response

    def get_tdecq(self):
        command = ":MEASure:EYE:TDEQ?"
        response = self.instrument.query(command)
        return response

    def get_oer(self):
        command = ":MEASure:EYE:OER?"
        response = self.instrument.query(command)
        return response

    def enable_function(self, channel):
        command = f":FUNC{channel}:DISPlay ON"
        self.instrument.write(command)

    def disable_function(self, channel):
        command = f":FUNC{channel}:DISPlay OFF"
        self.instrument.write(command)

    def get_CDR_ratio(self, CDR_channel=5):
        command = f":CRECovery{CDR_channel}:ODRatio?"
        response = self.instrument.query(command)
        return response


class Polatis_Switch(Instrument):

    def __init__(self, address=None, nickname="Polatis Switch"):
        super().__init__(address, nickname)

    def interconnect(self, input, output):
        command = f":oxc:swit:conn:add (@{input}),(@{output})"
        self.instrument.write(command)

    def interdisconnect(self, input, output):
        command = f":oxc:swit:conn:sub (@{input}),(@{output})"
        self.instrument.write(command)

    def disconnect_all(self):
        command = ":oxc:swit:disc:all"
        self.instrument.write(command)

    def check_connect(self, input):
        command = f":oxc:swit:conn:port? {input}"
        response = self.instrument.query(command)
        return response


class Frequency_Counter(Instrument):
    """
    Remember to use Oscilloscope.get_CDR_ratio() if creating algorithm for clock accuracy
    """

    def __init__(self, address=None, nickname="Polatis Switch"):
        super().__init__(address, nickname)
        self.idn = self.get_IDN().split(",")[1]

    def get_frequency(self, input=3):
        if self.idn == "53220A" or self.idn == "53230A":
            command = f"MEAS:FREQ? DEF,DEF,(@{input})"
        elif self.idn == "53132A":
            command = "READ:FREQ?"
        else:
            print("IDN not recognized.")
            raise Instrument.UnknownInstrumentError
        try:
            response = self.instrument.query(command)
        except:
            response = self.instrument.query(command)
        return response


class BERT(Instrument):

    def __init__(self, address="TCPIP0::172.20.240.110::5025::SOCKET", nickname="BERT"):
        super().__init__(address, nickname)

    def recall_instrument_state(self, filename):
        command = f"MMEMory:WORKspace:SETTings:USER:RECall '{filename}'"
        self.instrument.write(command)
        time.sleep(5)

    def set_prbs_31(self):
        command1 = rf""":DATA:SEQuence:SET:VALue 'Generator',#3376<?xml version="1.0" encoding="utf-16"?><sequenceDefinition xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.agilent.com/schemas/M8000/DataSequence">  <description />  <sequence>    <loop>      <block length="256">        <prbs polynomial="2^31-1" />      </block>    </loop>  </sequence></sequenceDefinition>"""
        command2 = rf""":DATA:SEQuence:SET:VALue 'Analyzer',#3371<?xml version="1.0" encoding="utf-16"?><sequenceDefinition xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.agilent.com/schemas/M8000/DataSequence">  <description />  <sequence>    <syncAndLoopBlock length="128">      <prbs polynomial="2^31-1" />    </syncAndLoopBlock>  </sequence></sequenceDefinition>"""
        command3 = f":DATA:SEQuence:BIND 'Generator','M2.DataOut'"
        command4 = f":DATA:SEQuence:BIND 'Analyzer','M1.DataIn1','M1.DataIn2'"
        self.instrument.write(command1)
        self.instrument.write(command2)
        self.instrument.write(command3)
        self.instrument.write(command4)

    def enable_global_outputs(self):
        command = f":OUTPut:GLOBal:STATe 'M1.System',1"
        self.instrument.write(command)

    def disable_global_outputs(self):
        command = f":OUTPut:GLOBal:STATe 'M1.System',0"
        self.instrument.write(command)

    def enable_impariments(self):
        command = f":SOURce:JITTer:GLOBal:STATe 'M1.System',1"
        self.instrument.write(command)

    def disable_impariments(self):
        command = f":SOURce:JITTer:GLOBal:STATe 'M1.System',0"
        self.instrument.write(command)

    def enable_SSC(self):
        command = f":SOURce:SSCLocking:GLOBal:STATe 'M1.System',1"
        self.instrument.write(command)

    def disable_SSC(self):
        command = f":SOURce:SSCLocking:GLOBal:STATe 'M1.System',0"
        self.instrument.write(command)

    def insert_error(self):
        command = f"OUTPut:EINSertion:ONCE 'M2.DataOut'"
        self.instrument.write(command)


def main():
    # att1 = Attenuator("GPIB0::2::INSTR")
    # print(att1.get_pset(2, 0))
    # att1.set_pset(2, 0, -9)
    # print(att1.get_pset(2, 0))
    # att1.close()

    scope = Oscilloscope("GPIB0::7::INSTR")
    print(scope.get_margin())
    scope.clear()
    scope.close()


if __name__ == "__main__":
    main()

