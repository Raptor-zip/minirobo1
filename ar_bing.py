import cv2
import numpy as np

# カメラの設定
cap = cv2.VideoCapture(9)

# ArUcoライブラリの設定
# aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
# aruco_params = cv2.aruco.DetectorParameters_create()
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
        ids_list_temp = ids.tolist() # idsのままだと.index()使えないから通常の配列に変換したものを作る
        ids_list = [item for sublist in ids_list_temp for item in sublist]
        if 1 in ids_list and len(ids) >= 2:  #idsに1が含まれていてidsが2個以上なら

            # マーカーの座標を取得
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_length, cameraMatrix, distCoeffs)

            # id 1のマーカーの角度を計算（X軸に対する回転）
            rmat1, _ = cv2.Rodrigues(rvecs[ids_list.index(1)])
            angle1_x = np.degrees(np.arctan2(rmat1[1, 0], rmat1[0, 0]))

            # 2つ目のマーカーの角度を計算（X軸に対する回転）
            if ids_list.index(1)+1 < len(ids_list):
                rmat2, _ = cv2.Rodrigues(rvecs[ids_list.index(1)+1])
            else:
                rmat2, _ = cv2.Rodrigues(rvecs[ids_list.index(1)-1])
            angle2_x = np.degrees(np.arctan2(rmat2[1, 0], rmat2[0, 0]))

            # 角度を表示
            # print(f"Angle for marker {ids[0]}: {angle1_x} degrees")
            # print(f"Angle for marker {ids[1]}: {angle2_x} degrees")

            # 角度差を表示
            angle_diff = int(angle2_x - angle1_x)
            print(f"Angle {ids[0]} and {ids[1]}: {angle_diff} degrees")

            # # id 1のマーカーの位置を取得
            # tvec_marker1 = tvecs[ids_list.index(1)][0]

            # # 2つ目のマーカーの位置を取得
            # if ids_list.index(1)+1 < len(ids_list):
            #     tvec_marker2 = tvecs[ids_list.index(1)+1][0]
            # else:
            #     tvec_marker2 = tvecs[ids_list.index(1)-1][0]

            # # x軸とy軸での座標差を計算
            # x_difference = tvec_marker2[0] - tvec_marker1[0]
            # y_difference = tvec_marker2[1] - tvec_marker1[1]

            # # 結果を表示
            # print(f"X-axis difference between markers {ids[0]} and {ids[1]}: {x_difference} units")
            # print(f"Y-axis difference between markers {ids[0]} and {ids[1]}: {y_difference} units")


            # 距離を表示
            # distance = np.linalg.norm(tvecs[1] - tvecs[0])
            # print("Distance between markers: ", distance)
        else:
            print("1が見つからなかったか、2つ以上みつからなかった")
    else:
        print("Markers not detected")

    # 画像を表示
    cv2.imshow("frame", frame)

    # 終了処理
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()