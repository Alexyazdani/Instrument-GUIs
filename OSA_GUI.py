"""
Created by Alexander Yazdani for Cisco Systems, ODVT, Summer 2023.
GPIB Format:        GPIB__::__::INSTR
TCP/IP Format:      TCPIP0::___.___.___.___::5025::SOCKET
pyinstaller --onefile --noconsole \...filepath...\OSA_GUI.py
"""

import pyvisa
import time
import sys
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Optical Spectrum Analyzer")
        self.resize(970, 470)
        self.gpib_label = QLabel("Address:")
        self.gpib_field = QLineEdit()
        self.connect_button = QPushButton("Connect")
        self.disconnect_button = QPushButton("Disconnect")

        self.osa_instrument = None

        self.analysis_labels = None
        self.analysis_data = None

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        self.refresh_button = None

        self.layout = QGridLayout()
        self.layout.addWidget(self.gpib_label, 0, 0)
        self.layout.addWidget(self.gpib_field, 0, 1)
        self.layout.addWidget(self.connect_button, 0, 2)
        self.layout.addWidget(self.disconnect_button, 0, 3)

        main_widget = QWidget()
        main_widget.setLayout(self.layout)
        self.setCentralWidget(main_widget)

        self.connect_button.clicked.connect(self.connect_instrument)
        self.disconnect_button.clicked.connect(self.disconnect_instrument)

    def setup_buttons(self):
        if self.refresh_button is None:

            self.frame1 = QFrame()
            self.frame1.setFrameShape(QFrame.Box)
            self.frame1.setLineWidth(2)
            self.button_layout1 = QVBoxLayout(self.frame1)
            self.layout.addWidget(self.frame1, 1, 3)

            self.frame2 = QFrame()
            self.frame2.setFrameShape(QFrame.Box)
            self.frame2.setLineWidth(2)
            self.button_layout2 = QGridLayout(self.frame2)
            self.button_layout2.setAlignment(Qt.AlignTop) 
            self.layout.addWidget(self.frame2, 1, 4)

            self.canvas = FigureCanvas(self.figure)
            self.layout.addWidget(self.canvas, 1, 0, 1, 3)

            self.refresh_button = QPushButton("Refresh Screen")
            self.refresh_button.clicked.connect(self.fetch_screen)

            self.autoscale_button = QPushButton("Auto")
            self.autoscale_button.clicked.connect(self.auto_sweep)

            self.repeat_button = QPushButton("Repeat")
            self.repeat_button.clicked.connect(self.repeat_sweep)

            self.single_button = QPushButton("Single")
            self.single_button.clicked.connect(self.single_sweep)

            self.stop_button = QPushButton("Stop")
            self.stop_button.clicked.connect(self.stop_sweep)

            self.button_layout1.addWidget(self.autoscale_button)
            self.button_layout1.addWidget(self.repeat_button)
            self.button_layout1.addWidget(self.single_button)
            self.button_layout1.addWidget(self.stop_button)
            self.button_layout1.addWidget(self.refresh_button)

            self.center_wl_label = QLabel("Center WL (nm):")
            self.center_wl_entry = QLineEdit()
            self.center_wl_button = QPushButton("Set")
            self.center_wl_button.clicked.connect(self.set_center)

            self.start_wl_label = QLabel("Start WL (nm):")
            self.start_wl_entry = QLineEdit()
            self.start_wl_button = QPushButton("Set")
            self.start_wl_button.clicked.connect(self.set_start)

            self.stop_wl_label = QLabel("Stop WL (nm):")
            self.stop_wl_entry = QLineEdit()
            self.stop_wl_button = QPushButton("Set")
            self.stop_wl_button.clicked.connect(self.set_stop)

            self.span_label = QLabel("Span (nm):")
            self.span_entry = QLineEdit()
            self.span_button = QPushButton("Set")
            self.span_button.clicked.connect(self.set_span)

            self.resolution_label = QLabel("Resolution (nm):")
            self.resolution_entry = QLineEdit()
            self.resolution_button = QPushButton("Set")
            self.resolution_button.clicked.connect(self.set_resolution)

            self.noisebw_label = QLabel("Noise BW (nm):")
            self.noisebw_entry = QLineEdit()
            self.noisebw_button = QPushButton("Set")
            self.noisebw_button.clicked.connect(self.set_noisebw)

            self.labels = QVBoxLayout()
            self.labels.addWidget(self.center_wl_label)
            self.labels.addWidget(self.start_wl_label)
            self.labels.addWidget(self.stop_wl_label)
            self.labels.addWidget(self.span_label)
            self.labels.addWidget(self.resolution_label)
            self.labels.addWidget(self.noisebw_label)

            self.entries = QVBoxLayout()
            self.entries.addWidget(self.center_wl_entry)
            self.entries.addWidget(self.start_wl_entry)
            self.entries.addWidget(self.stop_wl_entry)
            self.entries.addWidget(self.span_entry)
            self.entries.addWidget(self.resolution_entry)
            self.entries.addWidget(self.noisebw_entry)

            self.setbuttons = QVBoxLayout()
            self.setbuttons.addWidget(self.center_wl_button)
            self.setbuttons.addWidget(self.start_wl_button)
            self.setbuttons.addWidget(self.stop_wl_button)
            self.setbuttons.addWidget(self.span_button)
            self.setbuttons.addWidget(self.resolution_button)
            self.setbuttons.addWidget(self.noisebw_button)

            self.button_layout2.addLayout(self.labels, 0, 0)
            self.button_layout2.addLayout(self.entries, 0, 1)
            self.button_layout2.addLayout(self.setbuttons, 0, 2)

            self.analysis_label = QLabel("Analysis:")
            self.wdm_button = QPushButton("WDM")
            self.wdm_button.clicked.connect(self.dwdm_analysis)
            self.smsr_button = QPushButton("SMSR")
            self.smsr_button.clicked.connect(self.smsr_analysis)
            self.button_layout2.addWidget(QLabel(" "), 1, 0)
            self.button_layout2.addWidget(self.analysis_label, 2, 0)
            self.button_layout2.addWidget(self.wdm_button, 2, 1)
            self.button_layout2.addWidget(self.smsr_button, 2, 2)


    def set_center(self):
        try:
            self.osa_instrument.set_center(self.center_wl_entry.text())
            self.single_sweep()
        except:
            error_message = "Error communicating with instrument."
            QMessageBox.critical(self, "Error", error_message)

    def set_start(self):
        try:
            self.osa_instrument.set_start(self.start_wl_entry.text())
            self.single_sweep()
        except:
            error_message = "Error communicating with instrument."
            QMessageBox.critical(self, "Error", error_message)

    def set_stop(self):
        try:
            self.osa_instrument.set_stop(self.stop_wl_entry.text())
            self.single_sweep()
        except:
            error_message = "Error communicating with instrument."
            QMessageBox.critical(self, "Error", error_message)

    def set_span(self):
        try:
            self.osa_instrument.set_span(self.span_entry.text())
            self.single_sweep()
        except:
            error_message = "Error communicating with instrument."
            QMessageBox.critical(self, "Error", error_message)

    def set_resolution(self):
        try:
            self.osa_instrument.set_resolution(self.resolution_entry.text())
            self.single_sweep()
        except:
            error_message = "Error communicating with instrument."
            QMessageBox.critical(self, "Error", error_message)

    def set_noisebw(self):
        try:
            self.osa_instrument.set_noise_bw(self.noisebw_entry.text())
            self.single_sweep()
        except:
            error_message = "Error communicating with instrument."
            QMessageBox.critical(self, "Error", error_message)

    def auto_sweep(self):
        try:
            self.osa_instrument.auto_sweep()
            time.sleep(6)
            self.fetch_screen()
        except:
            error_message = "Error communicating with instrument."
            QMessageBox.critical(self, "Error", error_message)

    def repeat_sweep(self):
        try:
            self.osa_instrument.repeat_sweep()
        except:
            error_message = "Error communicating with instrument."
            QMessageBox.critical(self, "Error", error_message)

    def single_sweep(self):
        try:
            self.osa_instrument.single_sweep()
            time.sleep(3)
            self.fetch_screen()
        except:
            error_message = "Error communicating with instrument."
            QMessageBox.critical(self, "Error", error_message)

    def stop_sweep(self):
        try:
            self.osa_instrument.stop_sweep()
            self.fetch_screen()
        except:
            error_message = "Error communicating with instrument."
            QMessageBox.critical(self, "Error", error_message)

    def dwdm_analysis(self):
        self.osa_instrument.set_wdm_mode()
        self.osa_instrument.clear()
        try:
            wdm_data = self.osa_instrument.get_osnr_values()
        except:
            wdm_data = ['--', '--', '--', '--']

        try:
            self.button_layout2.removeItem(self.analysis_labels)
            while self.analysis_labels.count():
                item = self.analysis_labels.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        except:
            pass

        try:
            self.button_layout2.removeItem(self.analysis_data)
            while self.analysis_data.count():
                item = self.analysis_data.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        except:
            pass

        self.analysis_labels = QVBoxLayout()
        self.analysis_labels.addWidget(QLabel("Peak WL (nm):"))
        self.analysis_labels.addWidget(QLabel("Peak Level (dBm):"))
        self.analysis_labels.addWidget(QLabel("SNR (dB):"))
        self.button_layout2.addLayout(self.analysis_labels, 3, 0)

        self.analysis_data = QVBoxLayout()
        self.analysis_data.addWidget(QLabel(wdm_data[1]))
        self.analysis_data.addWidget(QLabel(wdm_data[2]))
        self.analysis_data.addWidget(QLabel(wdm_data[3]))
        self.button_layout2.addLayout(self.analysis_data, 3, 1)


    def smsr_analysis(self):
        self.osa_instrument.set_smsr_mode()
        self.osa_instrument.clear()
        try:
            smsr_data = self.osa_instrument.get_smsr_values()
        except:
            smsr_data = ['--', '--', '--', '--', '--', '--']

        try:
            self.button_layout2.removeItem(self.analysis_labels)
            while self.analysis_labels.count():
                item = self.analysis_labels.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        except:
            pass

        try:
            self.button_layout2.removeItem(self.analysis_data)
            while self.analysis_data.count():
                item = self.analysis_data.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        except:
            pass

        self.analysis_labels = QVBoxLayout()
        self.analysis_labels.addWidget(QLabel("Peak WL (nm):"))
        self.analysis_labels.addWidget(QLabel("Peak Level (dBm):"))
        self.analysis_labels.addWidget(QLabel("Side Mode WL (nm):"))
        self.analysis_labels.addWidget(QLabel("Side Mode Level (dBm):"))
        self.analysis_labels.addWidget(QLabel("WL Difference (dB):"))
        self.analysis_labels.addWidget(QLabel("Level Difference (dB):"))
        self.button_layout2.addLayout(self.analysis_labels, 3, 0)

        self.analysis_data = QVBoxLayout()
        self.analysis_data.addWidget(QLabel(smsr_data[0]))
        self.analysis_data.addWidget(QLabel(smsr_data[1]))
        self.analysis_data.addWidget(QLabel(smsr_data[2]))
        self.analysis_data.addWidget(QLabel(smsr_data[3]))
        self.analysis_data.addWidget(QLabel(smsr_data[4]))
        self.analysis_data.addWidget(QLabel(smsr_data[5]))
        self.button_layout2.addLayout(self.analysis_data, 3, 1)




    def remove_buttons(self):

        self.button_layout1.removeWidget(self.refresh_button)
        self.button_layout1.removeWidget(self.autoscale_button)
        self.button_layout1.removeWidget(self.repeat_button)
        self.button_layout1.removeWidget(self.single_button)
        self.button_layout1.removeWidget(self.stop_button)

        self.layout.removeWidget(self.canvas)

        self.refresh_button.deleteLater()
        self.autoscale_button.deleteLater()
        self.repeat_button.deleteLater()
        self.single_button.deleteLater()
        self.stop_button.deleteLater()

        self.canvas.deleteLater()


        self.layout.removeWidget(self.frame1)
        self.layout.removeWidget(self.frame2)
        self.frame1.deleteLater()
        self.frame2.deleteLater()

        self.refresh_button = None
        self.canvas = FigureCanvas(self.figure)



    def connect_instrument(self):
        try:
            self.disconnect_instrument()
            gpib_address = self.gpib_field.text()
            self.osa_instrument = OSA(gpib_address)
            self.osa_instrument.command_mode()
            self.setup_buttons()
            self.fetch_screen()
        except:
            error_message = "Could not connect to instrument."
            QMessageBox.critical(self, "Error", error_message)

    def disconnect_instrument(self):
        if self.osa_instrument:
            self.osa_instrument.close()
            self.osa_instrument = None
            self.figure.clear()
            self.canvas.draw()
            self.remove_buttons()

    def fetch_screen(self):
        try:
            if self.osa_instrument:
                self.figure.clear()
                amplitude = self.osa_instrument.instrument.query("LDATA").replace(" ", "").split(",")[1:]
                wavelength = self.osa_instrument.instrument.query("WDATA").replace(" ", "").split(",")[1:]
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
                self.canvas.draw()
        except:
            error_message = "Error fetching screen from OSA."
            QMessageBox.critical(self, "Error", error_message)


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

    def get_smsr_values(self):
        self.set_smsr_mode()
        command = "ANA?"
        response = self.instrument.query(command).replace(" ", "").replace("\n", "").split(",")
        response = [str(val) for val in response]
        return response

    # def fetch_screen(self):
    #     amplitude = self.instrument.query(
    #         "LDATA").replace(" ", "").split(",")[1:]
    #     wavelength = self.instrument.query(
    #         "WDATA").replace(" ", "").split(",")[1:]
    #     amplitude = [float(val) for val in amplitude]
    #     wavelength = [float(val) for val in wavelength]
    #     plt.plot(wavelength, amplitude)
    #     plt.xlabel('Wavelength (nm)')
    #     plt.ylabel('Amplitude (dBm)')
    #     plt.title('Amplitude vs. Wavelength')
    #     num_ticks = 5
    #     step = len(wavelength) // (num_ticks - 1)
    #     x_ticks = wavelength[::step]
    #     x_tick_labels = [f'{value:.1f}' for value in x_ticks]
    #     plt.xticks(x_ticks, x_tick_labels)
    #     plt.gca().xaxis.set_major_formatter('{:.3f}'.format)
    #     if min(amplitude) < -100:
    #         plt.ylim(-100, (max(amplitude) + 10))
    #     else:
    #         plt.ylim((min(amplitude) - 10), (max(amplitude) + 10))
    #     plt.grid(True)
    #     plt.show()

if __name__ == "__main__":
    main()
