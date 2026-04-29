import pyvisa
from unittest.mock import MagicMock
import time

def send_scpi_commands_with_error_check(ip_address, port, commands, delay=0.5):
    # 1. Luodaan Mock-laite simulointia varten
    device = MagicMock()
    
    # Määritellään Mock-laitteen vastauslogiikka
    def mock_response(query_string):
        query_string = query_string.strip()
        if query_string == "*IDN?":
            return "Rohde&Schwarz,FSV43,123456,1.0"
        if query_string == ":SYST:ERR?":
            # Simuloidaan, että laite on kunnossa (0 = No error)
            return '0,"No error"'
        return "OK"

    device.query.side_effect = mock_response

    print(f"--- Simulointi alkaa (Kohde: {ip_address}:{port}) ---")

    try:
        # PyVISA-asetukset (vaikka käytämme mockia, pidetään logiikka samana)
        device.timeout = 5000
        
        for command in commands:
            clean_cmd = command.strip()
            
            # 2. Lähetetään varsinainen komento
            if "?" in clean_cmd:
                print(f"KYSYLY: {clean_cmd}")
                resp = device.query(clean_cmd)
                print(f"VASTAUS: {resp}")
            else:
                print(f"ASETUS: {clean_cmd}")
                device.write(clean_cmd)
            
            # 3. AUTOMAATTINEN VIRHEENTARKISTUS
            # Kysytään laitteen virhejono jokaisen komennon jälkeen
            error_status = device.query(":SYST:ERR?")
            if not error_status.startswith('0'):
                print(f"!!! LAITEILMOITUS: {error_status}")
            
            time.sleep(delay)
            
    except Exception as e:
        print(f"Virhe suorituksessa: {e}")
    finally:
        device.close()
        print("--- Simulointi päättyi ---")

# Testikomennot
ip = '192.168.1.11'
portti = 5025
scpi_komennot = [
    "*IDN?",
    ":SENS1:SWE:TIME 5",
    ":SENS1:BAND:RES 5000000"
]

send_scpi_commands_with_error_check(ip, portti, scpi_komennot)
