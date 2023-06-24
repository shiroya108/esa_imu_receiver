from receiver.receiver import IMU_Receiver
import time

mac_address = "00:1A:FF:06:5A:24"
rfcomm_port = 1
receiver = IMU_Receiver(connection_type="MAC", mac_address=mac_address, rfcomm_port=rfcomm_port)
if receiver.com_connect():
    time.sleep(10)
    receiver.com_disconnect()
    print("disconnected")
    receiver.close_queue()
    print("queue closed")
    exit()