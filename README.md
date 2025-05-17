# Data collection of Bluetooth IMU module
Receive acceleration, gyroscope and magnetometer values from bluetooth IMU module
May be applied to embedded applications or used as data collection on PC

## Prerequisites
- PyQt5
- Bluetooth

## Use in embedded applications
Example in rasp_record.py and rasp_cli.py
Use MAC as connection_type and enter your module MAC address

### Python usage
IMU_Receiver::__init__()
Create receiver object
- connection_type=DEFAULT_CONNECTION_TYPE / "COM" or "MAC", whether connect by COM port or MAC adderess
- com_port=SERIAL_COM_PORT  // COM port of module
- baud_rate=SERIAL_BAUD_RATE  // default 921600
- mac_address=BLUEZ_MAC_ADDRESS // MAC address of module
- rfcomm_port=BLUEZ_RFCOMM_PORT // 1 by default
- packet_size=36 // 36 by default, do not change unless change of IMU module firmware
- check_debug=False // debug IMU messages in output
- use_offset=True // Use offset file
- load_offset=False   // Whether to load offset file, use_offset must be true to load
- save_offset=False  // Whether to save offset file, use_offset must be true to save
- offset_path="offset.csv" // Path of offset file for loading or saving
- write_raw_csv=False // Whether to write IMU raw data (without offset)
- raw_csv_path='raw.csv' // Path of raw data CSV
- write_csv=False // Whether to write data to CSV file
- csv_path="imu.csv"  //
- calibration_callback=lambda acc,gyro,mag,proc,time,delt,cali_times:None // Callback when calibration
- finish_calibration_callback=lambda rec:None // Callback of calibration finished
- receive_callback=lambda acc,gyro,mag,proc,time,delt,cali_times:None // Callback when receiving data, please put your processing here if you need real-time process
- write_timer_end_callback=lambda rec:None // Callback after writing timer has ended

IMU_Receiver::com_connect()
Connect IMU receiver
Return: Boolean

IMU_Receiver::com_disconnect()
Disconnect IMU receiver

IMU_Receiver::close_queue()
Close data queue

IMU_Receiver::create_csv(write_csv,csv_path)
Create CSV file
- write_csv: Boolean, whether to write CSV
- csv_path: String, CSV path

IMU_Receiver::create_raw_csv(write_csv,csv_path)
Create CSV file for raw data
- write_csv: Boolean, whether to write raw CSV
- csv_path: String, raw CSV path

IMU_Receiver::start_write_csv(set_write_timer, write_time):
Start writing CSV
- set_write_timer: Boolean, whether to set timer for writing CSV
- write_time: Number, number of seconds for timer

IMU_Receiver::stop_write_csv()
Stop writing CSV

## IMU data collection on PC
Example in pc_ui2.py  
Support collection of two IMU modules at once  
Support timing to record IMU data in a number of seconds
### PC Usage
1. Select COM port for connection
2. Load calibration file or create calibration
3. Press "Connect"
4. Do calibration if needed
5. Do the same and connect to second COM port if needed
6. Enter save location
7. Select "use timer" and enter number of seconds if needed
8. Press "Record"
9. Press "Stop" if finish recording or record until timer has ended
