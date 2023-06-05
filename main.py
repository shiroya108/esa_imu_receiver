from receiver import IMU_Receiver
import threading
import time

receiver = IMU_Receiver('COM7')
# receiver = IMU_Receiver('/dev/rfcomm0')
receiver.com_connect()




# print_thread = threading.Thread(target=print_process)
# print_thread.start()