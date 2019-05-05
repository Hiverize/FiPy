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
        print("Initialised CSV logger in directory " +dir)

    def get_time_string(self):
        # Get Time
        write_time = time.time()
        datetime_list = time.localtime(write_time)
        date_string = "{}-{}-{}H{}".format(*datetime_list[0:4])
        datetime_string = "{}-{}-{} {}:{}:{}".format(*datetime_list[0:6])
        return date_string, datetime_string

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
