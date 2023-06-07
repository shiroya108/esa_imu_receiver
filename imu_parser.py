from multiprocessing import Queue

PACKET_SIZE = 342

class IMU_Parser():
    # data
    id = 0
    acc = [0,0,0]
    gyro = [0,0,0]
    mag = [0,0,0]    
    
    # offset
    acc_total = [0,0,0]
    gyro_total = [0,0,0]
    mag_total = [0,0,0]  
    acc_offset = [0,0,0]
    gyro_offest = [0,0,0]
    mag_offset = [0,0,0]
    mag_min = [-32767, -32767, -32767]
    mag_max = [32767, 32767, 32767]

    # scale
    gscale = 0
    ascale = 0
    mscale = 0
    gres = 1
    ares = 1
    mres = 1

    def __init__(self,input_queue=Queue, output_queue=Queue):
        self.input_queue = input_queue
        self.output_queue = output_queue


    #------------------------------
    # read offset file
    def read_offset_file(self,path):
        with open(path) as f:
            offset_string = f.readline()
        offset = offset_string.split(",")


    def parse_process(self):
        while(True):
            self.input_queue.get()