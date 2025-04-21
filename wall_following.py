from Distance_sensor import Vl53l0x
from Robot import Platform, serial_connection
from sensors.Indication import Indicator
import time
from dropper import Dropper


indicator = Indicator(7)
left_sensorf = Vl53l0x(5, 130)
right_sensorf = Vl53l0x(2, 20)
left_sensor = Vl53l0x(4, 60)
right_sensor = Vl53l0x(3, 40)
front_sensor = Vl53l0x(6, 30)
robot = Platform()
dropper = Dropper()

indicator.set_color(255,255,255)
time.sleep(1)
indicator.off()
# time.sleep(5)
# while 1:
#     print(left_sensor.get_distance())

encode = 0
last_enc1 = 0
last_enc2 = 0
last_enc3 = 0
last_enc4 = 0
def update_enc():
    # global  encode
    global last_enc1
    global last_enc2
    global last_enc3
    global last_enc4

    delta_enc_tek = 0
    delta_enc_sum = 0

    try:
        count = 0
        enc1 = serial_connection.get_present_position(5)
        enc2 = serial_connection.get_present_position(4)
        enc3 = serial_connection.get_present_position(9)
        enc4 = serial_connection.get_present_position(18)
        # if((enc1-last_enc1>0) and (enc1-last_enc1)<300):
        #     encode+= (enc1 - last_enc1)
        #     last_enc1 = enc1
        # if ((enc2 - last_enc2> 0) and (enc2- last_enc2) < 300):
        #     encode += (enc2 - last_enc2)
        #     last_enc2 = enc2
        # if ((enc3 - last_enc3 > 0) and (enc3 - last_enc3) < 300):
        #     encode += (enc3 - last_enc3)
        #     last_enc3 = enc3
        # if ((enc4 - last_enc4 > 0) and (enc4 - last_enc4) < 300):
        #     encode += (enc4 - last_enc4)
        #     last_enc4 = enc4

        # print(f"\n enc_1:{enc1} last1:{last_enc1} | enc_2:{enc2} last2:{last_enc2} |  enc_3:{enc3} last3:{last_enc3} |  enc_4:{enc4} last4:{last_enc4} \n ")

        delta_enc_tek = abs(enc1-last_enc1)
        if (enc1 >= 0) and (enc1 < 1024):
            last_enc1 = enc1
            count += 1
        else:
            delta_enc_tek = 0
        if (delta_enc_tek < 400):
            delta_enc_sum += delta_enc_tek
        # print(f"delta_tek:{delta_enc_tek} delta_sum:{delta_enc_sum}")

        delta_enc_tek = abs(enc2-last_enc2)
        if (enc2 >= 0) and (enc2 < 1024):
            last_enc2 = enc2
            count += 1
        else:
            delta_enc_tek = 0
        if (delta_enc_tek < 400):
            delta_enc_sum += delta_enc_tek
        print(f"delta_tek:{delta_enc_tek} delta_sum:{delta_enc_sum}")

        delta_enc_tek = abs(enc3-last_enc3)
        if (enc3 >= 0) and (enc3 < 1024):
            last_enc3 = enc3
            count += 1
        else:
            delta_enc_tek = 0
        if (delta_enc_tek < 400):
            delta_enc_sum += delta_enc_tek
        print(f"delta_tek:{delta_enc_tek} delta_sum:{delta_enc_sum}")

        delta_enc_tek = abs(enc4-last_enc4)
        if (enc4 >= 0) and (enc4 < 400):
            last_enc4 = enc4
            count += 1
        else:
            delta_enc_tek = 0
        if (delta_enc_tek < 100):
            delta_enc_sum += delta_enc_tek
        # print(f"delta_tek:{delta_enc_tek} delta_sum:{delta_enc_sum}")

        # print(f"\n encode:{delta_enc_sum} \n")
    except:
        print("update enc err")
        delta_enc_sum+=0
    try:
        return(delta_enc_sum/count)
    except:
        return 0

# #
# while(1):
#     print(front_sensor.get_distance())
# while(1):
#     print(f"l = {left_sensor.get_distance()}, r = {right_sensor.get_distance() }")


def wall_following_two(speed = 550, kn=1.3, kd = 1.5, last_delta= [0]):
    try:
        left_distance = left_sensorf.get_distance()
        if left_distance > 100:
            left_distance = 50

        right_distance =right_sensorf.get_distance()
        if right_distance > 100:
            right_distance = 50

        delta = left_distance - right_distance
        up = int(delta * kn + (delta - last_delta[0])*kd)
        # print(up)
        last_delta[0] = delta
        robot.go(speed - up, speed + up)
    except:
        print("err")


def wall_following_until_distance(distance, speed=450,kn=2.7, kd = 1):
    start_distance = front_sensor.get_distance()
    while front_sensor.get_distance() > distance:
        wall_following_two(speed, kn, kd)
    robot.go(0, 0)


def straight():
    encode = 0
    while encode<650:
        _time = time.time()
        wall_following_two()
        encode += update_enc()
        # print("encode :", encode)
        delta_time = time.time()-_time
        print(f"time: {delta_time}")
    robot.go(0,0)




