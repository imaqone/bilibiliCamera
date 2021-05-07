# -*- coding: UTF-8 -
from picamera import PiCamera
import RPi.GPIO as GPIO
import time
import sys
import os
shutter_button_id = 20
quit_button_id = 21
path = './'
store_folder = 'photo'


def main():
    ISO = 300  # 100-800整型
    shutter_speed = 125000  # 快门速度 单位微妙
    auto_exposure_flag = True  # 设置是否自动曝光
    GPIO.setmode(GPIO.BCM)  # 设置GPIO的模式
    GPIO.setup(shutter_button_id, GPIO.IN,
               pull_up_down=GPIO.PUD_UP)  # 设置快门按键的GPIO引脚
    GPIO.setup(quit_button_id, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    camera = PiCamera()
    camera.resolution = (4056, 3040)  # 设置拍照分辨率 最高4056*3040
    if auto_exposure_flag:
        camera.exposure_mode = 'auto'  # 设置自动曝光
        camera.meter_mode = 'average'  # 设置测光模式为平均
    else:
        camera.exposure_mode = 'off'  # 关闭自动曝光
        camera.iso = ISO
        camera.shutter_speed = shutter_speed
    camera.awb_mode = 'auto'  # 设置自动白平衡
    # camera.exposure_compensation = 0 #设置曝光补偿 (-25 to 25)
    camera.start_preview(fullscreen=False, window=(0, 0, 640, 480))  # 设置窗口预览
    camera.video_stabilization=True
    GPIO.add_event_detect(quit_button_id, GPIO.RISING,
                          callback=quitButtonEvent)  # 为按键设置中断
    mkdir(path)
    try:
        while True:
            loop(camera)
    except KeyboardInterrupt:
        camera.stop_preview()
        GPIO.cleanup()


def mkdir(path):
    """
    判断photo文件夹是否存在
    如不存在则创建新的文件夹
    """
    photo_path = path+'photo'
    if not os.path.exists(photo_path):
        print("create photo")
        os.mkdir(photo_path)
        return True
    else:
        # print("folder is existing")
        return False


def loop(camera):
    """
    循环执行的函数
    """
    fileName = searchFile(path+store_folder)
    if GPIO.wait_for_edge(shutter_button_id, GPIO.RISING):
        print("press")
        camera.capture(path+store_folder+'/'+fileName+'.jpg')
    time.sleep(0.5)


def quitButtonEvent(a):
    """
    退出中断的回调函数
    """
    GPIO.cleanup()
    sys.exit(0)


def searchFile(path):
    """
    遍历文件夹并返回未重复出现的文件名
    """
    index = 1
    imageName = 'image%03d' % index
    while os.path.exists(path+'/'+imageName+'.jpg'):
        index += 1
        imageName = 'image%03d' % index
    return imageName


if __name__ == "__main__":
    main()
