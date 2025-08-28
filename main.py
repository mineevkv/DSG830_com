import pyvisa
import time
import os
import logging
import colorlog

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
logger.setLevel(logging.INFO)

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
        time.sleep(0.1)
        
        # Query the instrument identification
        if command.strip().endswith("?"):
            response = inst.query(command).strip()
            command_type = 'QUERY'
        else:
            response = f"bytes: {inst.write(command)}"
            command_type = 'WRITE'
        logger.info(f"Result of sending {command_type} command >> {command} --> {response}")
        
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

    visa_string_ip =  get_visa_string_ip(ip_DSG830)

    inst = get_visa_resource(visa_string_ip)

    if inst:
        pass
        # send_scpi_command(inst, ":SYST:DISP:UPD?")
        # send_scpi_command(inst, ":SYSTem:COMMunicate:LAN:SELF:IP:ADDRess 192.168.127.64")
        # send_scpi_command(inst, ":SYSTem:COMMunicate:LAN:SELF:IP:ADDRess?")

        # send_scpi_command(inst, ":SYSTem:COMMunication:LAN:IP:MANual?")
        # send_scpi_command(inst, ":SYST:COMM:LAN:IP:ADD?")
        # send_scpi_command(inst, ":SYST:COMM:LAN:IP:ADD 192.168.127.78")
        # send_scpi_command(inst, ":SYST:COMM:LAN:IP:ADD?")
        # send_scpi_command(inst, ":SYST:COMM:LAN:IP:SUB:MASK?")
        # send_scpi_command(inst, ":SYST:COMM:LAN:IP:SUB:MASK 255.255.255.0")
        # send_scpi_command(inst, ":SYST:COMM:LAN:IP:SUB:MASK?")
        # send_scpi_command(inst, ":SYSTem:COMMunication:LAN:IP:SET")

        send_scpi_command(inst, "*IDN?")

        
    else:
        logger.error("Instrument identification failed")