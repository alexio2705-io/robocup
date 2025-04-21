
from robo_platform import Platform
import time


class Nagigator:
    def __init__(self):
        self.robo = Platform()
        self.comand_state = 0
        self.cmd_code = 0
        
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        pass

    def  nav_set_warning (self, code:int = 0):
        # if self.is_dropped[i] == 0:
            self. robo.set_detected_warning(code)
            # обнулением внутри robo
            # self.is_dropped[i] = 1

    def set_orientation(self, yaw:float = 0, pitch:float = 0, roll:float = 0):
        self.robo.update_orintation(yaw, pitch, roll)
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll
        pass

    def set_distance(self, left_distance:float = 0, right_distance:float = 0, front_distance:float = 0, front_left_distance:float = 0, front_right_distance:float = 0):
        self.robo.update_distance(left_distance, right_distance, front_distance)
        pass

    # здесь делаем начальные уставоки
    def nav_start(self):
        self.cmd_code = 1
        self.robo.start_light()
        pass

    # здесь пишем сам алгоритм
    def nav_step(self):
        match self.cmd_code:
            case 0:
                pass
            case 1:
                self.cmd_code =3
                self.robo.straight(delta_encode = -1)
            case 2:
                self.robo.stop()
            case 3:
                cmd_status = self.robo.straight()
                if cmd_status > 0:
                    self.robo.stop()
                    self.cmd_code = 4
                    # устанавливаем начальное пожение для поворота
                    self.robo.set_start_position(self.yaw, self.pitch, self.roll)
            case 4:
                cmd_status = self.robo.turn_selection()
                if cmd_status >0:
                    self.robo.stop()
                    self.cmd_code = 3
                    # обнуляем локальные пкркненый в sraight
                    self.robo.straight(delta_encode = -1)
                    
            case _:
                self.cmd_code = 0
        
                
                
    
    # здесь останвливаем движение
    def nav_stop(self):
        self.cmd_code = 2
        self.robo.disco_light()
        pass
