import asyncio
import time
from typing import Tuple

import sha
import sha.cv as cv
from sha.points import *
from config import *
from time import sleep
from threading import Thread

from pynput import keyboard
from concurrent.futures import ThreadPoolExecutor

from rich import print

SUPER_CLICK = False
EXECUTOR = ThreadPoolExecutor(max_workers=1)
# global var to implement print_once function
print_once_done = False

__doc__ = """
[bold yellow]按下 ESC 键即退出，防止在其他程序内启用脚本。[/]

按下 p 打印鼠标位置，同时会复制坐标方便粘贴

按下 TAB 或者 d 开启连点，松开关闭。
只要激活连点，就会中断当前的脚本操作，立即切换鼠标连点（方便点小偷）

按下 q 一键添加四个菜，卷饼，加酱料，点机器打包。（需要解锁：自动刮肉，自动飞饼，一键打包）
按下 w 点击炸薯条，一键把炸好的薯条放到桌子上（不是切土豆）
按下 a 点击老板，备货（需要解锁：员工培训）

1、2、3、4（非小键盘）可以识别客人需求，自动喂食

"""


def print_once(*args, **kwargs):
    global print_once_done
    if not print_once_done:
        print(*args, **kwargs)
        print_once_done = True


def enable_super_click():
    """ 开启连点 """
    global SUPER_CLICK
    sha.FAILSAFE = True
    sha.mouse_up()
    SUPER_CLICK = True
    print('打开连点: {0}'.format(
        SUPER_CLICK))


def disable_super_click():
    """ 关闭连点 """
    global SUPER_CLICK
    SUPER_CLICK = False
    sha.FAILSAFE = False
    print('关闭连点: {0}'.format(
        SUPER_CLICK))


def action_add_4_dish():
    """
    一键添加四个菜
    :return:
    """
    # add dish
    print('[1] 一键添加四种酱料开始')
    for p in [POS_DISH_1, POS_DISH_2, POS_DISH_3, POS_DISH_4]:
        if SUPER_CLICK:
            return
        sha.click(p, DISH_CLICK_COUNT)
        print(f'[1] 酱料位置 {p} 完成')
    if SUPER_CLICK:
        return


def action_add_sauce(is_swipe=False):
    """
    添加石榴汁
    :return:
    """
    # just click first
    print('[2] 左下角酱汁开始')
    sha.move_to(POS_SHILIU)
    if is_swipe:
        if SUPER_CLICK:
            return
        sha.click(POS_SHILIU, 1)
        sleep(.1)
        sha.swipe(POS_SHILIU, POS_CACE_CENTER)
        print('[2] 左下角酱汁滑动完成')
        if SUPER_CLICK:
            return
        # sleep(1)
    else:
        sleep(.05)
        sha.click(POS_SHILIU, 2)
        # sleep(1)
        print('[2] 左下角酱汁点击完成')


def action_roll_pancake():
    """
    卷饼
    :return:
    """
    sha.swipe(POS_CAKE_BOTTOM, POS_CAKE_TOP, sha.DRAG_MODE_SLOW)
    print('[-] 卷饼操作完成')


def action_wrap_pancake():
    """
    打包
    :return:
    """
    sha.click(POS_WRAPPING_MACHINE, 3, 0.08)
    print('[-] 打包操作完成')


def action_fry_potato():
    """
    炸薯条
    :return:
    """
    sha.swipe(POS_TABLE_LEFT, POS_TABLE_RIGHT)
    print('[5] 炸土豆前战术性收钱已完成')
    action_click_potato_pot(2)
    sleep(.2)
    sha.click(POS_POTATO)
    sleep(.2)
    print(f'[5] 开始切土豆，需要切：{int(POTATO_CUT_TIME * 10) * 0.1} 秒')
    sha.click_hold(POS_POTATO, POTATO_CUT_TIME)
    sha.move_to(POS_TABLE_CENTER)
    print('[5] 土豆切割+炸土豆完成')


def action_click_potato_pot(cnt=1):
    sha.click(POS_POTATO_FRY, cnt)
    print(f'[-] 点击炸好的土豆 {cnt} 次')


def action_boss_add_atock():
    sha.click(POS_BOSS, 1)
    print('[-] 老板备货完成')


def action_click_coca_machine():
    sha.click(POS_COCA_1, 1)
    sha.click(POS_COCA_2, 1)
    print('[-] 可乐机点击完成')


