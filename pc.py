# from receiver_bluez import IMU_Receiver_Bluez
from receiver import IMU_Receiver
import time

receiver = IMU_Receiver(connection_type="COM", com_port="COM8", baud_rate=9600)
if receiver.com_connect():
    time.sleep(10)
    receiver.com_disconnect()
    print("disconnected")
    receiver.close_queue()
    print("queue closed")
    exit()

    

