import cv2
import numpy as np
import math

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
        ids_list_temp = ids.tolist()
        ids_list = [item for sublist in ids_list_temp for item in sublist]
        if 1 in ids_list and len(ids) >= 2:

            # マーカーの座標を取得
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_length, cameraMatrix, distCoeffs)

            # id 1のマーカーの回転行列を取得
            rmat1, _ = cv2.Rodrigues(rvecs[ids_list.index(1)])

            # 画像を回転
            h, w, c = frame.shape
            angle = np.degrees(np.arctan2(rmat1[1, 0], rmat1[0, 0]))
            a = np.radians(angle)
            w_rot = int(np.round(w * abs(np.cos(a)) + h * abs(np.sin(a))))
            h_rot = int(np.round(w * abs(np.sin(a)) + h * abs(np.cos(a))))
            M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
            M[0][2] += -w/2 + w_rot/2
            M[1][2] += -h/2 + h_rot/2
            img_rot = cv2.warpAffine(frame, M, (w_rot, h_rot), borderValue=(255, 255, 255))

            # 上下左右反転
            img_flip_ud_lr = cv2.flip(img_rot, -1)

            cv2.imshow("", img_flip_ud_lr)

            # 回転後のマーカーを検出
            corners_2, ids_2, _ = cv2.aruco.detectMarkers(img_flip_ud_lr, aruco_dict, parameters=aruco_params)

            if ids_2 is not None:
                ids_2_list_temp = ids_2.tolist()
                ids_2_list = [item for sublist in ids_2_list_temp for item in sublist]
                if 1 in ids_2_list and len(ids_2) >= 2:

                    # 回転後のマーカーの座標を取得
                    rvecs_2, tvecs_2, _ = cv2.aruco.estimatePoseSingleMarkers(corners_2, marker_length, cameraMatrix, distCoeffs)

                    # id 1のマーカーの回転行列を取得
                    rmat1_2, _ = cv2.Rodrigues(rvecs_2[ids_2_list.index(1)])

                    # 2つ目のマーカーの回転行列を取得
                    if ids_2_list.index(1) + 1 < len(ids_2_list):
                        rmat2, _ = cv2.Rodrigues(rvecs_2[ids_2_list.index(1) + 1])
                    else:
                        rmat2, _ = cv2.Rodrigues(rvecs_2[ids_2_list.index(1) - 1])

                    # 座標変換
                    tvec_marker1 = tvecs[ids_list.index(1)][0]
                    tvec_marker2 = tvecs_2[ids_2_list.index(1)][0]
                    rotated_tvec_marker2 = np.dot(rmat1.T, tvec_marker2)

                    # x軸とy軸での座標差を計算
                    x_difference = int(rotated_tvec_marker2[0] - tvec_marker1[0])
                    y_difference = int(rotated_tvec_marker2[1] - tvec_marker1[1])
                    z_difference = int(rotated_tvec_marker2[2] - tvec_marker1[2])

                    # 結果を表示
                    print(f"X     {ids[0]} and {ids[1]}: {x_difference} mm")
                    print(f"Y     {ids[0]} and {ids[1]}: {y_difference} mm")
                    print(f"Z     {ids[0]} and {ids[1]}: {z_difference} mm")

                else:
                    print("1が見つからなかったか、2つ以上みつからなかった")
            else:
                print("回転後にみつからない！")
        else:
            print("1が見つからなかったか、2つ以上みつからなかった")
    else:
        print("Markers not detected")

    # 終了処理
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
