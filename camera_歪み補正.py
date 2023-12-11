import cv2
import numpy as np

# カメラキャリブレーションで取得した歪み行列と歪み係数
camera_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])
dist_coeffs = np.array([k1, k2, p1, p2, k3])

cap = cv2.VideoCapture(0)

while True:
    # 画像の読み込み
    image = cv2.imread('your_image.jpg')
    image = cap.read()

    # 歪み補正
    undistorted_image = cv2.undistort(image, camera_matrix, dist_coeffs)

    # 歪み補正前後の画像を表示
    cv2.imshow('Original Image', image)
    cv2.imshow('Undistorted Image', undistorted_image)
    cv2.waitKey(0)
cv2.destroyAllWindows()
