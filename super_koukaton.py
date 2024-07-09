import os
import sys
import pygame as pg

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class JUMP(pg.sprite.Group):
    """
    こうかとんがジャンプに関するクラス
    """
    def __init__(self):
        self.up = -20  # こうかとんのジャンプ力
        self.down = 1  # こうかとんの重力
        self.speed = 0  # y方向の速度
        self.on = True  # こうかとんが地面にいるか判定


class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 1.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface, jump:JUMP):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
        if key_lst[pg.K_SPACE] and jump.on == True:
            jump.speed = jump.up
            jump.on = False

        self.rect.move_ip(self.speed*sum_mv[0], jump.speed)
        if jump.on == False:
            jump.speed += jump.down
            if self.rect.bottom > 600:
                jump.speed = 0
                jump.on = True
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        screen.blit(self.image, self.rect)




def main():
    pg.display.set_caption("はばたけ！こうかとん")
    screen = pg.display.set_mode((800, 600))
    clock  = pg.time.Clock()
    bg_img = pg.image.load("fig/pg_bg.jpg")     #背景画像「pg_bg.jpg」（画像サイズ：幅1600 高さ900）を読み込み，Surfaceを生成せよ．
    bg_flip = pg.transform.flip(bg_img, True, False)
    
    bird = Bird(3, (300, 400))
    tmr = 0
    jump_group = JUMP()

    while True:
        key_lst = pg.key.get_pressed()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 
    
        x = tmr%4800         #こうかとんが画面右に向かって進んでいるように見せるために，背景画像を右から左に動くように，背景画像の横座標を修正せよ．そして，1600フレーム後に背景画像が間延びしないように，工夫せよ．
        screen.blit(bg_img, [-x, 0])    #背景画像を表示せよ．
        screen.blit(bg_flip, [-x+1600, 0])
        screen.blit(bg_img, [-x+3200, 0])    #7
        screen.blit(bg_flip, [-x+4800, 0])
        # screen.blit(k3_img, [-x, 0]) 
        key_lst = pg.key.get_pressed()
        
        bird.update(key_lst, screen, jump_group)
        # screen.blit(k3_img, k3_rct)     #画像SurfaceをスクリーンSurfaceにRectに従って貼り付ける
        pg.display.update()
        tmr += 1        
        clock.tick(200)     #. FPSを200に変更せよ．



if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()