from machine import SD
import os
import time

class CSV_logger:
    def __init__(self, dir="/sd/hiverizelog"):
        self.dir = dir
        # Mount SD
        # Pins are Dat0: P8, SCLK: P23, CMD: P4, at least I think so
        # Apparently Pins can not be changed
        sd = SD()
        os.mount(sd, '/sd')

        # Check if directory, eg. hiverizelog, was already created,
        # and create it, if not existing:
        try:
            os.listdir(dir)
        except OSError:
            os.mkdir(dir)
        print("Init -> CSV logger in directory " +dir)

    def list_files(self):
        return os.listdir(self.dir)

    def read_file(self, file):
        path = "{}/{}".format(self.dir,file)
        print(path)
        f = open(path)
        content = f.read()
        f.close()
        return content



    def get_time_string(self):
        # Get Time
        write_time = time.time()
        write_time     += 3600
        datetime_list = time.localtime(write_time)
        date_string = "{:4d}-{:02d}-{:02d}H{:02d}".format(*datetime_list[0:4])
        datetime_string = "{:4d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*datetime_list[0:6])
        return date_string, datetime_string

    def get_date(self):
        write_time = time.time()
        write_time     += 3600                                  # UTC + 1 Stunde
        datetime_list = time.localtime(write_time)
        date_string = "{:4d}-{:02d}-{:02d}".format(*datetime_list[0:3])
        return date_string

    def get_time(self):
        write_time = time.time()
        write_time     += 3600                                  # UTC + 1 Stunde
        datetime_list = time.localtime(write_time)
        time_string = "{:02d}:{:02d}:{:02d}".format(*datetime_list[3:6])
        return time_string

    def get_hour(self):
        write_time = time.time()
        write_time     += 3600                                  # UTC + 1 Stunde
        datetime_list = time.localtime(write_time)
        time_string = "{:02d}".format(*datetime_list[3:4])
        return time_string

    def add(self, sensor, value):
        time_string, full_time_string = self.get_time_string()
        # concat filepath
        file_path = self.dir + "/" +time_string + ".csv"
        # Write header, if file did not exist before
        try:
            f = open(file_path, 'r')
            f.close()
        except OSError:
            f = open(file_path, 'w')
            f.write('Time, Sensor, Value\n')
            f.close()
            print("Logging measurements to " +file_path)
        # Get full timestamp

        # Append Value
        f = open(file_path, 'a')
        f.write("{}, {}, {}\n".format(full_time_string, sensor, value))
        f.close()

    def log(self, log_text):
        print(log_text)
        time_string, full_time_string = self.get_time_string()
        # concat filepath
        file_path = self.dir + "/logging.csv"
        # Write header, if file did not exist before
        try:
            f = open(file_path, 'r')
            f.close()
        except OSError:
            f = open(file_path, 'w')
            f.write('Timestring, Bob-Logging\n')
            f.close()
            print("Logging information, warnings and error to " +file_path)

        # Append Value
        f = open(file_path, 'a')
        f.write("{}, {}\n".format(full_time_string, log_text))
        f.close()

    def add_dict(self, data):
        # Get Time
        time_string, full_time_string = self.get_time_string()
        # combine dict entries
        data_list = ["{},{},{}\n".format(full_time_string, key, value) for key, value in data.items()]
        # concat filepath
        file_path = self.dir + "/" +time_string + ".csv"
        # Write header, if file did not exist before
        try:
            f = open(file_path, 'r')
            f.close()
        except OSError:
            f = open(file_path, 'w')
            f.write('Time, Sensor, Value\n')
            f.close()
            print("Logging measurements to " +file_path)
        # Append Value
        with open(file_path, 'a') as f:
            f.write("".join(data_list))
        print("Wrote {} lines to csv at {}".format(len(data_list), full_time_string))

    def add_dict_lineprotocol(self, data, sensor_key):
        print("in lineprotocol")
        # Get Time
        time_string, full_time_string = self.get_time_string()
        write_time = int(round(time.time() * 1000*1000*1000))
        print(write_time)
        # name and key
        name_key = "sensors,key={}".format(sensor_key)
        print(name_key)
        # combine dict entries
        data_list = ["{}={},".format(key, value) for key, value in data.items()]
        print(data_list)
        data_list = "".join(data_list)
        print(data_list)
        # delete last comma
        data_list = data_list[:-1]

        # combine
        full_string = "{} {} {}\n".format(name_key, data_list, write_time)

        # concat filepath
        file_path = self.dir + "/" +time_string + ".txt"
        # Write header, if file did not exist before
        try:
            f = open(file_path, 'r')
            f.close()
        except OSError:
            f = open(file_path, 'w')
            f.close()
            print("Logging measurements to " +file_path)
        # Append Value
        with open(file_path, 'a') as f:
            f.write(full_string)
        print("Wrote 1 line to csv at {}".format(full_time_string))

    
