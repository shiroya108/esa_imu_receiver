from receiver.receiver import IMU_Receiver
import time


receivers = []
addresses = []

with open("rasp_mac_addresses.txt","r") as f:
    addresses_str = f.read()
    addresses = addresses_str.split(",")




for i,a in enumerate(addresses):
    csv_filename = a.replace(":","_") + ".csv"
    raw_filename = a.replace(":","_") + "_raw.csv"
    receivers.append(IMU_Receiver(connection_type="MAC", mac_address=a, rfcomm_port=i+1, use_offset=True, write_csv=True, csv_path=csv_filename, write_raw_csv=True, raw_csv_path=raw_filename))