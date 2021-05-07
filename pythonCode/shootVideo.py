# -*- coding: UTF-8 -
from picamera import PiCamera
import RPi.GPIO as GPIO
import time
import sys
import os
shutter_button_id = 20
quit_button_id = 21
path = './'
store_folder = 'video'
resolution = (1920, 1080)  # 分辨率
fps = 30  # 帧率


def main():
    global path, resolution
    shutter_speed = 16667  # 快门速度 单位微妙
    GPIO.setmode(GPIO.BCM)  # 设置GPIO的模式
    GPIO.setup(shutter_button_id, GPIO.IN,
               pull_up_down=GPIO.PUD_UP)  # 设置快门按键的GPIO引脚
    GPIO.setup(quit_button_id, GPIO.IN,
               pull_up_down=GPIO.PUD_UP)  # 设置退出按键的GPIO引脚

    camera = PiCamera()
    camera.shutter_speed = shutter_speed  # 设置快门速度
    camera.exposure_mode = 'auto'  # 设置自动曝光

    camera.resolution = resolution  # 设置视频分辨率
    GPIO.add_event_detect(quit_button_id, GPIO.RISING,
                          callback=quitButtonEvent)  # 为按键设置中断
    mkdir(path)
    try:
        while True:
            loop(camera)
    except KeyboardInterrupt:
        camera.stop_recording()
        camera.stop_preview()
        GPIO.cleanup()


def loop(camera):
    """
    循环执行的函数
    """
    global shutter_button_id, quit_button_id
    global path, store_folder
    # camera.start_preview(fullscreen=True)  # 设置窗口预览
    camera.start_preview(fullscreen=False, window=(0, -100, 720, 540))  # 设置窗口预览
    camera.video_stabilization = True  # 视频稳定
    if GPIO.wait_for_edge(shutter_button_id, GPIO.RISING):
        print("start recording...")
        fileName = searchFile(path+store_folder)
        print('file name:'+fileName)
        camera.start_recording(path+store_folder+'/'+fileName+'.h264')
    time.sleep(0.5)
    if GPIO.wait_for_edge(shutter_button_id, GPIO.RISING):
        camera.stop_recording()
        print("stop recording")
    state = tranH264ToMp4(fileName, path+store_folder)
    if state:
        try:
            temp = path+store_folder+'/'+fileName+'.h264'
            os.remove(temp)
        except:
            print(fileName+'.h264 is not found')
    camera.stop_preview()
    time.sleep(0.5)


def tranH264ToMp4(file_name, path):
    """
    封装h264视频为mp4，需要安装MP4Box
    使用以下命令安装
    sudo apt-get install gpac
    """
    global fps
    h264_flie_path = path+'/'+file_name+'.h264'
    mp4_file_path = path+'/'+file_name+'.mp4'
    command = 'MP4Box -fps '+str(fps)+' -add '+h264_flie_path+' '+mp4_file_path
    state = os.system(command)
    print(command)
    if not state:
        return True
    else:
        return False


def quitButtonEvent(a):
    """
    退出中断的回调函数
    """
    GPIO.cleanup()
    sys.exit(0)


def mkdir(path):
    """
    判断video文件夹是否存在
    如不存在则创建新的文件夹
    """
    video_path = path+'video'
    if not os.path.exists(video_path):
        print("create video")
        os.mkdir(video_path)
        return True
    else:
        print("folder is existing")
        return False


def searchFile(path):
    """
    遍历文件夹并返回未重复出现的文件名
    """
    index = 1
    clipName = 'clip%03d' % index
    while os.path.exists(path+'/'+clipName+'.h264'):
        index += 1
        clipName = 'clip%03d' % index
    return clipName


if __name__ == "__main__":
    main()
