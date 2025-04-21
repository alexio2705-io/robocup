
from pyax12.connection import Connection
import math
import time
# from sensors.gyro import gyro
# from sensors.Distance_sensor import Vl53l0x

# serial_connection = Connection(port="/dev/ttyAMA0", baudrate=1000000)
# gy25 = gyro()
# gy25.calibrate()

from sensors.Indication import Indicator 
    

class Platform:
    def __init__(self, lb_dynamixel_id=4,lf_dynamixel_id=10, rb_dynamixel_id=5, rf_dynamixel_id=18, wheel_diameter=70):
        self.lb_dynamixel_id = lb_dynamixel_id
        self.lf_dynamixel_id = lf_dynamixel_id
        self.rb_dynamixel_id = rb_dynamixel_id
        self.rf_dynamixel_id = rf_dynamixel_id
        self.wheel_diameter = wheel_diameter
        
        
        self.last_enc_lb = 0
        self.last_enc_lf = 0
        self.last_enc_rb = 0
        self.last_enc_rf = 0
        
        self.encode = 0
        
        self.left_distance = 0
        self.right_distance = 0

        self.front_distance = 0

        self.front_left_distance = 0
        self.front_right_distance = 0

        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        
        self.start_Yaw = 0
        self.start_Pitch = 0
        self.start_Roll = 0
        
        self.is_complete = -1
        
        self.indicator = Indicator(7)

        
        self.serial_connection = Connection(port="/dev/ttyAMA0", baudrate=1000000)
        self.serial_connection.set_ccw_angle_limit(9, 150, degrees=True)
        self.serial_connection.set_cw_angle_limit(9, -150, degrees=True)
        self.start_pos = self.serial_connection.get_present_position(9, degrees=True)
        
        self.cubes =  [1] * 12 + [0]
        
        self.detected = 0
    
    def set_warning(self, warn_detected:int = 0):
        self.detected = warn_detected
        
        
    # вызываем одинажды при старте маневра    
    def set_start_position(self, yaw:float = 0, pitch:float = 0, roll:float = 0):
        self.start_Yaw = yaw
        self.start_Pitch = pitch
        self.start_Roll = roll
        
        # задано начальное положение
        self.is_complete = -1
        
    # вызываем каждый шаг            
    def update_orintation(self, yaw:float = 0, pitch:float = 0, roll:float = 0):
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll
                
    # вызываем каждый шаг            
    def update_distance(self, left_distance:float = 0, right_distance:float = 0, front_distance:float = 0):
        self.left_distance = left_distance
        self.right_distance = right_distance

        self.front_distance = front_distance

        self.front_left_distance = 0
        self.front_right_distance = 0
               
    
    def go(self, left_speed=200, right_speed=200):
        # a = time.time()
        if left_speed < 0:
            left_speed = 1024+abs(left_speed)
        
        if right_speed > 0:
            right_speed = 1024+abs(right_speed)
        if right_speed < 0:
            right_speed = abs(right_speed)
        try:
            self.serial_connection.set_speed(self.rf_dynamixel_id , max(0, min(right_speed, 2047)))
            # time.sleep(0.002)
            self.serial_connection.set_speed(self.rb_dynamixel_id , max(0, min(right_speed, 2047)))
            # time.sleep(0.002)
            self.serial_connection.set_speed(self.lf_dynamixel_id , max(0, min(left_speed, 2047)))
            # time.sleep(0.002)
            self.serial_connection.set_speed(self.lb_dynamixel_id , max(0, min(left_speed, 2047)))
        except:
            print("go err")
        # print(time.time()-a)
        
    # вызываем каждый шаг
    def turn_to( self,  yaw_dest:float = 0, pitch_dest:float = 0, roll_dest:float = 0, speed:int = 300):
        
        # turn = yaw_pos - self.start_Yaw

