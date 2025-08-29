import pyvisa
import time
import os
import logging
import colorlog

import numpy as np
import matplotlib.pyplot as plt

# from dsg830 import init_command as dsg_init

# Create colored formatter
formatter = colorlog.ColoredFormatter(
    "%(asctime)s %(log_color)s %(message)s",
    datefmt='%H:%M:%S',  # Define the date/time format
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)

# Setup handler
handler = colorlog.StreamHandler()
handler.setFormatter(formatter)

# Setup logger
logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.WARNING)

def press_single_button(rsa):
    """
    Emulates pressing the front panel 'Single' button"""

    send_scpi_command(rsa, ":INITiate:CONTinuous OFF")
    send_scpi_command(rsa, ":TRIGger:SEQuence:SOURce IMMediate")
    send_scpi_command(rsa, ":INITiate:IMMediate")
        
        

def get_visa_resource(visa_string):
    """
    Check connect to remote instrument
    """
    if 'TCPIP' or 'USB' in visa_string:
        com_interface = visa_string.split('::')[0]
    else:
        logger.error("Invalid VISA string format")
        return

    try:
        # Create a resource manager
        rm = pyvisa.ResourceManager()
        
        try:
            logger.info(f"Trying to connect to: {com_interface}")
            
            inst = rm.open_resource(visa_string)
            logger.info(f'{inst}')
            inst.timeout = 10000  # 10-second timeout
            inst.read_termination = '\n'  # Common termination characters
            inst.write_termination = '\n'
            
            time.sleep(0.1)
            
            idn = inst.query('*IDN?').strip()
            logger.info(f"Instrument identified as: {idn}")
            
            return inst
            
        except pyvisa.errors.VisaIOError as e:
            logger.error(f"Error communicating with {com_interface}: {e}")
            logger.info("Trying alternative termination characters...")
            
            # Try different termination characters
            for read_term, write_term in [('\r\n', '\r\n'), ('\r', '\r'), ('\n', '\n')]: # \r\n - Windows standard, \r - old \n - modern instruments
                try:
                    if 'inst' in locals():
                        inst.close()
                    
                    inst = rm.open_resource(visa_string)
                    inst.timeout = 10000
                    inst.read_termination = read_term
                    inst.write_termination = write_term
                    
                    time.sleep(0.1)
                    idn = inst.query('*IDN?').strip()
                    logger.info(f"Success with termination {repr(read_term)}/{repr(write_term)}: {idn}")
                    return inst
                    
                except pyvisa.errors.VisaIOError:
                    continue
            
            logger.warning(f"All termination character combinations failed for {com_interface}")
            
        except Exception as e:
            logger.error(f"Unexpected error with {com_interface}: {e}")
    
    except Exception as e:
        logger.error(f"Failed to initialize resource manager: {e}")
    
        logger.warning("Could not identify any instruments.")
        return

def get_visa_string_ip(ip):
    """
    Create VISA string for LAN connection
    """
    return f'TCPIP0::{ip}::INSTR'

def send_scpi_command(inst, command):
    """
    send SCPI command to the instrument
    """
    try:
        # Add a small delay before querying
        time.sleep(0.01)
        
        # Query the instrument identification
        if command.strip().endswith("?"):
            response = inst.query(command).strip()
            command_type = 'QUERY'
        else:
            response = f"bytes: {inst.write(command)}"
            command_type = 'WRITE'
        logger.info(f"{inst} sending {command_type} command >> {command} --> {response}")
        
        return response
    
    except pyvisa.errors.VisaIOError as e:
        logger.error(f"Error communicating with instrument: {e}")
        return None

