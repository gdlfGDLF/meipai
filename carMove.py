from picamera2 import Picamera2
import cv2
from pynput import keyboard  # 替代keyboard库
import time
import RPi.GPIO as GPIO

# 初始化GPIO（BOARD编号模式）
GPIO.setmode(GPIO.BOARD)

# ===== 电机控制引脚（L298N）=====
IN1 = 11  # 左轮方向1
IN2 = 12  # 左轮方向2
IN3 = 13  # 右轮方向1
IN4 = 15  # 右轮方向2

# 设置GPIO为输出
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# ===== 舵机控制引脚（预留）=====
SERVO_PIN = 16  # 舵机信号线接GPIO16
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz PWM
servo_pwm.start(0)

def set_servo_angle(angle):
    """控制舵机角度（0~180°）"""
    duty = angle / 18 + 2  # 角度转占空比
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)
    servo_pwm.ChangeDutyCycle(0)  # 防止舵机抖动

# ===== 电机控制函数 =====
def stop_motors():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

def forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def backward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

def turn_left():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def turn_right():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

# ===== 键盘监听回调 =====
def on_press(key):
    try:
        if key.char == 'w':
            forward()
            print("前进")
        elif key.char == 's':
            backward()
            print("后退")
        elif key.char == 'a':
            turn_left()
            print("左转")
        elif key.char == 'd':
            turn_right()
            print("右转")
        elif key.char == ' ':
            stop_motors()
            print("停止")
        elif key.char == '1':
            set_servo_angle(45)
        elif key.char == '2':
            set_servo_angle(90)
        elif key.char == '3':
            set_servo_angle(135)
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:  # 按ESC退出
        return False

# ===== 初始化摄像头 =====
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "BGR888"})
picam2.configure(config)
picam2.start()

# 启动键盘监听
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

try:
    print("WASD 控制小车，ESC 退出")
    while listener.is_alive():  # 当监听器运行时保持循环
        # 获取摄像头帧
        frame = picam2.capture_array()
        
        # 显示画面
        cv2.imshow("Camera", frame)
        
        # 检测OpenCV退出键
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("程序被用户中断")

finally:
    # 释放资源
    stop_motors()
    servo_pwm.stop()
    listener.stop()  # 停止键盘监听
    picam2.stop()
    cv2.destroyAllWindows()
    GPIO.cleanup()
    print("程序结束")