def super_add_dish_sauce_pack():
    """
    一键添加四个菜，卷饼，点机器打包
    :return:
    """
    print('=' * 20)
    print('一键添加四个菜，卷饼，加酱料，点机器打包')
    t1 = time.time()
    # add sauce
    action_add_sauce()
    if SUPER_CLICK:
        return
    # add 4 dish
    action_add_4_dish()
    if SUPER_CLICK:
        return
    # sleep(.2)
    # after click 4 dish, there's a small time gap
    # add stock
    action_boss_add_atock()
    # click potato
    action_click_potato_pot()
    # click coca machine
    action_click_coca_machine()
    sleep(.2)
    # roll the pancake
    action_roll_pancake()
    if SUPER_CLICK:
        return
    # while waiting for pancake, we clean the table
    # handle_swipte_table()
    # wrap
    # action_wrap_pancake()
    if SUPER_CLICK:
        return
    sha.move_to(POS_TABLE_CENTER)
    print('-' * 20)
    print(f'制作一个沙威玛耗时 {(time.time() - t1) * 1000:.2f} 毫秒\n')


def super_fry_potato():
    """
    一键炸薯条，升级了自动切薯条的话，此函数不需要
    :return:
    """
    action_fry_potato()


def handle_swipte_table():
    print('[6] 开始滑动桌子收钱')
    sha.swipe(POS_TABLE_LEFT, POS_TABLE_RIGHT)
    print('[6] 滑动桌子收钱完成')
    sha.move_to(POS_TABLE_CENTER)


def __feed_cola_1(guest_pos: Tuple[int, int]) -> None:
    sha.swipe(POS_COCA_CUP_1, guest_pos, sha.DRAG_MODE_TELEPORT)


def __feed_cola_2(guest_pos: Tuple[int, int]) -> None:
    sha.swipe(POS_COCA_CUP_2, guest_pos, sha.DRAG_MODE_TELEPORT)


def __feed_swm(guest_pos: Tuple[int, int], count=3) -> None:
    """
    喂食沙威玛，不包括图像识别
    :param guest_pos:  客人位置
    :param count:  需要喂食的数量
    :return:
    """
    pos = [POS_TABLE_CENTER_UPPER, POS_TABLE_CENTER_LOWER, POS_TABLE_CENTER]
    for i in range(count):
        sha.swipe(pos[i], guest_pos, sha.DRAG_MODE_TELEPORT)
        if count > 1 and i != count - 1:
            sleep(0.05)


def __feed_swm_image_recognition(guest_pos: Tuple[int, int], count=3) -> None:
    """
    通过图像识别喂食沙威玛
    :param guest_pos:  客人位置
    :param count:  需要喂食的数量
    :return:
    """
    # first get all coords of all swm
    print(f'沙威玛：', end='')
    img = cv.fast_screen_shot(POS_TABLE_LT, POS_TABLE_RB)
    cv.to_show_image.put((cv.WINDOW_NAME_TABLE, img))
    res = cv.match_many_object_on_image(img, cv.img_swm_h, draw_rect=True, output_name='swm_h.png')
    # shift the coords. res' coords are relative to POS_TABLE_LT
    res = [(x + POS_TABLE_LT[0], y + POS_TABLE_LT[1]) for x, y in res]
    print(f'桌子上有 {len(res)} 个，需要 {count} 个，满足条件：{len(res) >= count}')
    # feed the least swm
    for i in range(min(count, len(res))):
        sha.swipe(res[i], guest_pos, sha.DRAG_MODE_TELEPORT)
        sleep(.05)


def __feed_drink(guest_pos: Tuple[int, int], count=1) -> None:
    for i in range(count):
        sha.swipe(POS_DRINK, guest_pos, sha.DRAG_MODE_TELEPORT)


def __feed_digua(guest_pos: Tuple[int, int], count=1) -> None:
    # sha.swipe(POS_DIGUA, guest_pos, sha.DRAG_MODE_TELEPORT)
    for i in range(count):
        sha.swipe(POS_DIGUA, guest_pos, sha.DRAG_MODE_TELEPORT)


def __feed_shutiao(guest_pos: Tuple[int, int], count=3) -> None:
    shutiao = [POS_FRY_1, POS_FRY_2, POS_FRY_3]
    for i in range(count):
        sha.swipe(shutiao[i], guest_pos, sha.DRAG_MODE_TELEPORT)


