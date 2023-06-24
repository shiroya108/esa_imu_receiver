import time
from receiver.receiver import IMU_Receiver
from receiver.imu import MAG_CALI_TIMES
import threading

def timing_process(receiver):
    time.sleep(60)
    receiver.com_disconnect()
    print("disconnected")
    receiver.close_queue()
    print("queue closed")
    exit()


def calibration_callback(acc,gyro,mag,proc,time,delt,cali_times):
    print(f"Calibrating: {proc} / {cali_times}")

def finish_calibration_callback(receiver):
    threading.Thread(target=timing_process,args=(receiver,)).start()

def receive_callback(acc,gyro,mag,proc,time,delt,cali_times):
    print(f"acc:  {acc[0]}/{acc[1]}/{acc[2]}")
    print(f"gyro: {gyro[0]}/{gyro[1]}/{gyro[2]}")
    print(f"mag:  {mag[0]}/{mag[1]}/{mag[2]}")
    print(f"time: {time._hour}:{time._minute}:{time._second}.{time._millisecond}")
    print(f"processed: {proc} / delta: {delt}")


receiver = IMU_Receiver(connection_type="COM", com_port="COM7", baud_rate=9600, use_offset=True, save_offset=True, offset_path="offset.csv", write_csv=True, write_raw_csv=True, calibration_callback=calibration_callback,finish_calibration_callback=finish_calibration_callback, receive_callback=receive_callback)
if receiver.com_connect():
    receiver.start_write_csv()
    

