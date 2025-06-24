
from picamera2 import Picamera2
import cv2
from pynput import keyboard
import time
import RPi.GPIO as GPIO

# 初始化GPIO
GPIO.setmode(GPIO.BOARD)

# 电机控制引脚
IN1 = 11  # 左轮方向1
IN2 = 12  # 左轮方向2
IN3 = 13  # 右轮方向1
IN4 = 15  # 右轮方向2

# 设置GPIO为输出
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# 舵机控制
SERVO_PIN = 16
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo_pwm = GPIO.PWM(SERVO_PIN, 50)
servo_pwm.start(0)

def set_servo_angle(angle):
    duty = angle / 18 + 2
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)
    servo_pwm.ChangeDutyCycle(0)

# 电机控制函数
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

# 键盘事件处理
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
        elif key.char == '1':
            set_servo_angle(45)
        elif key.char == '2':
            set_servo_angle(90)
        elif key.char == '3':
            set_servo_angle(135)
    except AttributeError:
        pass

def on_release(key):
    stop_motors()
    if key == keyboard.Key.esc:
        return False  # 停止监听

# 初始化摄像头
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "BGR888"})
picam2.configure(config)
picam2.start()

# 启动键盘监听
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

try:
    print("WASD控制方向，松开停止，ESC退出")
    while listener.is_alive():
        frame = picam2.capture_array()
        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    stop_motors()
    servo_pwm.stop()
    listener.stop()
    picam2.stop()
    cv2.destroyAllWindows()
    GPIO.cleanup()
    print("程序结束")