def __feed_shutiao_image_recognition(guest_pos: Tuple[int, int], count=3) -> None:
    # first get all coords of all shutiao
    print(f'桌子上：', end='')
    img = cv.fast_screen_shot(POS_FRY_LT, POS_FRY_RB)
    res = cv.match_many_object_on_image(img, cv.img_shutiao_l, draw_rect=True, output_name='shutiao.png')
    cv.to_show_image.put((cv.WINDOW_NAME_FRY, img))
    # shift the coords. res' coords are relative to POS_FRY_LT
    res = [(x + POS_FRY_LT[0], y + POS_FRY_LT[1]) for x, y in res]
    print(f'有 {len(res)} 个薯条，需要 {count} 个，满足条件：{len(res) >= count}')
    # feed the least shutiao
    for i in range(min(count, len(res))):
        sha.swipe(res[i], guest_pos, sha.DRAG_MODE_TELEPORT)
        sleep(.1)


def __feed_guest(guest_pos: Tuple[int, int]) -> None:
    t1 = time.time()
    __feed_cola_1(guest_pos)
    __feed_cola_2(guest_pos)
    if SUPER_CLICK:
        return
    print(f'[7] 可乐 {guest_pos} (1/2)')
    __feed_swm(guest_pos)
    print(f'[7] 卷饼 {guest_pos} (1)')
    if SUPER_CLICK:
        return
    __feed_drink(guest_pos)
    __feed_drink(guest_pos)
    print(f'[7] 盒装饮料 {guest_pos}')
    if SUPER_CLICK:
        return
    __feed_digua(guest_pos)
    __feed_digua(guest_pos)
    print(f'[7] 地瓜 {guest_pos}')
    if SUPER_CLICK:
        return
    action_click_coca_machine()
    __feed_shutiao(guest_pos, 2)
    print(f'[7] 薯条 {guest_pos}')
    if SUPER_CLICK:
        return
    __feed_cola_1(guest_pos)
    __feed_cola_2(guest_pos)
    print(f'[7] 可乐 {guest_pos} (2/2)')
    t2 = time.time()
    print(f'[7] 客人 {guest_pos} 喂食完成，耗时 {t2 - t1:.2f} 秒')


def __feed_guest_image_recognition(pos_left_top: Tuple[int, int],
                                   pos_right_bottom: Tuple[int, int],
                                   pos_guest_center: Tuple[int, int]) -> None:
    """
    通过图像识别喂食客人
    :param pos_left_top: 客人气泡左上角
    :param pos_right_bottom: 客人气泡右下角
    :param pos_guest_center: 客人中心位置
    :return:
    """
    # print(f'debug __feed_guest_image_recognition {pos_left_top} {pos_right_bottom} {pos_guest_center}')
    print(f'=' * 20)
    print(f'开始识别 {pos_guest_center} 的需求')
    t1 = time.time()

    # get the screenshot
    img = cv.fast_screen_shot(pos_left_top, pos_right_bottom)
    t2 = time.time()
    # generate item list
    item_list = {}
    for item, name in [
        (cv.img_swm, 'swm'),
        (cv.img_box, 'box'),
        (cv.img_cola_b, 'cola_b'),
        (cv.img_cola_o, 'cola_o'),
        (cv.img_digua, 'digua'),
        (cv.img_shutiao, 'shutiao'),
    ]:
        res = cv.match_many_object_on_image(img, item, draw_rect=True)
        # update number of items
        item_list[name] = len(res)
    t3 = time.time()
    # show window
    cv.to_show_image.put((cv.WINDOW_NAME_GUEST, img))
    print(f'客人 {pos_guest_center} 的物品列表：{item_list}')
    # if cola is larger than 1, we first feed cola
    if item_list['cola_b'] > 0:
        __feed_cola_2(pos_guest_center)
    if item_list['cola_o'] > 0:
        __feed_cola_1(pos_guest_center)
    # feed other items
    if item_list['swm'] > 0:
        __feed_swm_image_recognition(pos_guest_center, item_list['swm'])
    if item_list['box'] > 0:
        __feed_drink(pos_guest_center, item_list['box'])
    if item_list['digua'] > 0:
        __feed_digua(pos_guest_center, item_list['digua'])
    if item_list['shutiao'] > 0:
        __feed_shutiao_image_recognition(pos_guest_center, item_list['shutiao'])
    # feed the rest cola
    if item_list['cola_b'] > 1:
        sleep(1.2)
        __feed_cola_2(pos_guest_center)
    if item_list['cola_o'] > 1:
        sleep(1.2)
        __feed_cola_1(pos_guest_center)
    t4 = time.time()
    sha.move_to(POS_TABLE_CENTER)
    print(f'截图 {(t2 - t1) * 1000:.2f} 毫秒，识别 {(t3 - t2) * 1000:.2f} 毫秒，喂食 {(t4 - t3) * 1000:.2f} 毫秒')
    print('-' * 20 + '\n')


