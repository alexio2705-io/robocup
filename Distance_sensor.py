from sensors.multiplexor import PCA9547
import busio
import adafruit_vl53l0x

import time

i2c = busio.I2C(3, 2)
hat = PCA9547()
# time.sleep(1)
hat.setChannel(4)

print(f"sens i2c init {i2c}")

sensor = adafruit_vl53l0x.VL53L0X(i2c)


def find_median(arr):
    arr.sort()
    n = len(arr)

    
    if n % 2 == 0:
        median = (arr[n // 2 - 1] + arr[n // 2]) / 2
    else:  
        median = arr[n // 2]
    
    return median


class Vl53l0x:
    def __init__(self, channel_number, adjustment):
        self.channal_number = channel_number
        self.adjustment = adjustment
    
    def get_distance(self):
        raw_distance = []
        try:
            hat.setChannel(self.channal_number)
        except:
            print("miltipexer not accessed")
        try:    
            sensor = adafruit_vl53l0x.VL53L0X(i2c)
            for i in range(3):
                raw_distance.append(sensor.range - self.adjustment)
        except:
            raw_distance.append(0)
            print(f"i2c sensor adr:{self.channal_number} error")
        
        return find_median(raw_distance)




