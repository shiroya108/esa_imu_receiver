from receiver_bluez import IMU_Receiver_Bluez
import threading
import time

mac_address = "00:1A:FF:06:5A:24"
rfcomm_port = 1
receiver = IMU_Receiver_Bluez(mac_address=mac_address, rfcomm_port=rfcomm_port)
receiver.com_connect()