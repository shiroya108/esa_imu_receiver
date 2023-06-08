from serial import Serial
import time
import threading
from multiprocessing import Queue
from connection import Connection

# Default connection type
DEFAULT_CONNECTION_TYPE = 'COM'

# Serial Settings
SERIAL_COM_PORT='COM7'
SERIAL_BAUD_RATE = 921600

#BlueZ Settings
BLUEZ_MAC_ADDRESS = "00:1A:FF:06:5A:27"
BLUEZ_RFCOMM_PORT = 1


# Glove State
GLOVE_STATE_STOP = 0
GLOVE_STATE_CALIBRATION_ACC = 1
GLOVE_STATE_CALIBRATION_MAG = 2
GLOVE_STATE_READ_DATA = 3

# Glove CMD
GLOVE_CMD_STOP = b'\x00'
GLOVE_CMD_START = b'\x01'
GLOVE_CMD_MAG_CAL = b'\x02'

# Receiver parse
IMU_PACKET_SIZE = 342

class IMU_Receiver():
    b_ready = True
    state = GLOVE_STATE_CALIBRATION_MAG
    check_debug= False
    use_offset = False
    save_offset = False
    receiving = False
    queue_ready = False

    acc_raw = [0,0,0,0,0,0]
    gyro_raw = [0,0,0,0,0,0]
    mag_raw = [0,0,0,0,0,0]

    acc = [0,0,0]
    gyro = [0,0,0]
    mag = [0,0,0]

    # -----------------------------
    # constructor
    def __init__(self, connection_type=DEFAULT_CONNECTION_TYPE, com_port=SERIAL_COM_PORT, baud_rate=SERIAL_BAUD_RATE, mac_address=BLUEZ_MAC_ADDRESS, rfcomm_port=BLUEZ_RFCOMM_PORT, check_debug=False, use_offset=False,save_offset=False):
        self.connection = Connection(connection_type,mac_address,com_port if connection_type=="COM" else rfcomm_port, baud_rate)
        self.check_debug = check_debug
        self.use_offset = use_offset
        self.save_offset = save_offset

        self.csv_raw = open('raw.csv','a')
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

        if not self._cmd_write(GLOVE_CMD_STOP):
            print("0.2-Glove system do not exist")
            self.connection.disconnect()
            return False

        # send start
        print("0.2-Glove system exist")
        if not self._cmd_write(GLOVE_CMD_START):
            print("0.3-Glove System Start Fail")
            self.connection.disconnect()
            return False
        
        # started
        print("0.3-Start Glove system")
        self.state = GLOVE_STATE_READ_DATA

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
        self.state = GLOVE_STATE_STOP
        time.sleep(1)
        
        # send stop
        if not self._cmd_write(GLOVE_CMD_STOP):
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
        
        if cmd == GLOVE_CMD_STOP:
            try:
                self.connection.read(11)
            except:
                return False

        elif cmd == GLOVE_CMD_START:
            return True
            # try:
            #     self.connection.read(11)
            # except:
            #     return False

        elif cmd == GLOVE_CMD_MAG_CAL:
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
                if len(data_array) < IMU_PACKET_SIZE-1:
                    data_array.append(byte)
                else:
                    print(data_array)
                    threading.Thread(target=self._write_raw_process, args=(data_array,)).start()
                    data_array = []

    def _write_raw_process(self, data_array):
        line = ",".join([str(n) for n in data_array])
        line += "\n"
        self.csv_raw.write(line)
                
                    












