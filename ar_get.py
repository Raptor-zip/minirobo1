import cv2
from cv2 import aruco
import math
import time

### --- aruco設定 --- ###
# dict_aruco = aruco.Dictionary_get(aruco.DICT_4X4_50)
dict_aruco = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
# parameters = aruco.DetectorParameters_create()
parameters = cv2.aruco.DetectorParameters()

cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, dict_aruco, parameters=parameters)

        # マーカーの座標とIDの配列を取得
        if ids is not None:
            for i in range(len(ids)):
                marker_id = ids[i]
                marker_corners = corners[i][0]

                # マーカーの座標とIDを表示
                print(f"Marker ID: {marker_id}, Corners: {marker_corners}")

                if marker_id == 2 or marker_id == 3:
                    # 対角線の長さを計算
                    diagonal_length = math.sqrt((marker_corners[0][0] - marker_corners[2][0])**2 + (marker_corners[0][1] - marker_corners[2][1])**2)

                    print(f"Marker ID: {marker_id}, Diagonal Length: {diagonal_length}")
            print("ーーーーーーーーーーーーーーーーーーーーーー")

        frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners, ids)
        cv2.imshow('frame', frame_markers)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyWindow('frame')
    cap.release()
except KeyboardInterrupt:
    cv2.destroyWindow('frame')
    cap.release()
