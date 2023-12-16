import cv2
import numpy as np
from cv2 import aruco

# カメラの設定
cap = cv2.VideoCapture(9)

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
aruco_params = cv2.aruco.DetectorParameters()

while True:
    # カメラから画像を取得
    ret, img = cap.read()

    # マーカーの検出
    corners, ids, _ = cv2.aruco.detectMarkers(img, aruco_dict, parameters=aruco_params)

    # マーカーが4つあるか確認
    frame_markers = cv2.aruco.drawDetectedMarkers(img.copy(), corners, ids)
    height = img.shape[0]
    width = img.shape[1]
    resized_img = cv2.resize(frame_markers, (int(width/2.5), int(height/2.5)))

    # cv2.namedWindow("img", cv2.WINDOW_NORMAL)
    cv2.imshow("img", resized_img)

    # id=2を検知した場合
    if len(corners) == 4 and 2 in ids:
        # 配列を初期化
        sPoints = np.zeros((4, 2), dtype=np.float32)

        for i, corner in enumerate(corners):
            points = corner[0].astype(np.int32)
            # id=2を検知した場合、その位置を取得
            if ids[i][0] == 2:
                sPoints[i] = points[0]

        sPoints = sPoints.astype(np.float32)
        # sPoints = sPoints[np.lexsort(sPoints[:, 0])]
        sPoints = sPoints[sPoints[:, 0].argsort()]
        print(sPoints)

        # if sPoints[0, 1] > sPoints[1, 1]:
        #     temp = sPoints[0]
        #     sPoints[0] = sPoints[1]
        #     sPoints[1] = temp

        # # 3個目と4個目のy座標を比較して小さい方を4個目にする
        # if sPoints[2, 1] < sPoints[3, 1]:
        #     temp = sPoints[3]
        #     sPoints[3] = sPoints[2]
        #     sPoints[2] = temp

        # 射影元と射影先の設定
        src = sPoints.astype(np.float32)
        dst = np.array([[0, 0], [600, 0], [0, 690], [600, 690]], dtype=np.float32)

        # 射影行列の作成
        M = cv2.getPerspectiveTransform(src, dst)

        # 射影変換の適用
        result = cv2.warpPerspective(img, M, (600, 690))

        cv2.imshow("test", result)

    cv2.waitKey(1)
