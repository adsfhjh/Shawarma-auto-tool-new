import math
import os
import time
from typing import Tuple, List
from .points import *

import cv2
import numpy as np
import mss

import threading
import queue

img_swm = cv2.imread('img/swm.png')
img_swm_h = cv2.imread('img/swm_h.png')
img_box = cv2.imread('img/box.png')
img_cola_b = cv2.imread('img/cola_b.png')
img_cola_o = cv2.imread('img/cola_o.png')
img_digua = cv2.imread('img/digua.png')
img_shutiao = cv2.imread('img/shutiao.png')
img_shutiao_l = cv2.imread('img/shutiao_l.png')
img_full_screen = cv2.imread('img/full_screen_2.png')

to_show_image = queue.Queue()  # put: (window_name, img)

WINDOW_NAME_GUEST = 'guest'
WINDOW_NAME_TABLE = 'table'
WINDOW_NAME_FRY = 'fry'


def __background_show_window():
    """
    后台显示窗口，用队列，避免阻塞主程序，被 init_show_windows 调用
    :return:
    """
    # 初始化窗口，程序一起动就先弹出来
    cv2.namedWindow(WINDOW_NAME_TABLE, cv2.WINDOW_NORMAL)
    cv2.namedWindow(WINDOW_NAME_GUEST, cv2.WINDOW_NORMAL)
    cv2.namedWindow(WINDOW_NAME_FRY, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME_TABLE, 200, 100)
    cv2.resizeWindow(WINDOW_NAME_GUEST, 200, 100)
    cv2.resizeWindow(WINDOW_NAME_FRY, 200, 100)
    while True:
        try:
            # get from queue
            name, img = to_show_image.get_nowait()
            cv2.imshow(name, img)
            img_size = img.shape
            cv2.resizeWindow(name, img_size[1], img_size[0])
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except queue.Empty:
            time.sleep(0.1)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cv2.destroyAllWindows()


def init_show_windows():
    """
    初始化显示窗口，拉起一个线程
    :return:
    """
    threading.Thread(target=__background_show_window, daemon=True).start()


def calc_center_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    """
    计算两个点的距离
    :param p1: 点1
    :param p2: 点2
    :return: 距离
    """
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def is_center_too_close_to(points_list: List[Tuple[int, int]], center: Tuple[int, int], threshold: int = 10) -> bool:
    """
    判断 center 是否和 points_list 中的任意一个点太近，用于过滤重复识别的点
    :param points_list: 已有的点列表
    :param center: 新的点
    :param threshold: 阈值
    :return: 是否太近
    """
    for p in points_list:
        if calc_center_distance(p, center) < threshold:
            return True
    return False


def match_many_object_on_image(whole_img: np.ndarray,
                               obj_img: np.ndarray,
                               threshold=0.8,
                               draw_rect=False,
                               save_file=False,
                               output_name='output.png') -> List[Tuple[int, int]]:
    """
    在整张图片上找到所有的目标物体
    :param whole_img: 整张图片
    :param obj_img: 目标物体
    :param threshold: 阈值
    :param draw_rect: 是否画出矩形
    :param save_file: 是否保存到文件
    :param output_name: 输出文件名
    :return: 所有目标物体的中心坐标
    """
    # res现在是一个 (xxx, xxx) 的矩阵，表示了在 whole_img 中每个位置与 obj_img 匹配的程度
    res = cv2.matchTemplate(whole_img, obj_img, cv2.TM_CCOEFF_NORMED)
    # np.where(res >= threshold)这行代码用来找出所有匹配度超过给定阈值的位置。
    # np.where函数返回满足条件的元素的索引数组，对于二维数组而言，它会返回两个数组：一个是所有符合条件的元素的行索引，另一个是列索引。
    loc = np.where(res >= threshold)
    # loc = (array([150, 200]), array([100, 300])) 表示两个匹配点的坐标分别是 (150, 100) 和 (200, 300)。
    match = []
    center_points = []
    final_points = []
    # go through all the points
    for pt in zip(*loc[::-1]):
        # pt 将会是 (100, 150) 和 (300, 200)，因为 loc 被反转且解包给 zip
        center = (pt[0] + obj_img.shape[1] // 2, pt[1] + obj_img.shape[0] // 2)
        # if the center is too close to the existing points, skip
        if is_center_too_close_to(center_points, center):
            continue
        center_points.append(center)
        # add to the final points
        final_points.append(pt)
        match.append(pt)
        # draw rect?
        if draw_rect:
            cv2.rectangle(whole_img, pt, (pt[0] + obj_img.shape[1], pt[1] + obj_img.shape[0]), (0, 255, 0), 2)
    if save_file:
        # save to test/output.png
        if not os.path.exists('test'):
            os.mkdir('test')
        cv2.imwrite('test/' + (output_name or 'output.png'), whole_img)
    return final_points


def fast_screen_shot(left_up: Tuple[int, int], right_down: Tuple[int, int], save=True) -> np.ndarray:
    """
    快速截图
    :param left_up:  左上角坐标
    :param right_down:  右下角坐标
    :param save:  是否保存到文件
    :return:  截图
    """
    # ensure correct corner coordinates
    if not (left_up[0] < right_down[0] and left_up[1] < right_down[1]):
        msg = f'截图坐标错误：左上角坐标应小于右下角坐标。传入参数 left_up: {left_up}, right_down: {right_down}'
        raise ValueError(msg)
    with mss.mss() as sct:
        # Define the monitor area to capture
        monitor = {'top': left_up[1], 'left': left_up[0], 'width': right_down[0] - left_up[0],
                   'height': right_down[1] - left_up[1]}
        # Capture the screen
        img = np.array(sct.grab(monitor))
        if save:
            # Save the captured image to a file
            cv2.imwrite('img/capture.png', img)
        # Convert the image from BGRA to BGR format
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    return img


if __name__ == '__main__':
    # for image, name in [
    #     (img_swm, 'swm'),
    #     (img_box, 'box'),
    #     (img_cola_b, 'cola_b'),
    #     (img_cola_o, 'cola_o'),
    #     (img_digua, 'digua'),
    #     (img_shutiao, 'shutiao'),
    # ]:
    #     print(name)
    #     res = match_many_object_on_image(img_full_screen, image, draw_rect=True, output_name=name + '.png')
    #     print(f'there are {len(res)} {name} in the screen')
    fast_screen_shot(POS_GUEST_1_LT, POS_GUEST_1_RB)
