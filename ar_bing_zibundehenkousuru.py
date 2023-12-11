import cv2
import numpy as np
import math

# カメラの設定
cap = cv2.VideoCapture(0)

# ArUcoライブラリの設定
# aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
# aruco_params = cv2.aruco.DetectorParameters_create()
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
aruco_params = cv2.aruco.DetectorParameters()
# マーカーの1辺の長さ
marker_length = 104


# カメラの内部パラメータを手動で設定
fx = 1453.61  # x軸方向の焦点距離
fy = 1456.56  # y軸方向の焦点距離
cx = 533.63   # x軸方向の光学中心の座標
cy = 948.43   # y軸方向の光学中心の座標
cameraMatrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])

# レンズ歪み係数を手動で設定
distCoeffs = np.zeros((5, 1))
# distCoeffs[0, 0] = 0.10194263
# distCoeffs[1, 0] = -0.16779273
# distCoeffs[2, 0] = -0.00536217
# distCoeffs[3, 0] = -0.00288195
# distCoeffs[4, 0] = 0.20033851

while True:
    # カメラから画像を取得
    ret, frame = cap.read()

# 逆光対策として、ヒストグラム平滑化
    img_yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV) # RGB => YUV(YCbCr)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4,4)) # claheオブジェクトを生成
    img_yuv[:,:,0] = clahe.apply(img_yuv[:,:,0]) # 輝度にのみヒストグラム平坦化
    frame = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR) # YUV => RGB

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

            h, w, c = frame.shape
            angle = angle1_x
            a = np.radians(angle)
            w_rot = int(np.round(w*abs(np.cos(a)) + h*abs(np.sin(a))))
            h_rot = int(np.round(w*abs(np.sin(a)) + h*abs(np.cos(a))))

            M = cv2.getRotationMatrix2D((w/2,h/2), angle, 1)
            M[0][2] += -w/2 + w_rot/2
            M[1][2] += -h/2 + h_rot/2

            img_rot  = cv2.warpAffine(frame, M, (w_rot,h_rot), borderValue=(255, 255, 255)) # 画像を回転?
            img_flip_ud_lr = cv2.flip(img_rot, -1) # 上下左右反転



            corners_2, ids_2, _ = cv2.aruco.detectMarkers(img_flip_ud_lr, aruco_dict, parameters=aruco_params)

            frame_markers = cv2.aruco.drawDetectedMarkers(img_flip_ud_lr.copy(), corners_2, ids_2)
            cv2.imshow("", frame_markers)

            if ids_2 is not None:
                ids_2_list_temp = ids_2.tolist() # idsのままだと.index()使えないから通常の配列に変換したものを作る
                ids_2_list = [item for sublist in ids_2_list_temp for item in sublist]
                if 1 in ids_2_list and len(ids_2) >= 2:  #idsに1が含まれていてidsが2個以上なら

                    # マーカーの座標を取得
                    rvecs_2, tvecs_2, _ = cv2.aruco.estimatePoseSingleMarkers(corners_2, marker_length, cameraMatrix, distCoeffs)

                    # id 1のマーカーの角度を計算（X軸に対する回転）
                    rmat1_2, _ = cv2.Rodrigues(rvecs_2[ids_2_list.index(1)])
                    angle1_x_2 = np.degrees(np.arctan2(rmat1_2[1, 0], rmat1_2[0, 0]))

                    if angle1_x_2 < 0:
                        angle1_x_2=+180

                    # 2つ目のマーカーの角度を計算（X軸に対する回転）
                    if ids_2_list.index(1)+1 < len(ids_2_list):
                        rmat2, _ = cv2.Rodrigues(rvecs_2[ids_2_list.index(1)+1])
                    else:
                        rmat2, _ = cv2.Rodrigues(rvecs_2[ids_2_list.index(1)-1])
                    angle2_x = np.degrees(np.arctan2(rmat2[1, 0], rmat2[0, 0]))

                    # 角度を表示
                    # print(f"Angle for marker {ids[0]}: {angle1_x} degrees")
                    # print(f"Angle for marker {ids[1]}: {angle2_x} degrees")

                    # 角度差を表示
                    angle_diff = int(angle2_x - angle1_x_2)
                    print(f"Angle {ids[0]} and {ids[1]}: {angle_diff} degrees")

                    # id 1のマーカーの位置を取得
                    tvec_marker1 = tvecs_2[ids_2_list.index(1)][0]

                    # 2つ目のマーカーの位置を取得
                    if ids_2_list.index(1)+1 < len(ids_2_list):
                        tvec_marker2 = tvecs_2[ids_2_list.index(1)+1][0]
                    else:
                        tvec_marker2 = tvecs_2[ids_2_list.index(1)-1][0]

                    # x軸とy軸での座標差を計算
                    x_difference = int(tvec_marker2[0] - tvec_marker1[0])
                    y_difference = int(tvec_marker2[1] - tvec_marker1[1])
                    z_difference = int(tvec_marker2[2] - tvec_marker1[2])

                    # 結果を表示
                    print(f"X     {ids[0]} and {ids[1]}: {x_difference} mm")
                    print(f"Y     {ids[0]} and {ids[1]}: {y_difference} mm")
                    print(f"Z     {ids[0]} and {ids[1]}: {z_difference} mm")


                    # 距離を表示
                    # distance = np.linalg.norm(tvecs[1] - tvecs[0])
                    # print("Distance between markers: ", distance)
                else:
                    print("1が見つからなかったか、2つ以上みつからなかった")
            else:
                print("回転後にみつからない！")
        else:
            print("1が見つからなかったか、2つ以上みつからなかった")
    else:
        print("Markers not detected")

    # 画像を表示
    # cv2.imshow("frame", frame)

    # 終了処理
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()