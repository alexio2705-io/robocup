
import multiprocessing as mp
import time
import math

camera_msg = {'id':'camera', 'time':0, 'cam_pos':'left', 'state':-1 , 'text':'x_x'}

def get_paddle_text_origin(pdl,img_source):
    
    res_text = {}
    
    # распознаем текст с оригинального изображения 
    start_time = time.time()
    result = pdl.ocr(img_source)
    if result[0]:
        text = result[0][0][-1]
    else:
        text = ('no', 0.0)
    end_time = time.time()
    elapsed_time = (end_time - start_time)*1000.
    # print(f"origilal, text: {text}, time_ms {elapsed_time}") 
    res_text["text"] = text
    res_text["time"] = int(elapsed_time)
       
    return res_text



def camera_worker(queue, is_work, num_camera:int =-1):

    import time
    
    print(f"Запуск камеры: {num_camera}")
    camera_start_time = time.time()
    
    if num_camera < 0:
        return
    
    import paddleocr as pocr
    # import cv2
    # import os
    
    from picamera2 import Picamera2, Preview
    from libcamera import Transform
    from picamera2.encoders import H264Encoder
    from picamera2.outputs import FfmpegOutput
    #from pprint import *

    # инициализация камер
    
    camera_msg['state'] = 0
    camera_msg['text'] ='starting'
    
    if num_camera == 0:
        camera_msg['cam_pos'] = "left"
    elif num_camera == 1:
        camera_msg['cam_pos'] = "rigth"
    else:
        camera_msg['cam_pos'] = "unknown"
    camera_msg['time'] = round(time.time() - camera_start_time, 2)            

    queue.put(camera_msg)

    pdl_ocr = pocr.PaddleOCR( lang = 'en')

    time.sleep(1)
    
    robo_camera = Picamera2(num_camera)
    
    modes =robo_camera.sensor_modes

    print(modes)

    
    robo_camera.set_controls({ "Brightness": 0.6, "HdrMode":'MultiExposure'})
    
    camera_transform=Transform(hflip=1, vflip=1)
    
    preview_config = robo_camera.create_preview_configuration( {"size":(1296, 972), 'format': 'BGR888'} , transform=camera_transform )
#     preview_config = robo_camera.create_preview_configuration( {"size":(640, 480), 'format': 'BGR888'} , transform=camera_transform )
    still_config = robo_camera.create_still_configuration( main={"size":(1296, 972), 'format': 'BGR888'} , transform=camera_transform )

    robo_camera.configure( preview_config )

    #camera_control = {"ExposureTime": 10000, "AnalogueGain": 1.0}
    #preview_config.set_controls( camera_control )

    robo_camera.start_preview(Preview.NULL, transform=camera_transform)



    robo_camera.start()

    #robo_camera.capture_file("cam_test.jpg" )
    #robo_camera.stop()  
    #robo_camera.switch_mode_and_capture_file(still_config, "still_cam_test2.jpg")

    #robo_camera.start()

    # robo_camera.configure(robo_camera.create_video_configuration(main={"size": (1280, 720),
    #                                                      "format": "YUV420"}))
    # robo_camera.start_recording(H264Encoder(), output=FfmpegOutput(f"-f rtp udp://192.168.168.110:900{num_camera}"))


    metadata = robo_camera.capture_metadata()
    controls = {c: metadata[c] for c in ["ExposureTime", "AnalogueGain", "ColourGains"]}
    print(controls)

    robo_camera.capture_file(f"{camera_msg['cam_pos']}_cam_img.jpg" )
    #robo_camera.switch_mode_and_capture_file(still_config, "cam_test2.jpg")

    #robo_camera.start()


    camera_msg['state'] = 1
    camera_msg['text'] =''
    camera_msg['time'] = round(time.time() - camera_start_time, 2)             

    queue.put(camera_msg)

    # обработка изображения с камер
    while is_work.value > 1:
        
        img_src = robo_camera.capture_array()
        
        print(f"size: {img_src.shape}")
    
        ocr_result = get_paddle_text_origin(pdl=pdl_ocr, img_source=img_src)
    
        print(ocr_result)

        camera_msg['text'] = ocr_result['text'][0]
        camera_msg['time'] = round(time.time() - camera_start_time, 2)            
        queue.put(camera_msg)
        
        time.sleep(0.1)

    robo_camera.stop()

    camera_msg['state'] = 2
    camera_msg['text'] ='stoped'
    camera_msg['time'] = round(time.time() - camera_start_time, 2)            

    queue.put(camera_msg)

    print(f"Завешение камеры: {num_camera}")


def detect_markers(txt:list):
    etalon_leter = ['S', 'H', 'X']
    
    danger_level:int = 0 #  

#     danger_level:int = -1 #  
#     danger_level:int = -2 #
    
#     danger_level:int = 1 #  
#     danger_level:int = 2 #  
    
    return danger_level



#  обработка мотров и гланый  управляющий процесс
def sens_motor_worker(queue, is_work):
    print("Запуск моторов")
    print("Запуск датчиков")
    
    motor_star_time = time.time()

    pin_btn_left = 23
    pin_btn_left_centr = 24
    
    pin_btn_right_centr = 8
    pin_btn_right = 7
    

    from sensors.gyro import gyro
