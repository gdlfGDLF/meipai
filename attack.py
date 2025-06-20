from picamera2 import Picamera2
import cv2
import numpy as np
from collections import deque
import time

# 红色的HSV范围定义
red1 = np.array([170, 100, 100])  
red2 = np.array([179, 255, 255])

# 设置路径缓冲区
mybuffer = 64  
pts = deque(maxlen=mybuffer)

# 初始化相机（新版API）
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()
time.sleep(1)  # 让相机预热

while True:
    # 获取帧（新版API直接返回numpy数组）
    frame = picam2.capture_array()
    
    # 将RGB图像转换为BGR格式（确保颜色显示正常）
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # 颜色检测逻辑
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, red1, red2)
    mask = cv2.erode(mask, None, iterations=2)  # 腐蚀操作
    mask = cv2.dilate(mask, None, iterations=2)  # 膨胀操作
    
    # 查找轮廓
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]  
    center = None  
    
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))

        if radius > 10:  # 如果物体的半径大于10，进行标记
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)  # 画圆
            cv2.circle(frame, center, 5, (0, 0, 255), -1)  # 画中心点
            pts.appendleft(center)
    
    # 绘制路径（用线条连接前几个点）
    for i in range(1, len(pts)):
        if pts[i - 1] is None or pts[i] is None:  
            continue
        thickness = int(np.sqrt(mybuffer / float(i + 1)) * 2.5)  # 线条的粗细
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)  # 画线

    # 显示处理过的帧
    cv2.imshow("Frame", frame)
    
    # 按'q'键退出程序
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break  # 按'q'退出循环

# 停止相机并关闭所有窗口
picam2.stop()
cv2.destroyAllWindows()
