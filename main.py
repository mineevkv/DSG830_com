import pyvisa
import time
import os

def check_dsg830_usb_idn(logging = True):
    """
    Attempts to identify a USB-connected RIGOL DSG830 signal generator
    by querying its identification string.
    """
    try:
        # Create a resource manager
        rm = pyvisa.ResourceManager()
        if logging: print(f"Using backend: {rm}")
        
        # List all available resources
        resources = rm.list_resources()
        if logging: 
            print("Available resources:", resources)
        
        # Filter for USB resources (looking for RIGOL DSG830 pattern)
        usb_resources = [res for res in resources if 'USB' in res and ('DSG' in res or '0x1AB1' in res)]
        
        if not usb_resources:
            print("No USB instruments found with RIGOL DSG pattern.")
            return None
        
        if logging: print(f"Found USB resources: {usb_resources}")
        
        for usb_address in usb_resources:
            try:
                if logging: print(f"Trying to connect to: {usb_address}")
                
                # Open the resource with appropriate settings
                inst = rm.open_resource(usb_address)
                inst.timeout = 10000  # 10-second timeout
                inst.read_termination = '\n'  # Common termination character
                inst.write_termination = '\n'
                
                # Add a small delay before querying
                time.sleep(0.1)
                
                # Query the instrument identification
                idn = inst.query('*IDN?').strip()
                
                if logging: print(f"Success! Instrument identified as: {idn}")
                
                # Check if it's a DSG830
                if 'DSG830' in idn:
                   if logging: print("Confirmed: RIGOL DSG830 series signal generator")
                
                inst.close()
                return idn
                
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
                        inst.close()
                        return idn
                        
                    except pyvisa.errors.VisaIOError:
                        continue
                
                print(f"All termination character combinations failed for {usb_address}")
                
            except Exception as e:
                print(f"Unexpected error with {usb_address}: {e}")
    
    except Exception as e:
        print(f"Failed to initialize resource manager: {e}")
    
        print("Could not identify any USB instruments.")
        return None

def send_scpi_command(command):
    """
    sends an SCPI command to the instrument
    """
    try:
        # Create a resource manager
        rm = pyvisa.ResourceManager()
        # print(f"Using backend: {rm}")
        
        # List all available resources
        resources = rm.list_resources()
        # print("Available resources:", resources)
        
        # Filter for USB resources (looking for RIGOL DSG830 pattern)
        usb_resources = [res for res in resources if 'USB' in res and ('DSG' in res or '0x1AB1' in res)]
        
        if not usb_resources:
            print("No USB instruments found with RIGOL DSG pattern.")
            return None
        
        # print(f"Found USB resources: {usb_resources}")
        
        for usb_address in usb_resources:
            try:
                # print(f"Trying to connect to: {usb_address}")
                
                # Open the resource with appropriate settings
                inst = rm.open_resource(usb_address)
                inst.timeout = 10000  # 10-second timeout
                inst.read_termination = '\n'  # Common termination character
                inst.write_termination = '\n'
                
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
                
                
                inst.close()
                return idn
            except pyvisa.errors.VisaIOError as e:
                print(f"Error1: {e}")
                inst.close()
                return None
            
    except Exception as e:
            print(f"Error2: {e}")
            inst.close()
            return None

if __name__ == "__main__":

    os.system('cls')

    identification = check_dsg830_usb_idn(False)


        
    if identification:
        send_scpi_command(":OUTP?")
        send_scpi_command(":OUTP OFF")
        send_scpi_command(":OUTP?")

    else:
        print("\nInstrument identification failed.")