if __name__ == "__main__":
    os.system('cls')

    ip_DSG830 = '192.168.127.78' # static IP for DSG830
    ip_RSA5065N = '192.168.127.64' # static IP for RSA5065N

    visa_string_usb_DSG830 = 'USB0::0x1AB1::0x099C::DSG8E263200078::INSTR'
    visa_string_usb_RSA5065N = 'USB0::0x1AB1::0x0968::RSA5F251600073::INSTR'


    dsg = get_visa_resource(get_visa_string_ip(ip_DSG830)) # Digital signal generator DSG830
    rsa = get_visa_resource(get_visa_string_ip(ip_RSA5065N)) #Real-time Spectrum Analyzer RSA5065N

    freq_start = 2100e6
    freq_end = 2900e6

    frequencies = np.linspace(freq_start, freq_end, 9, dtype=int)

    meas_freq = []
    meas_level = []


    send_scpi_command(rsa, ":TRACe:CLEar:ALL")

    
    for frequency in frequencies:
        send_scpi_command(dsg, f":FREQ {frequency}")
        time.sleep(0.5)

        # send_scpi_command(dsg, ":LEV -15dBm")
        # send_scpi_command(dsg, ":OUTP ON")

        # time.sleep(1)
        send_scpi_command(rsa, f":SENSE:FREQUENCY:CENTER {frequency}")
        send_scpi_command(rsa, f":SENSE:FREQUENCY:SPAN {1e5}")
        send_scpi_command(rsa,f":SENSE:BANDWIDTH:RESOLUTION {1e3}")
        send_scpi_command(rsa,f":SENSE:BANDWIDTH:VIDEO {1e3}")


        press_single_button(rsa)
        delay = float(send_scpi_command(rsa, ":SENSe:SWEep:TIME?")) + 0.5
        time.sleep(delay)

        send_scpi_command(rsa, ":CALCulate:MARKer1:MAXimum:MAX")
        time.sleep(0.1)

        send_scpi_command(rsa, f":SENSE:FREQUENCY:CENTER {send_scpi_command(rsa, ":CALCulate:MARKer1:X?")}")
        send_scpi_command(rsa, f":SENSE:FREQUENCY:SPAN {1e4}")
        send_scpi_command(rsa,f":SENSE:BANDWIDTH:RESOLUTION {100}")
        send_scpi_command(rsa,f":SENSE:BANDWIDTH:VIDEO {100}")

        press_single_button(rsa)
        delay = float(send_scpi_command(rsa, ":SENSe:SWEep:TIME?")) + 0.5
    
        time.sleep(delay)
        
        send_scpi_command(rsa, ":CALCulate:MARKer1:MAXimum:MAX")
        time.sleep(0.1)

        meas_freq.append(float(send_scpi_command(rsa, ":CALCulate:MARKer1:X?")))
        meas_level.append(float(send_scpi_command(rsa, ":CALCulate:MARKer1:Y?")))




    # Create the plot with professional styling
    plt.style.use('seaborn-v0_8')  # Modern and clean style

    # Create figure and axis with custom size
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot your data with styling
    ax.plot(meas_freq, meas_level, 
            linewidth=2.5, 
            color='#2E86AB',  # Nice blue color
            marker='o', 
            markersize=4, 
            markerfacecolor='#F24236',  # Red markers
            markeredgewidth=1,
            markeredgecolor='white',
            alpha=0.8)

    # Customize labels and title
    ax.set_xlabel('Frequency (MHz)', fontsize=14, fontweight='bold', labelpad=15)
    ax.set_ylabel('Level (dBm)', fontsize=14, fontweight='bold', labelpad=15)
    ax.set_title('Frequency Response Analysis', fontsize=16, fontweight='bold', pad=20)

    # Customize grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

    # Customize ticks
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:.0f}".format(x/1e6)))  # Clean frequency formatting in MHz

    # Add some padding around the data
    ax.margins(x=0.05, y=0.1)

    # Customize spines (borders)
    for spine in ax.spines.values():
        spine.set_linewidth(1.5)
        spine.set_color('gray')

    # Add a legend if you have multiple datasets
    # ax.legend(['Measurement Data'], loc='best', fontsize=12)

    # Improve layout
    plt.tight_layout()

    # Show the plot
    plt.show()

    
