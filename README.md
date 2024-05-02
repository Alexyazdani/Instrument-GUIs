Alexander Yazdani

GUI executables and source files for various laboratory instruments.

The file Instuments.py acts as a class definition of an Instrument, and has specific methods for specific instruments.  Alternatively, child classes are defined for each instrument as well.

Current support list:

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

The file InstrumentGUI.py uses Instruments.py to create a GUI for multimeters.  When connected to an instrument, the chassis will be scanned to identify the connected modules and create the proper interfaces for each.

The files AttenuatorGUI.py, OSA_GUI.py, and PowerMeterGUI.py are standalone files that act as individual GUIs for their respective instruments.  
