r"""
Created by Alexander Yazdani, April 2023
To install pyvisa library, run 'pip install pyvisa' in command prompt or terminal
This source file acts as a class definition of an Instrument, and has specific methods for specific instruments.
Alternatively, Child classes are defined for each instrument as well.
"""
import pyvisa
from decimal import Decimal

LIGHTWAVE_MULTIMETER_IDNS = ["8163A", "8163B"]
LIGHTWAVE_MEASURMENT_SYSTEM_IDNS = ["8164A", "8164B"]
LIGHTWAVE_MULTICHANNEL_SYSTEM_IDNS = ["8166A", "8166B"]
ATTENUATOR_IDNS = ["81560A", "81578A", "81576A", "81566A"]
POWER_SENSOR_IDNS = ["81632A", "81632B", "81635A", "81635B", "81536A", "81536B"]
TUNABLE_LASER_SOURCE_IDNS = ["81600B", "81606A", "81607A", "81608A", "81609A", "81602A", "N7776C", "N7778C", "N7779C", "N7711A", "N7714A"]
REFERENCE_TRANSMITTER_IDNS = ["81490A", "81490B"]


class Instrument:
    def __init__(self, gpib_address="GPIB0::00::INSTR", nickname="Instrument"):
        self.gpib_address = gpib_address
        self.nickname = nickname
        self.instrument = None

    def connect(self, gpib):
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(gpib)

    def refresh_connection(self):
        if not self.instrument.query("*IDN?"):
            self.reset()
            self.instrument.close()
            self.instrument = self.rm.open_resource(self.gpib_address)

    def get_IDN(self):
        self.refresh_connection()
        self.instrument.clear()
        self.IDN = self.instrument.query("*IDN?")
        return self.IDN

    def get_slot_IDNs(self):
        self.refresh_connection()
        self.instrument.clear()
        self.slot_IDNs = self.instrument.query("*OPT?")
        return self.slot_IDNs

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

    def close(self):
        self.instrument.close()
        self.rm.close()

    def reset(self):
        self.instrument.clear()
        # self.instrument.write("*RST")
        # controller = pyvisa.ResourceManager().open_resource(self.gpib_address)
        # controller.write('*RST')
        # controller.close()
    """
    Methods for Attenuators
    """
    def attenuator_get_attenuation(self, input_num):
        try:
            self.refresh_connection()
            command = f"INP{input_num}:ATT?"
            response = self.instrument.query(command)
            return response
        except:
            self.instrument.clear()
            self.refresh_connection()
            command = f"INP{input_num}:ATT?"
            response = self.instrument.query(command)
            return response

    def attenuator_set_attenuation(self, input_num, value):
        self.refresh_connection()
        command = f"INP{input_num}:ATT {value}"
        self.instrument.write(command)

    def attenuator_get_offset(self, input_num):
        try:
            self.refresh_connection()
            command = f"INP{input_num}:OFFS?"
            response = self.instrument.query(command)
            return response
        except:
            self.instrument.clear()
            self.refresh_connection()
            command = f"INP{input_num}:OFFS?"
            response = self.instrument.query(command)
            return response

    def attenuator_set_offset(self, input_num, value):
        self.refresh_connection()
        command = f"INP{input_num}:OFFS {value}"
        self.instrument.write(command)

    def attenuator_get_power_out(self, input_num):
        try:
            self.refresh_connection()
            command = f"OUTP{input_num}:POW?"
            response = self.instrument.query(command)
            return response
        except:
            self.instrument.clear()
            self.refresh_connection()
            command = f"OUTP{input_num}:POW?"
            response = self.instrument.query(command)
            return response

    def attenuator_set_power_out(self, input_num, value):
        self.refresh_connection()
        command = f"OUTP{input_num}:POW {value}"
        self.instrument.write(command)

    def attenuator_get_wavelength(self, input_num):
        try:
            self.refresh_connection()
            command = f":INP{input_num}:WAV?"
            response = self.instrument.query(command)
        except:
            self.instrument.clear()
            self.refresh_connection()
            command = f":INP{input_num}:WAV?"
            response = self.instrument.query(command)
        try:
            if float(response) > 2e-06:
                response = self.instrument.query(command)
            if float(response) > 2e-06:
                response = self.instrument.query(command)
            return response
        except:
            response = self.instrument.query(command)
        return response

    def attenuator_set_wavelength(self, input_num, value):
        self.refresh_connection()
        command = f":INP{input_num}:WAV {value}nm"
        self.instrument.write(command)

    def attenuator_refresh_connection(self):
        if not self.instrument.query("*IDN?"):
            self.instrument.close()
            self.instrument = self.rm.open_resource(self.gpib_address)
  
    """
    Methods for Power Meters
    """
    def power_meter_set_unit(self, input_num, channel=1, unit=0):
        self.refresh_connection()
        command = f":SENS{input_num}:CHAN{channel}:POW:UNIT {unit}"
        self.instrument.write(command)

    def power_meter_get_unit(self, input_num, channel=1):
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

    def power_meter_set_wavelength(self, input_num, value, channel=1):
        self.refresh_connection()
        command = f"SENSE{input_num}:CHAN{channel}:POWER:WAVELENGTH {value}nm"
        self.instrument.write(command)

    def power_meter_get_wavelength(self, input_num, channel=1):
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

    def power_meter_get_power(self, input_num, channel=1):
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
    """
    Methods for Tunable Lasers
    """

    def tunable_laser_set_wavelength(self, slot, wavelength, channel=1):
        command = f":SOUR{slot}:CHAN{channel}:WAV {wavelength}nm"
        self.instrument.write(command)
    
    def tunable_laser_get_wavelength(self, slot, channel=1):
        command = f":SOUR{slot}:CHAN{channel}:WAV?"
        response = self.instrument.query(command)
        return response
    
    def tunable_laser_get_power(self, slot, channel=1):
        command = f":SOUR{slot}:CHAN{channel}:POW?"
        response = self.instrument.query(command)
        return response
    
    def tunable_laser_get_state(self, slot, channel=1):
        command = f":OUTP{slot}:CHAN{channel}:STAT?"
        response = self.instrument.query(command)
        if int(response) == 1:
            return "ON"
        elif int(response) == 0:
            return "OFF"
        else:
            return "ERROR"
        
    """
    Methods for Reference Transmitters
    """
    def reference_transmitter_get_wavelength(self, slot, channel=1):
        command = f":SOUR{slot}:CHAN{channel}:WAV?"
        response = self.instrument.query(command)
        return response

    def reference_transmitter_tx_recal(self, slot):
        command = f"SOUR{slot}:TRAN:REC"
        self.instrument.write(command)

    def reference_transmitter_get_state(self, slot, channel=1):
        command = f":OUTP{slot}:CHAN{channel}:STAT?"
        response = self.instrument.query(command)
        if int(response) == 1:
            return "ON"
        elif int(response) == 0:
            return "OFF"
        else:
            return "ERROR"