#         turn = self.yaw - self.start_Yaw

        turn = yaw_dest + self.yaw

        if abs(turn) > 180:
            turn = turn - math.copysign(360., turn)
        
        print(f" turn_to {turn}")
        
        if abs(turn) < 1:
            self.is_complete = 1
        # else:        
        #     if turn <= 0:
        #         self.go(speed, -speed)
        #     else:
        #         self.go(-speed, speed)

        # while abs(turn) > 1:
        #     time.sleep(0.05)

        #     pos_data = self.gy25.get_last_measure()

        #     if (len(pos_data)<1):
        #         continue

        #     tek_yaw = pos_data[0]

        #     turn = yaw_pos - tek_yaw

        #     if abs(turn) > 180:
        #         turn = turn - math.copysign(360., turn)


            # print(tek_yaw, turn)
            
            
        # =1 завершили поворот, останавливаем моторы
        if self.is_complete == 1:
            self.go(0,0)
            print('ready')
        # =-1 однократно задаем скорость моторам
        # и переводим состояние в 0    
        elif self.is_complete < 0:
            if turn <= 0:
                self.go(speed, -speed)
            else:
                self.go(-speed, speed)
                
            self.is_complete = 0    

        print(f" turn_to is_complete {self.is_complete}")        

        return self.is_complete


    def turn(self, turn_Yaw, speed=300):

        print('turn')
       
        # start_Yaw = self.yaw
        # print(start_Yaw)
       
        turn = self.start_Yaw + turn_Yaw
        print(turn)
       
        if abs(turn) > 180:
             turn = turn - math.copysign(360., turn)

        print(turn)

        is_complete_loc = self.turn_to(yaw_dest = turn, pitch_dest = 0, roll_dest = 0)
        
        if is_complete_loc > 0:
            self.go(0,0)
 
        print(f"turn is_complete_loc {is_complete_loc}")
 
        return is_complete_loc

    def update_enc(self):
            count = 0
            delta_enc_tek = 0
            delta_enc_sum = 0 
        
#         try:
        
            enc_lb = self.serial_connection.get_present_position(self.lb_dynamixel_id)
            enc_lf = self.serial_connection.get_present_position(self.lf_dynamixel_id)
            enc_rb = self.serial_connection.get_present_position(self.rb_dynamixel_id)
            enc_rf = self.serial_connection.get_present_position(self.rf_dynamixel_id)
            
            delta_enc_tek = abs(enc_lb - self.last_enc_lb)
            if (enc_lb >= 0) and (enc_lb < 1024):
                self.last_enc_lb = enc_lb
                count += 1
            else:
                delta_enc_tek = 0
            if (delta_enc_tek < 400):
                delta_enc_sum += delta_enc_tek
            # print(f"delta_tek:{delta_enc_tek} delta_sum:{delta_enc_sum}")

            delta_enc_tek = abs(enc_lf - self.last_enc_lf)
            if (enc_lf >= 0) and (enc_lf < 1024):
                self.last_enc_lf = enc_lf
                count += 1
            else:
                delta_enc_tek = 0
            if (delta_enc_tek < 400):
                delta_enc_sum += delta_enc_tek
            print(f"delta_tek:{delta_enc_tek} delta_sum:{delta_enc_sum}")

            delta_enc_tek = abs(enc_rb - self.last_enc_rb)
            if (enc_rb >= 0) and (enc_rb < 1024):
                self.last_enc_rb = enc_rb
                count += 1
            else:
                delta_enc_tek = 0
            if (delta_enc_tek < 400):
                delta_enc_sum += delta_enc_tek
            print(f"delta_tek:{delta_enc_tek} delta_sum:{delta_enc_sum}")

            delta_enc_tek = abs(enc_rf - self.last_enc_rf)
            if (enc_rf >= 0) and (enc_rf < 400):
                self.last_enc_rf = enc_rf
                count += 1
            else:
                delta_enc_tek = 0
            if (delta_enc_tek < 100):
                delta_enc_sum += delta_enc_tek             
                     
            # print(f"\n encode:{delta_enc_sum} \n")
