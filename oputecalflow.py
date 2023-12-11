import cv2
import numpy as np

# カメラからの入力や動画ファイルの読み込み
cap = cv2.VideoCapture(0)  # カメラを使用する場合

# オプティカルフローのアルゴリズムの選択
# Example: Farneback法を使用
optical_flow_algorithm = cv2.optflow.createOptFlow_Farneback()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # グレースケールに変換
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # オプティカルフローの計算
    flow = optical_flow_algorithm.calc(prev, gray, None)

    # オプティカルフローの表示
    # オプティカルフローはベクトル場で、各ピクセルに対してベクトルが対応している
    h, w = flow.shape[:2]
    y, x = np.mgrid[0:h, 0:w].reshape(2, -1).astype(int)
    fx, fy = flow[y, x].T

    # ベクトルを画像上に描画
    lines = np.column_stack((x, y, x + fx, y + fy)).reshape(-1, 2, 2)
    for line in lines:
        cv2.line(frame, tuple(line[0]), tuple(line[1]), (0, 255, 0), 2)

    cv2.imshow('Optical Flow', frame)

    # ESCキーで終了
    if cv2.waitKey(30) == 27:
        break

    prev = gray

cap.release()
cv2.destroyAllWindows()
