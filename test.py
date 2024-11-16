from sha.cv import *
import cv2
from datetime import datetime


def now():
    return datetime.now().strftime('%H:%M:%S')


if __name__ == '__main__':
    for image in [
        'test/swm.png',
        'test/box.png',
        'test/cola_b.png',
        'test/cola_o.png',
        'test/digua.png',
        'test/shutiao.png',
    ]:
        full_screen = cv2.imread('test/full.png')
        print(f'当前测试 {image}')
        name = image.split('/')[-1].split('.')[0]
        img = cv2.imread(image)
        res = match_many_object_on_image(full_screen, img, draw_rect=True, save_file=False)
        output_name = f'__test_{name}.png'
        cv2.putText(full_screen, f'{name}: {len(res)} test at {now()}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imwrite(f'test/{output_name}', full_screen)
        print(f'发现了 {len(res)} 个 {name}')
