import cv2
import numpy as np

# カメラの設定
cap = cv2.VideoCapture(0)

# ArUcoライブラリの設定
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
aruco_params = cv2.aruco.DetectorParameters()

# マーカーの1辺の長さ
marker_length = 104

# カメラの内部パラメータを手動で設定
fx = 1000.0  # x軸方向の焦点距離
fy = 1000.0  # y軸方向の焦点距離
cx = 320.0   # x軸方向の光学中心の座標
cy = 240.0   # y軸方向の光学中心の座標
cameraMatrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])

# レンズ歪み係数を手動で設定
distCoeffs = np.zeros((5, 1))

while True:
    # カメラから画像を取得
    ret, frame = cap.read()

    # マーカーを検出
    corners, ids, _ = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=aruco_params)

    # マーカーが検出された場合
    if ids is not None:
        ids_list_temp = ids.flatten().tolist()  # idsを1次元にして通常のリストに変換
        if 1 in ids_list_temp and len(ids) >= 2:
            # マーカーの座標を取得
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_length, cameraMatrix, distCoeffs)

            # id 1のマーカーの座標を原点に設定
            tvec_marker1 = tvecs[ids_list_temp.index(1)][0]
            frame_center = np.array([frame.shape[1] // 2, frame.shape[0] // 2])  # 画像中心の座標
            translation_vector = frame_center - tvec_marker1[:2]
            translation_matrix = np.float32([[1, 0, translation_vector[0]], [0, 1, translation_vector[1]]])
            frame_rotated = cv2.warpAffine(frame, translation_matrix, (frame.shape[1], frame.shape[0]))

            # 画像を回転
            rmat1, _ = cv2.Rodrigues(rvecs[ids_list_temp.index(1)])
            angle1_x = np.degrees(np.arctan2(rmat1[1, 0], rmat1[0, 0]))
            rotation_matrix = cv2.getRotationMatrix2D(tuple(tvec_marker1[:2]), -angle1_x, 1)
            frame_rotated = cv2.warpAffine(frame_rotated, rotation_matrix, (frame.shape[1], frame.shape[0]))

            # 画像を表示
            cv2.imshow("frame", frame_rotated)

        else:
            print("Marker 1 not found or less than 2 markers detected.")
    else:
        print("Markers not detected")

    # 終了処理
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
