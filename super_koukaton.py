import os
import sys
import pygame as pg

WIDTH = 1600
HEIGHT = 900

START = 300

BROWN= (192, 112,  48)

#床の情報を入れるリスト length:床の長さ, height:床のy座標, wid:床の厚さ, start:床の左端
floor_lst = [(300, 700, 30, 200),
             (300, 700, 30, 700),
             (300, 550, 30, 450)]

os.chdir(os.path.dirname(os.path.abspath(__file__)))

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
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): img,  # 右上
            (0, -1): img,  # 上
            (-1, -1): img0,  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): img0,  # 左下
            (0, +1): img,  # 下
            (+1, +1): img,  # 右下
        }

        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10
        self.move_tup = () # こうかとんの移動距離を保存するタプル

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface, floors):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        # 床に接地していた場合、下に落ちないようにする
        for flo in pg.sprite.spritecollide(self, floors, False):
            if flo.rect.top+self.speed >= self.rect.bottom >= flo.rect.top-self.speed and sum_mv[1] > 0:
                sum_mv[1] = 0
        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        self.move_tup = (sum_mv[0]*self.speed, sum_mv[1]*self.speed)
        screen.blit(self.image, self.rect)

# 床を実装　金井
class floor(pg.sprite.Sprite):
    """
    床に関するクラス
    """
    def __init__(self, length:int, height:int=HEIGHT, wid:int=30, start:int=0):
        """
        床の線を描画する
        引数1 length:床の長さ
        引数2 height:床の高さ
        引数3 wid:床の厚さ
        引数4 start:床の左端
        """
        super().__init__()
        self.image = pg.Surface((length, wid))
        pg.draw.line(self.image, BROWN, [0,0], [length,0], wid)
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.left = start
        self.rect.centery = height 

    def update(self, bird:Bird):
        """
        こうかとんの移動に合わせて床を移動させる関数
        引数1 bird:こうかとんの情報
        """
        self.rect.move_ip(bird.move_tup[0]*(-1), 0)


def main():
    pg.display.set_caption("スーパーこうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock  = pg.time.Clock()
    bg_img = pg.image.load("fig/pg_bg.jpg")     #背景画像「pg_bg.jpg」（画像サイズ：幅1600 高さ900）を読み込み，Surfaceを生成せよ．
    bg_flip = pg.transform.flip(bg_img, True, False)
    # ここから床を敷く
    floors = pg.sprite.Group()
    floors.add(floor(10000,wid=100, start=START*(-1))) # 最初の床
    for f in floor_lst:
        floors.add(floor(f[0], f[1],f[2],f[3]))
    bird = Bird(3, (START, 400))
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return

        x = tmr%4800         #こうかとんが画面右に向かって進んでいるように見せるために，背景画像を右から左に動くように，背景画像の横座標を修正せよ．そして，1600フレーム後に背景画像が間延びしないように，工夫せよ．
        screen.blit(bg_img, [-x, 0])    #背景画像を表示せよ．
        screen.blit(bg_flip, [-x+1600, 0])
        screen.blit(bg_img, [-x+3200, 0])    #7
        screen.blit(bg_flip, [-x+4800, 0])
        key_lst = pg.key.get_pressed()
        if len(pg.sprite.spritecollide(bird, floors, False)) != 0:
            bird.on_floor = True
        bird.update(key_lst, screen, floors) # 床のグループを追加で渡す
        # 床のアップデート
        floors.update(bird)
        floors.draw(screen)
        pg.display.update()
        tmr += 1        
        clock.tick(60)     #. FPSを200に変更せよ．


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()