import os
import sys
import pygame as pg

WIDTH = 800
HEIGHT = 600

START = 300

BROWN= (192, 112,  48)

#床の情報を入れるリスト length:床の長さ, height:床のy座標, wid:床の厚さ, start:床の左端
floor_lst = [(300, 700, 30, 200),
             (300, 700, 30, 700),
             (300, 550, 30, 450)]

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

    def update(self, key_lst: list[bool], screen: pg.Surface, floors, jump):
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
        if key_lst[pg.K_SPACE] and jump.on == True:
            jump.speed = jump.up
            jump.on = False
        for flo in pg.sprite.spritecollide(self, floors, False):
            if flo.rect.top+self.speed >= self.rect.bottom >= flo.rect.top-self.speed and sum_mv[1] > 0:
                sum_mv[1] = 0
        self.rect.move_ip(self.speed*sum_mv[0], jump.speed)
        if jump.on == False:
            jump.speed += jump.down
            if self.rect.bottom > 600:
                jump.speed = 0
                jump.on = True
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

class Game:
    def __init__(self):
        # Pygameの初期化
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))  # ウィンドウサイズの設定
        pg.display.set_caption("Super Koukaton")
        
        # ゴール画像の読み込みとスケーリング
        self.goal_img = pg.image.load("fig/goal.png")
        self.goal_img = pg.transform.scale(self.goal_img, (550, 550))
        self.goal_rect = self.goal_img.get_rect()
        self.goal_rect.center = (WIDTH, HEIGHT/2+100)  # ゴールの位置をスクロール先に設定
        
        # フォントとテキストの設定
        self.font = pg.font.Font(None, 74)
        self.goal_text = self.font.render("Game Clearing!", True, (0, 255, 0))
        self.text_rect = self.goal_text.get_rect()
        self.text_rect.center = (WIDTH // 2, 100)
        self.screen_text = self.font.render("Space Start", True, (0, 255, 0))
        self.start_rect = self.screen_text.get_rect()
        self.start_rect.center = (WIDTH // 2, 100)
        
        self.tmr = 0
        self.scroll_y = 0  # スクロール位置を初期化

        # こうかとんの設定
        self.bird = Bird(3, (START, HEIGHT - 100))
        self.all_sprites = pg.sprite.Group(self.bird)
        self.jump = JUMP()
        
    def run(self, screen):
        running = True
        clock = pg.time.Clock()
        while running:
            key_lst = pg.key.get_pressed()
            
            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    running = False
            
            # 画面の塗りつぶし
            screen.fill((0, 0, 0))
            screen.blit(self.screen_text, self.start_rect)
            pg.display.update()


            # 画像とテキストの描画（スクロール位置を考慮）
    def game_update(self, screen, bird):
        self.goal_rect.centerx -= bird.move_tup[0]
        screen.blit(self.goal_img, self.goal_rect)
            


def main():
    pg.display.set_caption("スーパーこうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock  = pg.time.Clock()
    bg_img = pg.image.load("fig/pg_bg.jpg")   
    bg_flip = pg.transform.flip(bg_img, True, False)
    # ここから床を敷く
    floors = pg.sprite.Group()
    floors.add(floor(10000,wid=100, start=START*(-1))) # 最初の床
    for f in floor_lst:
        floors.add(floor(f[0], f[1],f[2],f[3]))
    bird = Bird(3, (START, 400))
    scroll_x = 0  # スクロール機能
    scroll_speed = 5
    tmr = 0
    jump_group = JUMP()
    game = Game()
    game.run(screen)
    
    tmr = 0

    while True:
        key_lst = pg.key.get_pressed()
        
        for event in pg.event.get():
            if event.type == pg.quit: 
                return

    
        key_lst = pg.key.get_pressed()
        if key_lst[pg.K_RIGHT]:  # 画面の中心をこうかとんにし、押下されたキーによって背景画像を移動させる。
            scroll_x -= scroll_speed
        if key_lst[pg.K_LEFT]:
            scroll_x += scroll_speed

        scroll_x = scroll_x % 4800
        screen.fill((0,0,0))
        screen.blit(bg_img, (scroll_x, 0))   
        screen.blit(bg_flip, (scroll_x - 1600, 0))   
        screen.blit(bg_img, (scroll_x - 3200, 0))   
        screen.blit(bg_flip, (scroll_x - 4800, 0))   
        screen.blit(bird.image, bird.rect) 

        if len(pg.sprite.spritecollide(bird, floors, False)) != 0:
            bird.on_floor = True
        bird.update(key_lst, screen, floors, jump_group) # 床のグループを追加で渡す
        # 床のアップデート
        floors.update(bird)
        floors.draw(screen)
        game.game_update(screen, bird)
        pg.display.update()
        tmr += 1        
        clock.tick(60)     #. FPSを200に変更せよ．
        
        if bird.rect.centerx >= game.goal_rect.centerx:
            screen.fill((255, 255, 255))
            screen.blit(game.goal_text, (screen.get_width() // 2 - game.goal_text.get_width() // 2, screen.get_height() // 2 - game.goal_text.get_height() // 2))
            pg.display.update()
            pg.time.wait(2000)
            return



if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()