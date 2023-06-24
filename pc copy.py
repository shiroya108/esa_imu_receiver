import time
from receiver.receiver import IMU_Receiver, STATE_CALIBRATION_MAG



receiver = IMU_Receiver(connection_type="COM", com_port="COM8", baud_rate=9600, save_offset=True, offset_path="offset.csv")
if receiver.com_connect():
    time.sleep(300)
    receiver.com_disconnect()
    print("disconnected")
    receiver.close_queue()
    print("queue closed")
    exit()

    

