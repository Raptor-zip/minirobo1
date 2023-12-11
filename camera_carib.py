import numpy as np
import cv2
import glob

# チェスボードの各マス目の一辺の長さ（メートル）
square_size = 0.02

# チェスボードのサイズ（内角点の数）
pattern_size = (7, 10)

# チェスボード上の3D座標
objp = np.zeros((np.prod(pattern_size), 3), dtype=np.float32)
objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2) * square_size

# 3D座標を保存するリスト
obj_points = []
# 2D座標を保存するリスト
img_points = []

# 画像フォルダのパス
image_folder_path = "img_resized/*.jpg"
# 画像ファイルのパスを取得
image_paths = glob.glob(image_folder_path)

for image_path in image_paths:
    # 画像を読み込み
    frame = cv2.imread(image_path)

    # チェスボードのコーナーを検出
    ret, corners = cv2.findChessboardCorners(frame, pattern_size, None)

    if ret:
        # コーナーが検出されたら3D座標と2D座標を保存
        obj_points.append(objp)
        img_points.append(corners)

        # コーナーを描画
        cv2.drawChessboardCorners(frame, pattern_size, corners, ret)

    cv2.imshow("Calibration", frame)

    # 'q' キーでキャリブレーションを終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# カメラキャリブレーション
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, frame.shape[::-1][1:], None, None)

# 結果を表示
print("Camera Matrix:")
print(mtx)
print("\nDistortion Coefficients:")
print(dist)

# ウィンドウを閉じる
cv2.destroyAllWindows()