def feed_guest(guest_pos: Tuple[int, int]) -> None:
    Thread(target=__feed_guest, args=(guest_pos,), daemon=True).start()
    # EXECUTOR.submit(__feed_guest, guest_pos)


def feed_guest_image_recognition(pos_left_top: Tuple[int, int],
                                 pos_right_bottom: Tuple[int, int],
                                 pos_guest_center: Tuple[int, int]) -> None:
    """
    通过图像识别喂食客人. **传参顺序：左上角，右下角，客人中心**
    :param pos_left_top: 客人气泡左上角
    :param pos_right_bottom: 客人气泡右下角
    :param pos_guest_center: 客人中心位置
    :return:
    """
    # Thread(target=__feed_guest_image_recognition,
    #        args=(pos_left_top, pos_right_bottom, pos_guest_center),
    #        daemon=True).start()

    # check arguments order
    if pos_guest_center[0] > pos_left_top[0] or pos_guest_center[0] > pos_right_bottom[0]:
        print_once(f'[yellow]传入的客人坐标可能有误：客人中心点 {pos_guest_center} 应当位于气泡区域的左侧'
                   f'（比左上角{pos_left_top}、右下角{pos_right_bottom}均更靠左），'
                   '但现在位于气泡区域中间或右侧。如果图像识别不工作，请检查传参顺序。如正常，可忽略此消息。[/]')
    EXECUTOR.submit(__feed_guest_image_recognition, pos_left_top, pos_right_bottom, pos_guest_center)


async def handle_key_press(key):
    if key in {keyboard.Key.esc}:
        # Stop listener
        return False
    try:
        if key.char == 'p':
            sha.print_mouse()

        elif key.char == 'a':
            sha.click(POS_BOSS, 2)
            sha.move_to(POS_TABLE_CENTER)

        elif key.char == 'q':
            EXECUTOR.submit(super_add_dish_sauce_pack)

        elif key.char == 'w':
            # waiting for package fly to table
            # do other stuff
            action_click_coca_machine()
            action_click_potato_pot(2)
            sha.move_to(POS_TABLE_CENTER)

        # elif key.char == 'e':
        #     EXECUTOR.submit(super_fry_potato)

        elif key.char == 'c':
            EXECUTOR.submit(handle_swipte_table)

        elif key.char == 'd':
            enable_super_click()

        elif key.char == 'z':
            sha.move_to(POS_DRINK)
        elif key.char == 'x':
            sha.move_to(POS_DIGUA)
        elif key.char == '1':
            # feed_guest(POS_GUEST_1)
            feed_guest_image_recognition(POS_GUEST_1_LT, POS_GUEST_1_RB, POS_GUEST_1)
        elif key.char == '2':
            # feed_guest(POS_GUEST_2)
            feed_guest_image_recognition(POS_GUEST_2_LT, POS_GUEST_2_RB, POS_GUEST_2)
        elif key.char == '3':
            # feed_guest(POS_GUEST_3)
            feed_guest_image_recognition(POS_GUEST_3_LT, POS_GUEST_3_RB, POS_GUEST_3)
        elif key.char == '4':
            # feed_guest(POS_GUEST_4)
            feed_guest_image_recognition(POS_GUEST_4_LT, POS_GUEST_4_RB, POS_GUEST_4)
    except AttributeError:
        if key == keyboard.Key.tab:
            enable_super_click()


async def handle_key_release(key):
    if key == keyboard.Key.tab:
        disable_super_click()
    # d
    try:
        if key.char == 'd':
            disable_super_click()
    except AttributeError:
        pass


def on_press(key):
    return asyncio.run(handle_key_press(key))


def on_release(key):
    return asyncio.run(handle_key_release(key))


def super_click_thread():
    print('鼠标连点线程已启动')
    while True:
        if SUPER_CLICK:
            sha.click_no_pos()
            sleep(0.05)
        else:
            sleep(0.05)


if __name__ == '__main__':
    # Start super click thread
    Thread(target=super_click_thread, daemon=True).start()
    cv.init_show_windows()
    print(__doc__)
    # Collect events until released
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()
