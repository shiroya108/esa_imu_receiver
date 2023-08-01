from recorder2 import Ui_ESAIMU_RecorderUI
from PyQt5 import QtCore, QtGui, QtWidgets
from serial.tools import list_ports
from receiver.receiver import IMU_Receiver, STATE_STOP
import sys
from playsound import playsound
import math
import threading
import time

class Recorder(Ui_ESAIMU_RecorderUI):
    receive_count = 0
    com_port = ""

    receive_count_2 = 0
    com_port_2 = ""

    start_writing_time = 0
    writing_time = 0

    def __init__(self):
        super().__init__()
    
    #----------------------------------------------
    # init
    def init(self):
        self.updateCom()
        self.buttonEvents()

    # add button events
    def buttonEvents(self):
        self.ConnectButton.clicked.connect(self.connectPort)
        self.BrowseOffsetButton.clicked.connect(self.choose_offset_location)
        self.BrowseSaveButton.clicked.connect(self.choose_save_location)
        self.RecordButton.clicked.connect(self.write_csv)

        self.ConnectButton_2.clicked.connect(self.connectPort_2)
        self.BrowseOffsetButton_2.clicked.connect(self.choose_offset_location_2)

     # update com port list
    def updateCom(self):
        ports = list_ports.comports()
        portnames=[]
        for p in ports:
            portnames.append(p.name)
        self.ComPortSelect.addItems(portnames)
        self.ComPortSelect_2.addItems(portnames)

    # connect port
    def connectPort(self):
        def calibrating(acc,gyro,mag,proc,time,delt,cali_times):
            self.ReceivedNumber.setText(f"{proc} / {cali_times}")
            self._display_imu_values(acc,gyro,mag)

        def calibrated(rec):
            self.StatusText.setText(f"Receiving from {self.com_port}...")

        def receiving(acc,gyro,mag,proc,time,delt,cali_times):
            self.receive_count += 1
            if self.receive_count >= 9:
                self.receive_count = 0
                self.ReceivedNumber.setText(f"{proc}")
                self._display_imu_values(acc,gyro,mag)
                
        # def end_writing(rec):
        #     # play bell sound
        #     playsound("./audio/bell.mp3",False)
        #     self.RecordButton.setText("Record")
        #     self.RecordButton.clicked.disconnect()
        #     self.RecordButton.clicked.connect(self.write_csv)  

        self.com_port = self.ComPortSelect.currentText()

        load_offset = self.radioLoadOffset.isChecked()
        save_offset= self.radioSaveOffset.isChecked()
        use_offset = load_offset or save_offset or self.radioOneTimeOffset.isChecked()
        offset_path = self.OffsetPath.text()

        packet_size =  int(self.PacketSizeSelect.currentText())

        # self.receiver = IMU_Receiver("COM",self.com_port,use_offset=use_offset,save_offset=save_offset,load_offset=load_offset, offset_path=offset_path, packet_size=packet_size, calibration_callback=calibrating, finish_calibration_callback=calibrated, receive_callback=receiving, write_timer_end_callback=end_writing)
        self.receiver = IMU_Receiver("COM",self.com_port,use_offset=use_offset,save_offset=save_offset,load_offset=load_offset, offset_path=offset_path, packet_size=packet_size, calibration_callback=calibrating, finish_calibration_callback=calibrated, receive_callback=receiving)

        if self.receiver.com_connect():
            self.StatusText.setText("Calibrating...")
            # show disconnect
            self.ConnectButton.setText("Disconnect")
            self.ConnectButton.clicked.disconnect()
            self.ConnectButton.clicked.connect(self.disconnectPort)
        else:
            self.StatusText.setText("Unable to connect "+self.com_port)


       # connect port
    def connectPort_2(self):
        def calibrating(acc,gyro,mag,proc,time,delt,cali_times):
            self.ReceivedNumber_2.setText(f"{proc} / {cali_times}")
            self._display_imu_values_2(acc,gyro,mag)

        def calibrated(rec):
            self.StatusText_2.setText(f"Receiving from {self.com_port_2}...")

        def receiving(acc,gyro,mag,proc,time,delt,cali_times):
            self.receive_count_2 += 1
            if self.receive_count_2 >= 9:
                self.receive_count_2 = 0
                self.ReceivedNumber_2.setText(f"{proc}")
                self._display_imu_values_2(acc,gyro,mag)

        self.com_port_2 = self.ComPortSelect_2.currentText()

        load_offset = self.radioLoadOffset_2.isChecked()
        save_offset= self.radioSaveOffset_2.isChecked()
        use_offset = load_offset or save_offset or self.radioOneTimeOffset_2.isChecked()
        offset_path = self.OffsetPath_2.text()

        packet_size =  int(self.PacketSizeSelect_2.currentText())

        self.receiver_2 = IMU_Receiver("COM",self.com_port_2,use_offset=use_offset,save_offset=save_offset,load_offset=load_offset, offset_path=offset_path, packet_size=packet_size, calibration_callback=calibrating, finish_calibration_callback=calibrated, receive_callback=receiving)

        if self.receiver_2.com_connect():
            self.StatusText_2.setText("Calibrating...")
            # show disconnect
            self.ConnectButton_2.setText("Disconnect")
            self.ConnectButton_2.clicked.disconnect()
            self.ConnectButton_2.clicked.connect(self.disconnectPort_2)
        else:
            self.StatusText_2.setText("Unable to connect "+self.com_port_2)

    def disconnectPort(self):
        self.receiver.com_disconnect()
        self.StatusText.setText("Disconnected")
        self.ConnectButton.setText("Connect")
        self.receive_count = 0
        self.ReceivedNumber.setText("")
        self.ConnectButton.clicked.disconnect()
        self.ConnectButton.clicked.connect(self.connectPort)

    def disconnectPort_2(self):
        self.receiver_2.com_disconnect()
        self.StatusText_2.setText("Disconnected")
        self.ConnectButton_2.setText("Connect")
        self.receive_count_2 = 0
        self.ReceivedNumber_2.setText("")
        self.ConnectButton_2.clicked.disconnect()
        self.ConnectButton_2.clicked.connect(self.connectPort_2)


    def choose_offset_location(self):
        if self.radioLoadOffset.isChecked():
            filename = QtWidgets.QFileDialog.getOpenFileName()[0]
        elif self.radioSaveOffset.isChecked():
            filename = QtWidgets.QFileDialog.getSaveFileName()[0]
        else:
            filename = ""
            QtWidgets.QMessageBox.information(None,"Error","Select load or save Offset first")
        self.OffsetPath.setText(filename)

    def choose_offset_location_2(self):
        if self.radioLoadOffset_2.isChecked():
            filename = QtWidgets.QFileDialog.getOpenFileName()[0]
        elif self.radioSaveOffset_2.isChecked():
            filename = QtWidgets.QFileDialog.getSaveFileName()[0]
        else:
            filename = ""
            QtWidgets.QMessageBox.information(None,"Error","Select load or save Offset first")
        self.OffsetPath_2.setText(filename)

    def choose_save_location(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(None,"Select Save Location")
        self.SavePath.setText(path)


    def write_csv(self):
        def writing_timer(write_time,use_rec2):
            writing_minute = 0
            while self.receiver.writing_csv:
                # check every 0.1s
                time.sleep(0.1)
                self._display_recording_time()
                
                s = math.floor(self.writing_time)
                m = math.floor(s/60)               

                # stop writing when time is up
                if s >= write_time:
                    self.receiver.stop_write_csv()
                    if use_rec2:
                        self.receiver_2.stop_write_csv()
                    self.RecordButton.setText("Record")
                    self.RecordButton.clicked.disconnect()
                    self.RecordButton.clicked.connect(self.write_csv)  
                    playsound('./audio/end.mp3',False)
                    break
            
                # play sound for every minute
                if self.writing_time >= 60 and write_time - self.writing_time >= 10 and writing_minute != m :
                    playsound('./audio/minute.mp3',False)
                    writing_minute = m
        
        if not hasattr(self,"receiver"):
            QtWidgets.QMessageBox.information(None,"Error","Connect to COM Port first")

        use_rec2 = hasattr(self,"receiver_2")

        if self.SavePath.text() == "":
            QtWidgets.QMessageBox.information(None,"Error","Select Save Path first")
            return
    
        # create csv file
        self.receiver.create_csv(True,self.SavePath.text()+'/data_'+self.com_port+".csv")

        if self.checkWriteRaw.isChecked():
            self.receiver.create_raw_csv(True,self.SavePath.text()+'/raw_'+self.com_port+".csv")

        # do same to receiver 2        
        if use_rec2:
            self.receiver_2.create_csv(True,self.SavePath.text()+'/data_'+self.com_port_2+".csv")
            if self.checkWriteRaw.isChecked():
                self.receiver_2.create_raw_csv(True,self.SavePath.text()+'/raw_'+self.com_port_2+".csv")

        # Play sound  
        playsound('./audio/start.mp3',False)

        # set timer if needed
        if self.checkUseTimer.isChecked() and self.RecordingTimeInput.value() > 0:
            timer_process=threading.Thread(target=writing_timer,args=(self.RecordingTimeInput.value(),use_rec2,))


        self.receiver.start_write_csv(False)
        # if self.checkUseTimer.isChecked() and self.RecordingTimeInput.value() > 0:
        #     self.receiver.start_write_csv(True,self.RecordingTimeInput.value())
        # else:
        #     self.receiver.start_write_csv(False)

        # do same to receiver 2        
        if use_rec2:
            # if self.checkUseTimer.isChecked() and self.RecordingTimeInput.value() > 0:
            #     self.receiver_2.start_write_csv(True,self.RecordingTimeInput.value())
            # else:
                self.receiver_2.start_write_csv(False)

        # change button to stop
        if self.receiver.writing_csv:
            self.start_writing_time = time.time()
            timer_process.start()
    
            self.RecordButton.setText("Stop")
            self.RecordButton.clicked.disconnect()
            self.RecordButton.clicked.connect(self.stop_write_csv)
            

    def stop_write_csv(self):
        # stop writing
        self.receiver.stop_write_csv()

        # stop receiver 2 writing
        if hasattr(self,"receiver_2"):
            self.receiver_2.stop_write_csv()

        self.RecordButton.setText("Record")
        self.RecordButton.clicked.disconnect()
        self.RecordButton.clicked.connect(self.write_csv)  

    def _display_imu_values(self,acc,gyro,mag):
        self.ax.setText(f"{acc[0]:0,.3f}")
        self.ay.setText(f"{acc[1]:0,.3f}")
        self.az.setText(f"{acc[2]:0,.3f}")
        self.gx.setText(f"{gyro[0]:0,.3f}")
        self.gy.setText(f"{gyro[1]:0,.3f}")
        self.gz.setText(f"{gyro[2]:0,.3f}")
        self.mx.setText(f"{mag[0]:0,.3f}")
        self.my.setText(f"{mag[1]:0,.3f}")
        self.mz.setText(f"{mag[2]:0,.3f}")


    def _display_imu_values_2(self,acc,gyro,mag):
        self.ax_2.setText(f"{acc[0]:0,.3f}")
        self.ay_2.setText(f"{acc[1]:0,.3f}")
        self.az_2.setText(f"{acc[2]:0,.3f}")
        self.gx_2.setText(f"{gyro[0]:0,.3f}")
        self.gy_2.setText(f"{gyro[1]:0,.3f}")
        self.gz_2.setText(f"{gyro[2]:0,.3f}")
        self.mx_2.setText(f"{mag[0]:0,.3f}")
        self.my_2.setText(f"{mag[1]:0,.3f}")
        self.mz_2.setText(f"{mag[2]:0,.3f}")

    def _display_recording_time(self):
        if self.receiver.writing_csv:
            current_time = time.time()
            self.writing_time = current_time - self.start_writing_time

            ms = math.floor(self.writing_time * 1000) % 1000
            s = math.floor(self.writing_time) % 60
            m = math.floor(self.writing_time / 60) 
           
            self.RecordTime.setText(f"{m}:{s:02}.{ms:03}")

    # exit window
    def close(self,event):
        print("close")
        if hasattr(self, "receiver"):
            if self.receiver.state != STATE_STOP:
                self.receiver.stop_write_csv()
                self.receiver.com_disconnect()
                self.receiver.close_queue()

        if hasattr(self, "receiver_2"):
            if self.receiver_2.state != STATE_STOP:
                self.receiver_2.stop_write_csv()
                self.receiver_2.com_disconnect()
                self.receiver_2.close_queue()
        exit()




app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()
ui = Recorder()
ui.setupUi(window)
ui.init()
window.closeEvent = ui.close
window.show()
sys.exit(app.exec_())


# receiver = IMU_Receiver(connection_type="COM", com_port="COM8", baud_rate=9600)
# if receiver.com_connect():
#     time.sleep(10)
#     receiver.com_disconnect()
#     print("disconnected")
#     receiver.close_queue()
#     print("queue closed")
#     exit()

    