class Attenuator(Instrument):

    def __init__(self, gpib_address="GPIB0::00::INSTR", nickname="Attenuator"):
        super().__init__(gpib_address, nickname)

    def get_attenuation(self, input_num):
        try:
            self.refresh_connection()
            command = f"INP{input_num}:ATT?"
            response = self.instrument.query(command)
            return response
        except:
            self.instrument.clear()
            self.refresh_connection()
            command = f"INP{input_num}:ATT?"
            response = self.instrument.query(command)
            return response

    def set_attenuation(self, input_num, value):
        self.refresh_connection()
        command = f"INP{input_num}:ATT {value}"
        self.instrument.write(command)

    def get_offset(self, input_num):
        try:
            self.refresh_connection()
            command = f"INP{input_num}:OFFS?"
            response = self.instrument.query(command)
            return response
        except:
            self.instrument.clear()
            self.refresh_connection()
            command = f"INP{input_num}:OFFS?"
            response = self.instrument.query(command)
            return response

    def set_offset(self, input_num, value):
        self.refresh_connection()
        command = f"INP{input_num}:OFFS {value}"
        self.instrument.write(command)

    def get_power_out(self, input_num):
        try:
            self.refresh_connection()
            command = f"OUTP{input_num}:POW?"
            response = self.instrument.query(command)
            return response
        except:
            self.instrument.clear()
            self.refresh_connection()
            command = f"OUTP{input_num}:POW?"
            response = self.instrument.query(command)
            return response

    def set_power_out(self, input_num, value):
        self.refresh_connection()
        command = f"OUTP{input_num}:POW {value}"
        self.instrument.write(command)

    def get_wavelength(self, input_num):
        try:
            self.refresh_connection()
            command = f":INP{input_num}:WAV?"
            response = self.instrument.query(command)
        except:
            self.instrument.clear()
            self.refresh_connection()
            command = f":INP{input_num}:WAV?"
            response = self.instrument.query(command)
        try:
            if float(response) > 2e-06:
                response = self.instrument.query(command)
            if float(response) > 2e-06:
                response = self.instrument.query(command)
            return response
        except:
            response = self.instrument.query(command)
        return response

    def set_wavelength(self, input_num, value):
        self.refresh_connection()
        command = f":INP{input_num}:WAV {value}nm"
        self.instrument.write(command)

    def refresh_connection(self):
        if not self.instrument.query("*IDN?"):
            self.instrument.close()
            self.instrument = self.rm.open_resource(self.gpib_address)


