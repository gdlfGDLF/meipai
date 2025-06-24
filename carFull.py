from picamera2 import Picamera2
import cv2
from pynput import keyboard
import time
import RPi.GPIO as GPIO

# 初始化GPIO（BOARD编号模式）
GPIO.setmode(GPIO.BOARD)

# ===== 电机控制引脚（L298N）=====
IN1 = 11  # 左轮方向1
IN2 = 12  # 左轮方向2
IN3 = 13  # 右轮方向1
IN4 = 15  # 右轮方向2

# 设置GPIO为输出，并初始化为低电平
GPIO.setup(IN1, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(IN2, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(IN3, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(IN4, GPIO.OUT, initial=GPIO.LOW)

# ===== 舵机控制引脚 =====
SERVO_LR = 7   # 左右转向舵机
SERVO_UD = 18  # 上下运动舵机
GPIO.setup(SERVO_LR, GPIO.OUT)
GPIO.setup(SERVO_UD, GPIO.OUT)

# 初始化PWM（50Hz）
servo_lr = GPIO.PWM(SERVO_LR, 50)
servo_ud = GPIO.PWM(SERVO_UD, 50)
servo_lr.start(0)
servo_ud.start(0)

# 舵机初始角度
current_lr_angle = 90  # 左右舵机初始居中
current_ud_angle = 90  # 上下舵机初始居中

def set_servo_angle(servo, angle, min_angle=0, max_angle=180):
    """控制舵机角度（限制范围）"""
    angle = max(min(angle, max_angle), min_angle)  # 限制角度范围
    duty = angle / 18 + 2  # 角度转占空比
    servo.ChangeDutyCycle(duty)
    time.sleep(0.1)
    servo.ChangeDutyCycle(0)  # 防止舵机抖动
    return angle

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

# ===== 键盘事件处理 =====
def on_press(key):
    global current_lr_angle, current_ud_angle
    try:
        # 小车移动控制
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
        
        # 舵机控制
        elif key.char == 'q':  # 左转舵机
            current_lr_angle = set_servo_angle(servo_lr, current_lr_angle - 15)
            print(f"左转舵机: {current_lr_angle}°")
        elif key.char == 'e':  # 右转舵机
            current_lr_angle = set_servo_angle(servo_lr, current_lr_angle + 15)
            print(f"右转舵机: {current_lr_angle}°")
        elif key.char == 'n':  # 舵机上抬
            current_ud_angle = set_servo_angle(servo_ud, current_ud_angle - 15)
            print(f"上抬舵机: {current_ud_angle}°")
        elif key.char == 'm':  # 舵机下压
            current_ud_angle = set_servo_angle(servo_ud, current_ud_angle + 15)
            print(f"下压舵机: {current_ud_angle}°")
            
    except AttributeError:
        pass

def on_release(key):
    stop_motors()  # 松开任何移动键都停止电机
    if key == keyboard.Key.esc:
        return False  # 按ESC退出

# ===== 初始化摄像头 =====
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "BGR888"})
picam2.configure(config)
picam2.start()

# 初始化舵机位置
set_servo_angle(servo_lr, current_lr_angle)
set_servo_angle(servo_ud, current_ud_angle)
stop_motors()

# 启动键盘监听
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

try:
    print("""
    控制指令:
    W - 前进    A - 左转    S - 后退    D - 右转
    Q - 舵机左转  E - 舵机右转
    N - 舵机上抬  M - 舵机下压
    ESC - 退出
    """)
    
    while listener.is_alive():
        frame = picam2.capture_array()
        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("程序被用户中断")

finally:
    # 释放资源
    stop_motors()
    servo_lr.stop()
    servo_ud.stop()
    listener.stop()
    picam2.stop()
    cv2.destroyAllWindows()
    GPIO.cleanup()
    print("程序结束")
