import time
import threading
from imu_parser import IMU_Parser
import bluetooth

# Glove State
GLOVE_STATE_STOP = 0
GLOVE_STATE_CALIBRATION_ACC = 1
GLOVE_STATE_CALIBRATION_MAG = 2
GLOVE_STATE_READ_DATA = 3


# Glove CMD
GLOVE_CMD_STOP = b'\x00'
GLOVE_CMD_START = b'\x01'
GLOVE_CMD_MAG_CAL = b'\x02'

class IMU_Receiver_Bluez():

    # status
    b_ready = True
    state = GLOVE_STATE_CALIBRATION_MAG
    check_debug= False
    use_offset = False
    save_offset = False
    receiving = False

    # raw 
    raw_byte_data = b""


    # filtered



    # parser
    # parser = IMU_Parser

    # -----------------------------
    # constructor
    def __init__(self, mac_address, rfcomm_port=1, check_debug=False, use_offset=False,save_offset=False, offset_file=""):
        self.mac_address = mac_address
        self.rfcomm_port = rfcomm_port
        self.check_debug = check_debug
        self.use_offset = use_offset
        self.save_offset = save_offset

        # if use_offset:
        #     self.parser.


    # -----------------------------
    # connect com port
    def com_connect(self):
        # connect
        #print(self.mac_address)
        #print(self.rfcomm_port)
        
        try:
            self.connection = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
            self.connection.connect((self.mac_address, self.rfcomm_port))
        except Exception as e:
            print(e)
            print("0.1-Com port open fail")
            return False
        
        # send stop
        print("0.1-Com port open success")

        if not self._cmd_write(GLOVE_CMD_STOP):
            print("0.2-Glove system do not exist")
            self.connection.close()
            return False

        # send start
        print("0.2-Glove system exist")
        if not self._cmd_write(GLOVE_CMD_START):
            print("0.3-Glove System Start Fail")
            self.connection.close()
            return False
        
        # started
        print("0.3-Start Glove system")
        self.state = GLOVE_STATE_READ_DATA

        # use prerecorded offset
        #if self.use_offset:

        # save recorded offset
        #if self.save_offset:
        self.receiving = True
        
        # start parse process
        parse_thread = threading.Thread(target=self._parse_process)
        parse_thread.start()       
        
        return True
    
    # -----------------------------
    # connect com port
    def com_disconnect(self):
        # stop receiving
        self.receiving = False
        time.sleep(1)
        
        # send stop
        if not self._cmd_write(GLOVE_CMD_STOP):
            print("COM Port already disconnected")
        
        self.connection.close()
   
    
    # -----------------------------
    # read and parse imu data
    def _parse_process(self):
        self.time = time.time()
        while self.receiving:
            # buffer = self.connection.read(2048000)
            buffer = self.connection.recv(1024)
            self.raw_byte_data = buffer
            print(buffer)  

    #-----------------------------
    # UTILITIES

     # -----------------------------
    # write cmd byte to com port
    def _cmd_write(self, cmd):
        cmd_buff = b'\x55'+cmd+b'\x03\x03\x01\x01\x01\x01\x01\x01\xAA'
        try:
            self.connection.send(bytes(cmd_buff))
        except Exception as e:
            print(e)
            return False
        
        if cmd == GLOVE_CMD_STOP:
            try:
                self.connection.recv(11)
            except Exception as e:
                print(e)
                return False

        elif cmd == GLOVE_CMD_START:
            pass
            # try:
            #     self.connection.read(11)
            # except:
            #     return False

        elif cmd == GLOVE_CMD_MAG_CAL:
            try:
                self.connection.recv(11)
            except Exception as e:
                print(e)
                return False
        return True