#         except:
#             print("update enc err")
            delta_enc_sum+=0
            if count > 0:
                delta_enc_sum /= count
            else:
                delta_enc_sum = 0
        
            return delta_enc_sum                                 

    def wall_following_two(self, speed = 550, kn=1.3, kd = 1.5, last_delta= [0]):
        try:
            left_distance = self.left_distance       #left_sensorf.get_distance()
            if left_distance > 100:
                left_distance = 50

            right_distance = self.right_distance       #right_sensorf.get_distance()
            if right_distance > 100:
                right_distance = 50

            delta = left_distance - right_distance
            up = int(delta * kn + (delta - last_delta[0])*kd)
            # print(up)
            last_delta[0] = delta
            self.go(speed - up, speed + up)
        except:
            print("err")
        pass

    def wall_following_until_distance(self, distance, speed=450,kn=2.7, kd = 1):

        # start_distance =  front_sensor.get_distance()
        # while front_sensor.get_distance() > distance:
        #     wall_following_two(speed, kn, kd)
        # self.go(0, 0)
        self.is_complete = 0    
        if self.front_distance > distance:
            self.wall_following_two(speed, kn, kd)
        else:
            self.go(0, 0)
            self.is_complete = 1 
                
        return (self.is_complete)

    def wall_go(self, speed=200, kn=0.2, kd=2):
        pass
    

    def wall_go_left(self, speed=200, kn=0.2, kd=2):
        pass


    def wall_go_right(self, speed=200, kn=0.2, kd=2):
        pass

    def drop_left(self):

        index = self.cubes.index(1) 
        if index == -1:
            return
        print(index)
        self.serial_connection.goto(9, min(150, self.start_pos + 12   + 13 * (1+index)), 900, degrees=True)
        time.sleep(0.5 +0.5*index)
        self.serial_connection.goto(9, self.start_pos, 200, degrees=True)

        self.cubes[index] = 0


    def drop_right(self):

        index = len(self.cubes) - self.cubes[::-1].index(1) - 1
        if index == -1:
            return
        print(self.start_pos - 13.47 * (13-index))
        self.serial_connection.goto(9, max(self.start_pos - 13.82 * (12-index),-150), 900, True)
        time.sleep(0.5*(13-index))
        self.serial_connection.goto(9, self.start_pos, 200, degrees=True)
        self.cubes[index] = 0

    def start_light(self):

        self.indicator.set_color_white()
        time.sleep(0.2)
         
        self.indicator.off() 
        
    def disco_light(self):
        self.indicator.set_color_red()
        time.sleep(0.2)

        self.indicator.set_color_blue()
        time.sleep(0.2)

        self.indicator.set_color_green()
        time.sleep(0.2)
         
        self.indicator.off() 
        
        
        
    def drop(self):
        if self.detected == -2:
            self.indicator.set_color_red()
            for i in range(2):
                self.drop_left()
            self.indicator.off()
        elif self.detected == -1:
            self.indicator.set_color_orange()
            for i in range(1):
                self.drop_left()
            self.indicator.off()
        elif self.detected in (3, -3):
            self.indicator.set_color_green()
            time.sleep(0.3)
            self.indicator.off()
                    
        if self.detected == 2:
            self.indicator.set_color_red()
            for i in range(2):
                 self.drop_right()
            self.indicator.off()
        elif self.detected == -1:
            self.indicator.set_color_orange()
            for i in range(1):
                self.drop_right()
            self.indicator.off()
 
    
    
    # delta_encode < 0 - задаем начальные условия
    def straight(self, delta_encode:int = 650):
        
        if delta_encode < 0:
            self.encode = 0
            self.is_complete = -1
        else:
            self.is_complete = 0
            if self.encode < delta_encode:
                loc_time = time.time()
                self.wall_following_two()      
                self.encode += self.update_enc()
                if self.detected != 0:
                    self.drop()
                    self.detected = 0
                # print("encode :", encode)
                delta_time = time.time()-loc_time
                print(f"time: {delta_time}")
            else:    
                self.go(0,0)
                self.is_complete = 1
            
        # while encode<delta_encode:
        #     loc_time = time.time()
        #     self.wall_following_two()
        #     encode += self.update_enc()
        #     # print("encode :", encode)
        #     delta_time = time.time()-loc_time
        #     print(f"time: {delta_time}")
        # self.go(0,0)
        
        return self.is_complete
    
    def turn_selection(self):
        if(self.right_distance > 150):
            self.is_complete = self.turn(-85)
        elif(self.front_distance >150):
            pass
        elif(self.left_distance > 150):
            self.is_complete = self.turn(85)
        else:
            self.is_complete = self.turn(180)
            
        return self.is_complete   
            
            
    def stop(self):
 
        try:
            self.go(0,0)
            self.is_complete = 1
        except:
            self.is_complete = -1
            
        return self.is_complete
    

       

        
 
#
    
    
