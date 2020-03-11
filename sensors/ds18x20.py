# DS18x20 temperature sensor driver for MicroPython.
# MIT license; Copyright (c) 2016 Damien P. George

# https://raw.githubusercontent.com/micropython/micropython/v1.11/drivers/onewire/ds18x20.py
# Didi Lamken 20.02.2020

from micropython import const
import binascii

_CONVERT = const(0x44)
_RD_SCRATCH = const(0xbe)
_WR_SCRATCH = const(0x4e)

class DS18X20:
    def __init__(self, onewire):
        print("init -> DS18B20")
        self.ow = onewire
        self.buf = bytearray(9)
        self.roms = self.scan()

    def scan(self):
        self.roms = [rom for rom in self.ow.scan() if rom[0] == 0x10 or rom[0] == 0x28]
        return self.roms

    def convert_temp(self):
        self.ow.reset(True)
        self.ow.writebyte(self.ow.SKIP_ROM)
        self.ow.writebyte(_CONVERT)

    def read_scratch(self, rom):
        self.ow.reset(True)
        self.ow.select_rom(rom)
        self.ow.writebyte(_RD_SCRATCH)
        self.ow.readinto(self.buf)
        if self.ow.crc8(self.buf):
            raise Exception('CRC error')
        return self.buf

    def write_scratch(self, rom, buf):
        self.ow.reset(True)
        self.ow.select_rom(rom)
        self.ow.writebyte(_WR_SCRATCH)
        self.ow.write(buf)

# modifiziert  02.2020 Diren Senger
    def read_temp(self, rom):
        try:
            buf = self.read_scratch(rom)
            if rom[0] == 0x10:
                if buf[1]:
                    t = buf[0] >> 1 | 0x80
                    t = -((~t + 1) & 0xff)
                else:
                    t = buf[0] >> 1
                return t - 0.25 + (buf[7] - buf[6]) / buf[7]
            elif rom[0] in (0x22, 0x28):
                t = buf[1] << 8 | buf[0]
                if t & 0x8000: # sign bit set
                    t = -((t ^ 0xffff) + 1)
                return t / 16
            else:
                return None
        except AssertionError:
            return None

# modifiziert 20.02.2020 Didi Lamken
    def read_all(self, ds_positions=None):
        roms = self.roms
        data = {}
        for rom in roms:
            name = binascii.hexlify(rom).decode('utf-8')
            try:
                tmp = self.read_temp(rom)
                ds18b20tmp = round(tmp, 2)
            except:
                print("CRC-Err", end = ' ')
                # ds18b20tmp =  '99.9'
                continue
            print(ds18b20tmp, end=' ')
            if ds_positions:
                if name in ds_positions:
                    data[ds_positions[name]] = ds18b20tmp
            else:
                data[name] = ds18b20tmp
        print( ' Sensors:', len(roms) )
        return data
