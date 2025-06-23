import RPi.GPIO as GPIO
import cv2
import time
import keyboard  # 需要安装：pip install keyboard

# 初始化GPIO
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
SERVO_PIN = 16  # 假设舵机接在GPIO16（BOARD编号）
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz PWM
servo_pwm.start(0)  # 初始占空比0

def set_servo_angle(angle):
    """控制舵机转动到指定角度（0~180°）"""
    duty = angle / 18 + 2  # 角度转占空比
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)  # 等待舵机转动
    servo_pwm.ChangeDutyCycle(0)  # 停止信号，防止抖动

# ===== 电机控制函数 =====
def stop_motors():
    """停止所有电机"""
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

def forward():
    """前进（两个电机正转）"""
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def backward():
    """后退（两个电机反转）"""
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

def turn_left():
    """左转（左轮反转，右轮正转）"""
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def turn_right():
    """右转（右轮反转，左轮正转）"""
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

# ===== 主程序 =====
try:
    # 初始化摄像头
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  # 设置宽度
    cap.set(4, 480)  # 设置高度

    print("WASD 控制小车，Q 退出")
    while True:
        # 读取摄像头画面
        ret, frame = cap.read()
        if not ret:
            print("摄像头读取失败！")
            break

        # 显示摄像头画面
        cv2.imshow("Camera", frame)

        # 检测键盘输入
        if keyboard.is_pressed('w'):
            forward()
            print("前进")
        elif keyboard.is_pressed('s'):
            backward()
            print("后退")
        elif keyboard.is_pressed('a'):
            turn_left()
            print("左转")
        elif keyboard.is_pressed('d'):
            turn_right()
            print("右转")
        elif keyboard.is_pressed(' '):
            stop_motors()
            print("停止")
        elif keyboard.is_pressed('q'):
            print("退出程序")
            break

        # === 舵机控制示例（可扩展）===
        # 例如：按数字键控制舵机角度
        if keyboard.is_pressed('1'):
            set_servo_angle(45)  # 转到45°
        elif keyboard.is_pressed('2'):
            set_servo_angle(90)  # 转到90°
        elif keyboard.is_pressed('3'):
            set_servo_angle(135)  # 转到135°

        # 检测 OpenCV 窗口关闭
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("程序被用户中断")

finally:
    # 释放资源
    stop_motors()
    servo_pwm.stop()
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()
    print("GPIO 已清理，程序结束")