class PowerMeter(Instrument):

    def __init__(self, gpib_address="GPIB0::00::INSTR", nickname="Power Meter"):
        super().__init__(gpib_address, nickname)

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


class Tunable_Laser(Instrument):

    def __init__(self, gpib_address="GPIB0::00::INSTR", nickname="Tunable Laser"):
        super().__init__(gpib_address, nickname)

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

class Reference_Transmitter(Instrument):
    def __init__(self, gpib_address="GPIB0::00::INSTR", nickname="Reference Transmitter"):
        super().__init__(gpib_address, nickname)
    
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


def main():
    # att = Attenuator("GPIB2::21::INSTR", "MM Rx Testing")
    # att.connect(att.gpib_address)

    # att.set_wavelength(2, 1310)
    # wavelength = att.get_wavelength(2)
    # print(f"{att.nickname} Attenuator Input 2 wavelength: {wavelength}")

    # att.set_wavelength(2, 850)
    # wavelength = att.get_wavelength(2)
    # print(f"{att.nickname} Attenuator Input 2 wavelength: {wavelength}")

    # att.close()

    # pow = PowerMeter("GPIB0::21::INSTR", "Right Rack")
    # pow.connect(pow.gpib_address)
    # print(type(pow.get_slot_IDNs()))

    # pow.set_wavelength(1, 1310, 1)
    # wavelength = pow.get_wavelength(1, 1)
    # print(f"{pow.nickname} Power Meter Input 1 wavelength: {wavelength}")
    # power = pow.get_power(1, 1)
    # print(f"{pow.nickname} Power Meter Input 1 power: {power}")

    # pow.set_wavelength(1, 1561.41, 1)
    # wavelength = pow.get_wavelength(1, 1)
    # print(f"{pow.nickname} Power Meter Input 1 wavelength: {wavelength}")
    # power = pow.get_power(1, 1)
    # print(f"{pow.nickname} Power Meter Input 1 power: {power}")

    # wavelength = pow.get_wavelength(2, 1)
    # print(f"{pow.nickname} Power Meter Input 2 wavelength: {wavelength}")
    # power = pow.get_power(2, 1)
    # print(f"{pow.nickname} Power Meter Input 2 power: {power}")
    # wavelength = round(float(pow.get_wavelength(1, 2)), 3)
    # if power > 90:
    #     power = "it works"
    # print(wavelength)
    # print(pow.get_IDN())
    # print(pow.get_unit(1, 1))
    # print(pow.get_unit(1, 2))

    # pow.set_unit(1, 1, 1)
    # pow.set_unit(1, 2, 1)

    # print(pow.get_unit(1, 1))
    # print(pow.get_unit(1, 2))

    # pow.close()

    tunable_laser = Tunable_Laser("GPIB0::21::INSTR")
    tunable_laser.connect(tunable_laser.gpib_address)
    print(tunable_laser.get_state(0, 1))
    # tunable_laser.set_wavelength(0, 1310, 1)
    # print(round(Decimal(tunable_laser.get_wavelength(0, 1))*1000000000, 4))
    tunable_laser.close()

    # reference_tx = Reference_Transmitter("GPIB0::21::INSTR")
    # reference_tx.connect(reference_tx.gpib_address)
    # print(round(Decimal(reference_tx.get_wavelength(1))*1000000000, 1))
    # print(round(Decimal(reference_tx.get_wavelength(3))*1000000000, 1))
    # reference_tx.close()

if __name__ == "__main__":
    main()
