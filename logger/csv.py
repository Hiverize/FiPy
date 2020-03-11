from machine import SD
import os
import time

class CSV_logger:
    def __init__(self, dir="/sd/hiverizelog"):
        print(dir)
        self.dir = dir
        # Mount SD
        # Pins are Dat0: P8, SCLK: P23, CMD: P4, at least I think so
        # Apparently Pins can not be changed
        sd = SD()
        os.mount(sd, '/sd')

        # Check if directory, eg. hiverizelog, was already created,
        # and create it, if not existing:
        try:
            os.listdir(self.dir)
        except OSError:
            os.mkdir(self.dir)
        print("Init -> CSV logger in directory " +dir)

    def list_files(self, subdir = ""):
        return os.listdir(self.dir +"/" +subdir)

    def read_file(self, file):
        path = "{}/{}".format(self.dir,file)
        print(path)
        f = open(path)
        content = f.read()
        f.close()
        return content

    def remove_file(self, file):
        path = "{}/{}".format(self.dir,file)
        print("trying to remove file" +path)
        try:
            os.remove(path)
            print("Removed file")
        except:
            print("Failed to remove file")



    def get_time_string(self):
        # Get Time
        print("try to get time")
        write_time = time.time()
        print("got time")
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

    def log(self, log_text, dir = "logging"):
        print(log_text)
        time_string, full_time_string = self.get_time_string()
        try:
            os.listdir(self.dir + "/" +dir)
        except OSError:
            os.mkdir(self.dir + "/" +dir)
        # concat filepath
        file_path = self.dir + "/" + dir +"/logging.csv"
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

    def add_dict_lineprotocol(self, data, sensor_key, dir = "influx"):
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

        try:
            os.listdir(self.dir + "/" +dir)
        except OSError:
            os.mkdir(self.dir + "/" +dir)
        # concat filepath
        file_path = self.dir + "/" + dir +"/" +time_string + ".txt"
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

    #Datenfile yyyy-mm-dd.csv mit time, value1, ... value10               """
    def add_data_didi(self, data, plt, cycle, dir ="csv"):
        date_string = self.get_date()
        time_string = self.get_time()
        hour_string = self.get_hour()
        try:
            os.listdir(self.dir + "/" +dir)
        except OSError:
            os.mkdir(self.dir + "/" +dir)
        #file_path = self.dir + "/ + date_string +  "x" + hour_string +  ".csv"
        file_path = self.dir + "/" + dir +"/" + date_string +  ".csv"
        # Get Time
        time_string, full_time_string = self.get_time_string()
        # combine dict entries
        # data_list = ["{},  {},  {}\n".format(full_time_string, key, value) for key, value in data.items()]
        # print('data_list:', data_list)
        full_time_string = date_string + ',  ' + self.get_time()

        test_list = ' '
        test_list = test_list +  str(cycle) + ', '

        test_list = test_list + full_time_string + ',  '
        if 't' in data:
            test_list = test_list +  str(data['t']) + ', '
        else:
            test_list = test_list + ', '
        if 'p' in data:
            test_list = test_list +  str(data['p']) + ', '
        else:
            test_list = test_list + ', '
        if 'h' in data:
            test_list = test_list +  str(data['h']) + ', '
        else:
            test_list = test_list + ', '
        if 'weight_kg' in data:
            test_list = test_list +  str(data['weight_kg']) + ',  '
        else:
            test_list = test_list + ',  '

        if 't_i_1' in data:
            # t1  = data['t_i_1']    # t1s = ("{:5.1f}".format(t1))
            test_list = test_list +  str(data['t_i_1']) + ', '
        else:
            test_list = test_list + ', '
#        print('add_data 3')
        if 't_i_2' in data:
            test_list = test_list +  str(data['t_i_2']) + ', '
        else:
            test_list = test_list + ', '
        if 't_i_3' in data:
            test_list = test_list +  str(data['t_i_3']) + ', '
        else:
            test_list = test_list + ', '
        if 't_i_4' in data:
            test_list = test_list +  str(data['t_i_4']) + ', '
        else:
            test_list = test_list + ', '
        if 't_i_5' in data:
            test_list = test_list +  str(data['t_i_5']) + ', '
        else:
            test_list = test_list + ', '
        if 't_o'   in data:
            test_list = test_list +  str(data['t_o']) + ', '
        else:
            test_list = test_list + ', '

        test_list = test_list     + ' \n'
        print('   SD-Card:', test_list, end = ' ')

        # Write header, if file did not exist before
        try:
            f = open(file_path, 'r')
            f.close()
        except OSError:
            f = open(file_path, 'w')
            f.write('Cycle,,       Time,               BME280,,,               HX711,    DS18B20 \n')
            f.write('Cycle, Date,         Time,        t,     p,        h,       kg,     t1,     t2,     t3,     t4,     t5,     to \n')
            f.close()
            print("   Logging measurements to " + file_path)
        # Append Value
        with open(file_path, 'a') as f:
            # f.write("".join(data_list))
            f.write("".join(test_list))
        print('  Datei:   Daten in {}'.format(file_path))

        # Plotfile für gnuplot yyyy-mm-dd.plt erzeugen
        if plt:
            file_path = self.dir + "/" + date_string +  ".plt"
            try:
                f = open(file_path, 'r')
                f.close()
            except OSError:
                f = open(file_path, 'w')
                # f.write('# Plotfile  2020-02-08.plt am 08.02.2020 um 00:00:00 \n')
                text = '# Plotfile  ' + file_path + ' am ' + self.get_date() + ' ab ' + self.get_time() + ' \n'
                f.write(text)
                text = 'DATAFILE = "' + self.get_date() + '.csv" \n'
                f.write(text)
                text = 'TITLE    = "Messdaten der BOB-Bienenbeute' + ' am ' + self.get_date() + ' ab ' + self.get_time() + '" \n'
                f.write(text)
                f.write('load       "PlotBOB.plt" \n')
                f.write('       \n')
                f.write('# exit \n')
                f.write('pause -1 "Details Gewicht"         \n')
                f.write('set xrange ["10:00:00":"12:00:00"] \n')
                f.write('set yrange [0:10] \n')
                f.write('replot \n')
                f.write('       \n')
                f.write('pause -1 "Details Temperatur"      \n')
                f.write('set xrange ["10:00:00":"12:00:00"] \n')
                f.write('set yrange [15:25] \n')
                f.write('replot \n')
                f.close()
                print("   Logging measurements to " + file_path)
