from serial import Serial
import time
import threading
from multiprocessing import Queue
from connection import Connection
from imu import IMU, MAG_CALI_TIMES

# Default connection type
DEFAULT_CONNECTION_TYPE = 'COM'

# Serial Settings
SERIAL_COM_PORT='COM7'
SERIAL_BAUD_RATE = 921600

#BlueZ Settings
BLUEZ_MAC_ADDRESS = "00:1A:FF:06:5A:27"
BLUEZ_RFCOMM_PORT = 1


# IMU State
STATE_STOP = 0
# STATE_CALIBRATION_ACC = 1
STATE_CALIBRATION_MAG = 2
STATE_READ_DATA = 3

# ESA IMU commands
ESA_CMD_STOP = b'\x00'
ESA_CMD_START = b'\x01'
ESA_CMD_MAG_CAL = b'\x02'

# Receiver parse
IMU_PACKET_SIZE = 342

class IMU_Receiver():
    b_ready = True
    state = STATE_CALIBRATION_MAG
    check_debug= False
    use_offset = False
    save_offset = False
    receiving = False
    queue_ready = False

    acc_raw = [0,0,0]
    gyro_raw =[0,0,0]
    mag_raw = [0,0,0]
    time_raw = [0,0,0,0,0]

    time_start = time.time()

    acc = []
    gyro = []
    mag = []
    time = []

    # -----------------------------
    # constructor
    def __init__(self, connection_type=DEFAULT_CONNECTION_TYPE, com_port=SERIAL_COM_PORT, baud_rate=SERIAL_BAUD_RATE, mac_address=BLUEZ_MAC_ADDRESS, rfcomm_port=BLUEZ_RFCOMM_PORT, check_debug=False, use_offset=False,save_offset=False, offset_path="offset.csv", write_raw_csv=True, raw_csv_path='raw.csv', write_csv=True, csv_path="imu.csv"):
        self.connection = Connection(connection_type,mac_address,com_port if connection_type=="COM" else rfcomm_port, baud_rate)
        self.check_debug = check_debug
        self.use_offset = use_offset
        self.save_offset = save_offset
        self.imu = IMU(use_offset,)

        self.write_raw_csv = write_raw_csv
        if write_raw_csv:
            self.csv_raw = open(raw_csv_path,'a')
        self.write_csv = write_csv
        if write_csv:
            self.csv = open(csv_path,'a')
            self._write_csv_header()

    # -----------------------------
    # connect com port
    def com_connect(self):
        # connect
        try:
            self.connection.connect()
        except:
            print("0.1-Com port open fail")
            return False
        
        # send stop
        print("0.1-Com port open success")

        if not self._cmd_write(ESA_CMD_STOP):
            print("0.2-ESA IMU system do not exist")
            self.connection.disconnect()
            return False

        # send start
        print("0.2-ESA IMU system exist")
        if not self._cmd_write(ESA_CMD_START):
            print("0.3-ESA IMU System Start Fail")
            self.connection.disconnect()
            return False
        
        # started
        print("0.3-Start ESA IMU system")
        self.state = STATE_READ_DATA

        # use prerecorded offset
        #if self.use_offset:

        # save recorded offset
        #if self.save_offset:

        self.receiving = True
        self.queue_ready = True
        self.queue = Queue()
        # start parse process
        read_thread = threading.Thread(target=self._read_process)
        read_thread.start()   
        parse_thread =  threading.Thread(target=self._parse_process)
        parse_thread.start()
        
        return True


    # -----------------------------
    # connect com port
    def com_disconnect(self):
        # stop receiving
        self.receiving = False
        self.state = STATE_STOP
        time.sleep(1)
        
        # send stop
        if not self._cmd_write(ESA_CMD_STOP):
            print("COM Port already disconnected")
        self.connection.disconnect()



    def close_queue(self):
        self.queue.cancel_join_thread()
        self.queue.close()
        
    

    #-----------------------------
    # UTILITIES

     # -----------------------------
    # write cmd byte to com port
    def _cmd_write(self, cmd):
        cmd_buff = b'\x55'+cmd+b'\x03\x03\x01\x01\x01\x01\x01\x01\xAA'
        try:
            self.connection.send(bytes(cmd_buff))
        except:
            return False
        
        if cmd == ESA_CMD_STOP:
            try:
                self.connection.read(11)
            except:
                return False

        elif cmd == ESA_CMD_START:
            return True
            # try:
            #     self.connection.read(11)
            # except:
            #     return False

        elif cmd == ESA_CMD_MAG_CAL:
            try:
                self.connection.read(11)
            except:
                return False
        return True
    
    # -----------------------------
    # read imu data
    def _read_process(self):
       while self.receiving:
            buffer = self.connection.read(512)
            if len(buffer) >= 1:
                for b in buffer:
                    if self.receiving:
                        self.queue.put(b)

    # --------------------------------
    # parse imu data
    def _parse_process(self):
        data_array = []
        while self.queue_ready:
            if not self.queue.empty():
                byte = self.queue.get()
                # locate header (0x55 0xaa)
                if len(data_array) == 0:
                    if byte == 0x55:
                        data_array.append(byte)
                        continue
                    else:
                        continue

                if len(data_array) == 1:
                    if byte == 0xaa:
                        data_array.append(byte)
                        continue
                    else:
                        data_array = []
                        continue

                # add data to array until reached packet size
                data_array.append(byte)
                
                # reached packet length, process data
                if len(data_array) >= IMU_PACKET_SIZE:
                    # print(data_array)
                    if self.write_raw_csv:
                        threading.Thread(target=self._write_raw_process, args=(data_array,)).start()
                    
                    # extract data into raw array
                    self.acc_raw = data_array[18:24]
                    self.gyro_raw = data_array[24:30]
                    self.mag_raw = data_array[30:36]
                    self.time_raw = data_array[2:7]
                    data_array = []

                    # state process
                    self._imu_state_machine()

     # --------------------------------
    # write raw data to csv
    def _write_raw_process(self, data_array):
        line = ",".join([str(n) for n in data_array])
        line += "\n"
        self.csv_raw.write(line)

    # --------------------------------
    # write csv heaser
    def _write_csv_header(self):
        self.csv.write("Processed,Time(h),Time(m),Time(s),Time(ms),Delt,AccX,AccY,AccZ,GyroX,GyroY,GyroZ,MagX,MagY,MagZ,Roll,Pinch,Yaw,PCTimestamp\n")

    # --------------------------------
    # state
    def _imu_state_machine(self):
        if self.state == STATE_CALIBRATION_MAG:
            # mag calibration
            self.imu.set_data(self.acc_raw, self.gyro_raw, self.mag_raw, self.time_raw)
            self.imu.update_mag_offset()
            self.imu.print_data()
            print("Calibrating: "+str(self.imu.processed)+'/'+ MAG_CALI_TIMES)
            
            # finish calibrating
            if self.imu.calibarated:
                if self.save_offset:
                    self.imu.save_offset()
                
                print("Calibration finished")
                self.time_start = time.time()
                self.state = STATE_READ_DATA

        elif self.state == STATE_READ_DATA:
            # read data
            self.imu.set_data(self.acc_raw, self.gyro_raw, self.mag_raw, self.time_raw)
            self.imu.print_data()
            if self.write_csv:
                self.imu.write_csv(self.csv)

        








    
                
                    












