import pyvisa
import time
import os

def get_usb_resource(logs = True):
    """
    Attempts to identify a USB-connected RIGOL DSG830 signal generator
    by querying its identification string.
    """
    try:
        # Create a resource manager
        rm = pyvisa.ResourceManager()
        if logs: print(f"Using backend: {rm}")
        
        # List all available resources
        resources = rm.list_resources()
        if logs: print("Available resources:", resources)
        
        # Filter for USB resources (looking for RIGOL DSG830 pattern)
        usb_resources = [res for res in resources if 'USB' in res]
        
        if not usb_resources:
            print("No USB instruments found with RIGOL USB pattern.")
            return None
        
        if logs: print(f"Found USB resources: {usb_resources}")
        
        for usb_address in usb_resources:
            try:
                if logs: print(f"Trying to connect to: {usb_address}")
                
                # Open the resource with appropriate settings
                inst = rm.open_resource(usb_address)
                inst.timeout = 10000  # 10-second timeout
                inst.read_termination = '\n'  # Common termination character
                inst.write_termination = '\n'
                
                # Add a small delay before querying
                time.sleep(0.1)
                
                # Query the instrument identification
                idn = inst.query('*IDN?').strip()
                
                if logs: print(f"Success! Instrument identified as: {idn}")
                
                
                return inst
                
            except pyvisa.errors.VisaIOError as e:
                print(f"Error communicating with {usb_address}: {e}")
                print("Trying alternative termination characters...")
                
                # Try different termination characters
                for read_term, write_term in [('\r\n', '\r\n'), ('\r', '\r'), ('\n', '\n')]:
                    try:
                        if 'inst' in locals():
                            inst.close()
                        
                        inst = rm.open_resource(usb_address)
                        inst.timeout = 10000
                        inst.read_termination = read_term
                        inst.write_termination = write_term
                        
                        time.sleep(0.1)
                        idn = inst.query('*IDN?').strip()
                        print(f"Success with termination {repr(read_term)}/{repr(write_term)}: {idn}")
                        return inst
                        
                    except pyvisa.errors.VisaIOError:
                        continue
                
                print(f"All termination character combinations failed for {usb_address}")
                
            except Exception as e:
                print(f"Unexpected error with {usb_address}: {e}")
    
    except Exception as e:
        print(f"Failed to initialize resource manager: {e}")
    
        print("Could not identify any USB instruments.")
        return None
    

    """
    Attempts to identify a USB-connected RIGOL DSG830 signal generator
    by querying its identification string.
    """
    try:
        # Create a resource manager
        rm = pyvisa.ResourceManager()
        if logs: print(f"Using backend: {rm}")
        
        # List all available resources
        resources = rm.list_resources()
        if logs: 
            print("Available resources:", resources)
        
        # Filter for USB resources (looking for RIGOL DSG830 pattern)
        usb_resources = [res for res in resources if 'USB' in res and ('DSG' in res or '0x1AB1' in res)]
        
        if not usb_resources:
            print("No USB instruments found with RIGOL DSG pattern.")
            return None
        
        if logs: print(f"Found USB resources: {usb_resources}")
        
        for usb_address in usb_resources:
            try:
                if logs: print(f"Trying to connect to: {usb_address}")
                
                # Open the resource with appropriate settings
                inst = rm.open_resource(usb_address)
                inst.timeout = 10000  # 10-second timeout
                inst.read_termination = '\n'  # Common termination character
                inst.write_termination = '\n'
                
                # Add a small delay before querying
                time.sleep(0.1)
                
                # Query the instrument identification
                idn = inst.query('*IDN?').strip()
                
                if logs: print(f"Success! Instrument identified as: {idn}")
                
                # Check if it's a DSG830
                if 'DSG830' in idn:
                   if logs: print("Confirmed: RIGOL DSG830 series signal generator")
                
                return inst
                
            except pyvisa.errors.VisaIOError as e:
                print(f"Error communicating with {usb_address}: {e}")
                print("Trying alternative termination characters...")
                
                # Try different termination characters
                for read_term, write_term in [('\r\n', '\r\n'), ('\r', '\r'), ('\n', '\n')]:
                    try:
                        if 'inst' in locals():
                            inst.close()
                        
                        inst = rm.open_resource(usb_address)
                        inst.timeout = 10000
                        inst.read_termination = read_term
                        inst.write_termination = write_term
                        
                        time.sleep(0.1)
                        idn = inst.query('*IDN?').strip()
                        print(f"Success with termination {repr(read_term)}/{repr(write_term)}: {idn}")
                        return inst
                        
                    except pyvisa.errors.VisaIOError:
                        continue
                
                print(f"All termination character combinations failed for {usb_address}")
                
            except Exception as e:
                print(f"Unexpected error with {usb_address}: {e}")
    
    except Exception as e:
        print(f"Failed to initialize resource manager: {e}")
    
        print("Could not identify any USB instruments.")
        return None
    