#     from sensors.light_sens import ligth

    try:
        from Distance_sensor import Vl53l0x

        left_sensor = Vl53l0x(4, 60)
        right_sensor = Vl53l0x(3, 40)
        front_sensor = Vl53l0x(6, 30) 
        front_left_sensor = Vl53l0x(1, 130)
        front_right_sensor = Vl53l0x(2, 20)
    except:
        print("ERROR INI Sens Vl53l0x")
        pass


    import gpiod

    # from pyax12.connection import Connection 
    # from sensors.Indication import Indicator 
    
    # from robo_platform import Platform 
    from navigation import Nagigator 
    
    nav = Nagigator() 

#     bottom_light = light()

#     chip = gpiod.Chip('gpiochip4')
    
#    btn_left = chip.get_line(pin_btn_left)
#     btn_left.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
    
#     btn_left_centr = chip.get_line(pin_btn_left_centr)
#     btn_left_centr.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
    
#     btn_right_centr = chip.get_line(pin_btn_right_centr)
#     btn_right_centr.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
    
#     btn_right = chip.get_line(pin_btn_right)
#     btn_right.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
    
    gy25 = gyro()
    
    # калибровка датчиков
    gy25.calibrate()
    
    # обработка датчиков
    
    gy25.start_measure()

    tek_Yaw:float = 0.
    tek_Pitch:float = 0.
    tek_Roll: float = 0.


    work_time = 0
    
    cameras_text = []
    
    nav.nav_start()

    while is_work.value > 0:

       	while not queue.empty():
            item = queue.get()
            # print(f"\n msg id : {item['id']} " )
            print(item)
            
            match item['id']:
                    
                case 'camera':
                    print(f"{item['cam_pos']} camera")
                    if item['cam_pos'] == 'left':
                        cameras_text.insert(0,item['text'])
                    if item['cam_pos'] == 'right':
                        cameras_text.insert(1,item['text'])
                case _ :
                    print("неизвестное сообщение")        

        # print("Данные успешно прочитаны из очереди")

        # читаем датчики

        try:
            f_distance = front_sensor.get_distance()
        except:
            f_distance = 8000
            print{"f_distance error"}
        
        try:
            l_distance = left_sensor.get_distance()
        except:
            l_distance = 8000
            print{"l_distance error"}
                
        try:
            r_distance = right_sensor.get_distance()
        except:
            r_distance = 8000
            print{"r_distance error"}

               
        try:
            fl_distance = front_left_sensor.get_distance()
        except:
            fl_distance = 8000
            print{"fl_distance error"}

        try:    
            fr_distance = front_right_sensor.get_distance()
        except:
            fr_distance = 8000
            print{"fr_distance error"}

        nav.set_distance(left_distance = l_distance, right_distance = r_distance,
                         front_distance = f_distance,
                         front_left_distance = fl_distance, front_right_distance = fr_distance)


        
        # try:    
        #     pos_data = gy25.get_last_measure()
        # except:
        #     pos_data = (-1, -1, -1)
            
        # tek_Yaw = pos_data[0] 
        # tek_Pitch = pos_data[1] 
        # tek_Roll = pos_data[2]  

        try:    
            tek_Yaw, tek_Pitch, tek_Roll = gy25.get_last_measure()
        except:
            tek_Yaw, tek_Pitch, tek_Roll = (-1, -1, -1)
            print{"gy25 error"}
            
        nav.set_orientation(yaw = tek_Yaw, pitch = tek_Pitch, roll = tek_Roll)


        # light_lux = bottom_light.get_lux() 
        # light_temp = bottom_light.get_temp() 
        # light_rgb = bottom_light.get_rgb()
        
#         btn_list = []
#         btn_value =  btn_left.get_value()
#         btn_list.append(btn_value)
#          
#         btn_value =  btn_left_centr.get_value() 
#         btn_list.append(btn_value)
#          
#         btn_value =  btn_right_centr.get_value() 
#         btn_list.append(btn_value)
#          
#         btn_value =  btn_right.get_value()
#         btn_list.append(btn_value)
#          
#         sensor_msg['btns'] = btn_list

         


               
        # передаем уровееь опасности в клетке 
        warn_lvl = detect_markers(cameras_text) 
        
        if abs(warn_lvl) != 0:
            nav.nav_set_warning(warn_lvl)
            print(warn_lvl)           

        #логика одного шага
        nav.nav_step()

        # даем системным процессам поработать
        time.sleep(0.040)

        #  очищаем обработанный текст от камер
        cameras_text.clear()
        
        work_time = time.time() - motor_star_time
        
        #  для работы в лабириринте увеличить время до 700
        if work_time > 30:
            
            if is_work.value < 2:
                # выключаемся сами
                is_work.value = 0
            else:
                # завершаем другие процессы 
                # и делаем обработку финальных сообщений
                is_work.value = 1

                # даем всем процессам завершится
                time.sleep(3)

    nav.nav_stop()

    print( "Завешение моторов" )


if __name__ == '__main__':

    shared_queue = mp.Queue()
    
    manager = mp.Manager()

    
    shared_isWork = manager.Value('i', 0)
    shared_dict = manager.dict()
    
    Processes =[]
    
    # активируем цикл обработки в процессах
    shared_isWork.value = 15
 
    motor_process = mp.Process(target=sens_motor_worker, args=(shared_queue,shared_isWork,))
    Processes.append(motor_process)
    
    # left_camera_process = mp.Process(target=camera_worker, args=(shared_queue,shared_isWork,0,))
    # Processes.append(left_camera_process)
    
    # right_camera_process = mp.Process(target=camera_worker, args=(shared_queue,shared_isWork,1,))
    # Processes.append(right_camera_process)
    
    for proc in Processes:
        proc.start()

    for proc in Processes:
        proc.join()

    # result = read_data(shared_queue)
    # print("Результат из очереди:", result)

    print("все процессы завершены")