from recorder import Ui_ESAIMU_RecorderUI
from PyQt5 import QtCore, QtGui, QtWidgets
from serial.tools import list_ports
from receiver.receiver import IMU_Receiver, STATE_STOP
import sys
from playsound import playsound
import math

class Recorder(Ui_ESAIMU_RecorderUI):
    receive_count = 0
    com_port = ""
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
    # add button events
    def buttonEvents(self):
        self.ConnectButton.clicked.connect(self.connectPort)
        self.BrowseOffsetButton.clicked.connect(self.choose_offset_location)
        self.BrowseSaveButton.clicked.connect(self.choose_save_location)
        self.RecordButton.clicked.connect(self.write_csv)

     # update com port list
    def updateCom(self):
        ports = list_ports.comports()
        portnames=[]
        for p in ports:
            portnames.append(p.name)
        self.ComPortSelect.addItems(portnames)

    # connect port
    def connectPort(self):
        def calibrating(acc,gyro,mag,proc,time,delt,cali_times):
            self.ReceivedNumber.setText(f"{proc} / {cali_times}")
            self._display_imu_values(acc,gyro,mag)

        def calibrated(rec):
            self.StatusText.setText("Receiving...")

        def receiving(acc,gyro,mag,proc,time,delt,cali_times):
            self.ReceivedNumber.setText(f"{proc}")
            self.receive_count += 1
            if self.receive_count >= 9:
                self.receive_count = 0
                self._display_imu_values(acc,gyro,mag)
                self._display_recording_time(time)
                

        def end_writing(rec):
            # play bell sound
            playsound("./audio/bell.mp3",False)
            self.RecordButton.setText("Record")
            self.RecordButton.clicked.disconnect()
            self.RecordButton.clicked.connect(self.write_csv)  

        self.com_port = self.ComPortSelect.currentText()

        load_offset = self.radioLoadOffset.isChecked()
        save_offset= self.radioSaveOffset.isChecked()
        use_offset = load_offset or save_offset or self.radioOneTimeOffset.isChecked()
        offset_path = self.OffsetPath.text()

        packet_size =  int(self.PacketSizeSelect.currentText())

        self.receiver = IMU_Receiver("COM",self.com_port,use_offset=use_offset,save_offset=save_offset,load_offset=load_offset, offset_path=offset_path, packet_size=packet_size, calibration_callback=calibrating, finish_calibration_callback=calibrated, receive_callback=receiving, write_timer_end_callback=end_writing)

        if self.receiver.com_connect():
            self.StatusText.setText("Calibrating...")
            # show disconnect
            self.ConnectButton.setText("Disconnected")
            self.ConnectButton.clicked.disconnect()
            self.ConnectButton.clicked.connect(self.disconnectPort)
        else:
            self.StatusText.setText("Unable to connect "+self.com_port)

    def disconnectPort(self):
        self.receiver.com_disconnect()
        self.StatusText.setText("Disconnected")
        self.ConnectButton.setText("Connect")
        self.receive_count = 0
        self.ReceivedNumber.setText("")
        self.ConnectButton.clicked.disconnect()
        self.ConnectButton.clicked.connect(self.connectPort)


    def choose_offset_location(self):
        if self.radioLoadOffset.isChecked():
            filename = QtWidgets.QFileDialog.getOpenFileName()[0]
        elif self.radioSaveOffset.isChecked():
            filename = QtWidgets.QFileDialog.getSaveFileName()[0]
        else:
            filename = ""
            QtWidgets.QMessageBox.information(None,"Error","Select load or save Offset first")
        self.OffsetPath.setText(filename)

    def choose_save_location(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(None,"Select Save Location")
        self.SavePath.setText(path)


    def write_csv(self):
        if not hasattr(self,"receiver"):
            QtWidgets.QMessageBox.information(None,"Error","Connect to COM Port first")

        if self.SavePath.text() == "":
            QtWidgets.QMessageBox.information(None,"Error","Select Save Path first")
            return
    

        # create csv file
        self.receiver.create_csv(True,self.SavePath.text()+'/data_'+self.com_port+".csv")

        if self.checkWriteRaw.isChecked():
            self.receiver.create_raw_csv(True,self.SavePath.text()+'/raw_'+self.com_port+".csv")

        # Play sound  
        playsound('./audio/start.mp3',True)

        # set timer if needed
        if self.checkUseTimer.isChecked() and self.RecordingTimeInput.value() > 0:
            self.receiver.start_write_csv(True,self.RecordingTimeInput.value())
        else:
            self.receiver.start_write_csv(False)

        # change button to stop
        if self.receiver.writing_csv:
            self.start_writing_time = self.receiver.imu._time.total_time
            self.RecordButton.setText("Stop")
            self.RecordButton.clicked.disconnect()
            self.RecordButton.clicked.connect(self.stop_write_csv)
            

    def stop_write_csv(self):
        self.receiver.stop_write_csv()
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

    def _display_recording_time(self,time):
        if self.receiver.writing_csv:
            current_time = time.total_time
            recorded_time = current_time - self.start_writing_time
            ms = recorded_time % 1000
            s = math.floor(recorded_time / 1000) % 60
            m = math.floor(recorded_time / 60000)
            self.RecordTime.setText(f"{m}:{s:02}.{ms:03}")


    # exit window
    def close(self,event):
        print("close")
        if hasattr(self, "receiver"):
            if self.receiver.state != STATE_STOP:
                self.receiver.stop_write_csv()
                self.receiver.com_disconnect()
                self.receiver.close_queue()
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

    