def get_lan_resource(logs = True , ip = False):
    """
    Check LAN-connect to remote instrument
    """
    if not ip:
        print("Check IP address")
        return False

    try:
        # Create a resource manager
        rm = pyvisa.ResourceManager()
        visa_string_lan = f'TCPIP0::{ip}::INSTR'
        
        try:
            if logs: print(f"Trying to connect to: {ip}")
            
            inst = rm.open_resource(visa_string_lan)
            print(f'{inst}')
            inst.timeout = 10000  # 10-second timeout
            inst.read_termination = '\n'  # Common termination characters
            inst.write_termination = '\n'
            
            # Add a small delay before querying
            time.sleep(0.1)
            
            # Query the instrument identification
            idn = inst.query('*IDN?').strip()
            
            if logs: print(f"Success! Instrument identified as: {idn}")
            
            return inst
            
        except pyvisa.errors.VisaIOError as e:
            print(f"Error communicating with {ip}: {e}")
            print("Trying alternative termination characters...")
            
            # Try different termination characters
            for read_term, write_term in [('\r\n', '\r\n'), ('\r', '\r'), ('\n', '\n')]:
                try:
                    if 'inst' in locals():
                        inst.close()
                    
                    inst = rm.open_resource(visa_string_lan)
                    inst.timeout = 10000
                    inst.read_termination = read_term
                    inst.write_termination = write_term
                    
                    time.sleep(0.1)
                    idn = inst.query('*IDN?').strip()
                    print(f"Success with termination {repr(read_term)}/{repr(write_term)}: {idn}")
                    return inst
                    
                except pyvisa.errors.VisaIOError:
                    continue
            
            print(f"All termination character combinations failed for {ip}")
            
        except Exception as e:
            print(f"Unexpected error with {ip}: {e}")
    
    except Exception as e:
        print(f"Failed to initialize resource manager: {e}")
    
        print("Could not identify any LAN instruments.")
        return None

def send_scpi_command(inst, command):
    """
    send SCPI command to the instrument
    """
    try:
        # Add a small delay before querying
        time.sleep(0.1)
        
        # Query the instrument identification
        if command.strip().endswith("?"):
            idn = inst.query(command).strip()
            command_type = 'QUERY'
        else:
            idn = f"ok : {inst.write(command)}"
            command_type = 'WRITE'
        print(f"Result of sending {command_type} command >> {command} --> {idn}")
        
        return idn
    
    except pyvisa.errors.VisaIOError as e:
        print(f"Error communicating with instrument: {e}")
        return None

if __name__ == "__main__":
    os.system('cls')

    device_ip_DSG830 = '192.168.127.78' # static IP for DSG830
    device_ip_RSA5065N = '192.168.127.64' # static IP for RSA5065N
    visa_string_usb = 'USB0::0x1AB1::0x099C::DSG8E263200078::INSTR' # VISA USB Connect String

    # inst = get_usb_resource()
    inst = get_lan_resource(ip = device_ip_RSA5065N)

    if inst:
        # send_scpi_command(inst, ":SYST:DISP:UPD?")
        # send_scpi_command(inst, ":SYSTem:COMMunicate:LAN:SELF:IP:ADDRess 192.168.127.64")
        send_scpi_command(inst, ":SYSTem:COMMunicate:LAN:SELF:IP:ADDRess?")
    else:
        print("\nInstrument identification failed.")
