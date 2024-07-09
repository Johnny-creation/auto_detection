import cv2
import numpy as np


def detect_colored_objects_in_video(url):
    # 打开视频流
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    while True:
        # 读取一帧
        ret, frame = cap.read()

        if not ret:
            print("Failed to grab frame.")
            break

        # 将图像转换为HSV颜色空间
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 定义蓝色的HSV范围
        lower_blue = np.array([100, 150, 50])
        upper_blue = np.array([140, 255, 255])

        # 定义棕色的HSV范围
        lower_brown = np.array([10, 100, 20])
        upper_brown = np.array([20, 255, 200])

        # 创建蓝色和棕色掩模
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)

        # 使用形态学操作去除噪声
        kernel = np.ones((5, 5), np.uint8)
        blue_mask = cv2.erode(blue_mask, kernel, iterations=1)
        blue_mask = cv2.dilate(blue_mask, kernel, iterations=2)
        brown_mask = cv2.erode(brown_mask, kernel, iterations=1)
        brown_mask = cv2.dilate(brown_mask, kernel, iterations=2)

        # 检测蓝色轮廓
        blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in blue_contours:
            area = cv2.contourArea(contour)
            if area > 500:  # 过滤掉小面积的噪声轮廓
                cv2.drawContours(frame, [contour], -1, (255, 0, 0), 3)
                print("Blue object detected.")

        # 检测棕色轮廓
        brown_contours, _ = cv2.findContours(brown_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in brown_contours:
            area = cv2.contourArea(contour)
            if area > 500:  # 过滤掉小面积的噪声轮廓
                cv2.drawContours(frame, [contour], -1, (0, 0, 255), 3)
                print("Brown object detected.")

        # 显示当前帧
        cv2.imshow('Frame', frame)

        # 按q键退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放视频捕捉对象和关闭所有窗口
    cap.release()
    cv2.destroyAllWindows()


# 示例使用，传入视频流的URL
video_url = 'http://your_video_url_here'
detect_colored_objects_in_video(video_url)
