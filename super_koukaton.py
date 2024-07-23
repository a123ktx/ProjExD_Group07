import os
import sys
import pygame as pg

WIDTH = 800
HEIGHT = 600

START = (300, 300)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BROWN= (192, 112,  48)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

BAG_IMAGE = "fig/pg_bg.jpg"
GOAL_IMAGE = "fig/goal.png"
GOAL_X = WIDTH*2

FPS = 60

#床の情報を入れるリスト length:床の長さ, height:床のy座標, wid:床の厚さ, start:床の左端
floor_lst = [(400, 470, 30, 250),
             (50, 300, 100, 680),
             (250, 200, 50, 800),
             (250, 400, 50, 800),
             (50, 300, 100, 1250), 
             (100, 150, 100, 1500),
             (100, 450, 100, 1500),
             (50, 300, 100, 1750)]

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
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 1.5)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {(+1, 0): img0,
                     (-1, 0): img} # 右 左
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed_x = 10
        self.speed_y = 0
        self.move_x = 0 # こうかとんの移動距離を保存するタプル
        self.where = None # どの床に乗っているか確認する
        self.flip = 1 # 空中で向いている方向を確認する

    def change_img(self, num: int, flip: int):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"),0, 2.0)
        self.flip = flip
        if  flip > 0:
            self.image = pg.transform.flip(self.image, True, False)
            self.flip = flip

    def update(self, key_lst: list[bool], screen: pg.Surface, floors, jump):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items(): # キーリストを方向にしてsum_mvに格納
            if key_lst[k]:
                sum_mv[0] += mv[0]
        # 床に接地していた場合、下に落ちないようにする

        self.check_on_floor(sum_mv[0], key_lst, floors, jump)
        screen.blit(self.image, self.rect)

    def check_on_floor(self, mv: int, key_lst: list[bool], floors, jump):
        for flo in pg.sprite.spritecollide(self, floors, False):
            if flo.rect.top+jump.max_sp >= self.rect.bottom > flo.rect.top-jump.max_sp and self.speed_y > 0:
                self.rect.bottom = flo.rect.top
                self.where = flo
        self.speed_y = Jump.update(jump, self, key_lst, self.speed_y)
        if self.rect.centerx >= WIDTH/2 and mv >= 0: # 画面中央で右に移動したら地形が動くように
            self.rect.move_ip(0, self.speed_y)
            self.move_x = mv*self.speed_x
        elif self.rect.left <= 50 and mv <= 0: # 画面左で左に移動したら地形が移動
            self.rect.move_ip(0, self.speed_y)
            self.move_x = mv*self.speed_x
        else:
            self.rect.move_ip(self.speed_x*mv, self.speed_y)
            self.move_x = 0
        if not self.where:
            if mv != 0:
                self.change_img(3, mv)
            else:
                self.change_img(3, self.flip)
        elif mv != 0 :
            self.dire = (mv, 0)
            self.image = self.imgs[self.dire]
            self.flip = self.dire[0]
        else:
            self.image = self.imgs[(self.flip, 0)]   

# 担当:村上
class Jump():
    """
    ジャンプに関するクラス
    """
    def __init__(self):
        """
        ジャンプのイニシャライザ
        ジャンプの初速、減速度、最高落下速度を管理する
        """
        self.up = -20  # こうかとんのジャンプ力
        self.down = 1  # こうかとんの重力
        self.max_sp = 25 # 落下最高速度
    
    def update(self,bird:Bird, key_lst, now_sp:int):
        if bird.where:
            # 乗っている床の外に出た場合、落ちるように
            if bird.where.rect.left > bird.rect.right-20 or bird.where.rect.right < bird.rect.left+20:
                bird.where = None
                bird.rect.move_ip(0, self.max_sp)
            # 床に乗っている場合、落下速度を0に
            else:
                now_sp = 0
                # 床に接地していた場合、スペースを押すとジャンプできるように
                if key_lst[pg.K_SPACE] and bird.where:
                    now_sp = self.up
                    bird.where = None
        # 床に接地していなければ落ちるように
        elif not bird.where and now_sp < self.max_sp:
            now_sp += self.down
        return now_sp

# 担当:金井
class Floor(pg.sprite.Sprite):
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
        self.rect.move_ip(bird.move_x*(-1), 0)

# 担当:渡邊
class Scroll(pg.sprite.Sprite):
    """
    背景スクロールに関するクラス
    """
    sc_num = 0
    def __init__(self):
        """
        スクロールのイニシャライザ
        横幅1600、縦900の画像を読み込む
        """
        super().__init__()
        self.img = pg.image.load(BAG_IMAGE)
        if __class__.sc_num % 2 == 1:
            self.img = pg.transform.flip(self.img, True, False)
        self.x = -1600 + 1600*__class__.sc_num
        __class__.sc_num += 1

    def update(self, bird:Bird, screen):
        """
        画面を移動、更新する関数
        左右に流れた背景を逆側に持ってくる処理を行っている
        引数1 bird:移動するこうかとん
        引数2 screen:画面
        """
        self.x -= bird.move_x
        if self.x < -3200:
            self.x = 3200
            
        elif self.x > 4800:
            self.x = -1600
        screen.blit(self.img, [self.x, 0])

