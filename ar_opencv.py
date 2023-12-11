from cv2 import aruco
import cv2
import matplotlib.pyplot as plt


#aruco辞書の生成
dict_aruco=aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

#IDを指定 (適当な整数)
marker_id=3

#マーカーサイズ
size_mark=2000

#imgの作成
img=aruco.generateImageMarker(dict_aruco,marker_id,size_mark)

# plt.imshow(img,cmap='gray')
# 画像を保存
output_file = "ar_marker_3.png"
cv2.imwrite(output_file, img)