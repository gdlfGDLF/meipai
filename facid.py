from picamera2 import Picamera2
import cv2
import time  # 新增用于帧率控制

# 初始化摄像头
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})  # 限制分辨率
picam2.configure(config)
picam2.start()

# 加载分类器
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

while True:
    start_time = time.time()  # 记录开始时间
    
    # 获取帧并转换色彩
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    # 人脸检测
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, 
        scaleFactor=1.05, 
        minNeighbors=7, 
        minSize=(60, 60)
    )
    
    # 绘制检测框（持久化显示）
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)  # 绿色框
    
    # 显示处理后的帧
    cv2.imshow("Face Detection", frame)
    
    # 控制帧率（约10FPS）
    processing_time = time.time() - start_time
    delay = max(1, int(100 - processing_time * 1000))  # 确保至少1ms延迟
    if cv2.waitKey(delay) == 27:
        break

picam2.stop()
cv2.destroyAllWindows()