# 担当:矢本
class Goal(pg.sprite.Sprite):
    """
    ゴールに関するクラス
    """
    def __init__(self):
        """
        ゴールのSurfaceを作成する
        """
        super().__init__()
        # ゴール画像を読み込む
        self.image = pg.image.load(GOAL_IMAGE)
        height = self.image.get_height()
        self.image = pg.transform.rotozoom(self.image, 0, (HEIGHT/height))
        self.rect = self.image.get_rect()
        self.rect.centerx = GOAL_X
        self.rect.y = HEIGHT*0.1
        # ゴール用のテキストを決定する
        self.font = pg.font.Font(None, 74)
        self.text = self.font.render("Game Clearing!", True, GREEN)
        self.text_width = self.text.get_width()
        self.text_height = self.text.get_height()

    def update(self, bird:Bird, screen: pg.Surface):
        """
        ゴールを動かす関数
        引数1 bird:こうかとん
        引数2 screen:画面のSurface
        """
        if self.rect.centerx > bird.rect.centerx:
            self.rect.move_ip(bird.move_x*(-1), 0)
        elif self.rect.centerx <= bird.rect.centerx and bird.move_x >= 0:
            bird.move_x = 0
        screen.blit(self.image, self.rect)

    def check_goal(self, bird:Bird, screen:pg.Surface, clock: pg.time):
        """
        こうかとんがゴールに触れたら、ゲームクリアの処理をする
        引数1 bird:こうかとん
        引数2 screen:画面のSurface
        引数3 clock:ゲームのtime関数 
        """
        if bird.rect.centerx >= self.rect.centerx:
            if bird.rect.colliderect(self.rect):
                tmr = 0
                while tmr < FPS*4:
                    for event in pg.event.get():
                        if event.type == pg.QUIT:
                            pg.quit()
                            sys.exit()
                    screen.fill(WHITE)
                    screen.blit(self.text, (WIDTH/2-self.text_width/2, 
                                            HEIGHT/3-self.text_height/2))
                    pg.display.update()
                    tmr += 1
                    clock.tick(FPS)
                pg.quit()
                sys.exit()

# 担当:村上
class Gameover(pg.sprite.Sprite):
    """
    ゲームオーバーに関するクラス
    """
    def __init__(self):
        """
        ゲームオーバー用のテキストを決定する
        """
        super().__init__()
        # ゲームオーバー用のテキストを決定する
        self.font = pg.font.Font(None, 74)
        self.text = self.font.render("Game Over^^", True, RED)
        self.text_width = self.text.get_width()
        self.text_height = self.text.get_height()
    
    def check_fall(self, bird:Bird, screen:pg.Surface, clock:pg.time):
        """
        こうかとんが下に落ちたかチェックする
        """
        if bird.rect.bottom >= HEIGHT:
            tmr = 0
            while tmr < FPS*4:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()
                screen.fill(BLACK)
                screen.blit(self.text, (WIDTH/2-self.text_width/2, 
                                        HEIGHT/3-self.text_height/2))
                pg.display.update()
                tmr += 1
                clock.tick(FPS)
            pg.quit()
            sys.exit()

# 担当:矢本
class Start(pg.sprite.Sprite):
    """
    ゲームをスタートするクラス
    """
    def __init__(self):
        """
        ゲームを開始する準備をする
        """
        super().__init__()
        # ゲームスタートの確認をする
        self.on = False
        # ゲームスタート用のテキストを決定する
        self.font = pg.font.Font(None, 74)
        self.text = self.font.render("Space Start", True, GREEN)
        self.text_width = self.text.get_width()
        self.text_height = self.text.get_height()
    
    def check_start(self, screen:pg.Surface, clock:pg.time):
        """
        スタートしたかチェックする
        """
        while not self.on:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            key_lst = pg.key.get_pressed()
            screen.fill(WHITE)
            screen.blit(self.text, (WIDTH/2-self.text_width/2, 
                                    HEIGHT/3-self.text_height/2))
            pg.display.update()
            if key_lst[pg.K_SPACE]:
                self.on = True
                return
            clock.tick(FPS)


def main():
    pg.display.set_caption("スーパーこうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock  = pg.time.Clock()
    # ここから背景を設定する
    bgs = pg.sprite.Group()
    for i in range(4):
        bgs.add(Scroll())
    # ここから床を敷く
    floors = pg.sprite.Group()
    # floors.add(Floor(100000,wid=100, start=-10000)) # 最初の床
    for f in floor_lst:
        floors.add(Floor(f[0], f[1], f[2], f[3]))
    bird = Bird(2, START)
    jump = Jump() # ジャンプのイニシャライザを作成
    goal = Goal()
    g_o = Gameover()
    g_s = Start()
    g_s.check_start(screen,clock)
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        bgs.update(bird, screen)
        key_lst = pg.key.get_pressed()
        # こうかとんのアップデート、中で
        bird.update(key_lst, screen, floors, jump)
        # ゴールのアップデート
        goal.update(bird, screen)
        goal.check_goal(bird, screen, clock)
        # ゲームオーバーの判定を行う
        g_o.check_fall(bird, screen, clock)
        # 床のアップデート
        floors.update(bird)
        floors.draw(screen)
        pg.display.update()
        tmr += 1        
        clock.tick(FPS)


if __name__ == "__main__":
    pg.init()
    main()