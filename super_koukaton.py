import os
import sys
import pygame as pg

WIDTH = 800
HEIGHT = 600

START = 300

BROWN= (192, 112,  48)

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

        __class__.check_on_floor(self, sum_mv[0], key_lst, floors, jump)
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
        self.rect.move_ip(-bird.move_x, 0)

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
        self.goal_rect.center = (WIDTH*3, HEIGHT/2+100)  # ゴールの位置をスクロール先に設定
        
        # フォントとテキストの設定
        self.font = pg.font.Font(None, 74)
        self.goal_text = self.font.render("Game Clearing!", True, (0, 255, 0))
        self.text_rect = self.goal_text.get_rect()
        self.text_rect.center = (WIDTH // 2, 100)
        self.screen_text = self.font.render("Space Start", True, (0, 255, 0))
        self.start_rect = self.screen_text.get_rect()
        self.start_rect.center = (WIDTH // 2, 100)
    
        
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
        self.goal_rect.centerx -= bird.move_x
        screen.blit(self.goal_img, self.goal_rect)
            


def main():
    pg.display.set_caption("スーパーこうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock  = pg.time.Clock()
    bg_img = pg.image.load("fig/pg_bg.jpg")   
    bg_flip = pg.transform.flip(bg_img, True, False)
    # ここから床を敷く
    floors = pg.sprite.Group()
    # floors.add(floor(10000,wid=50, start=START*(-1))) # 最初の床
    for f in floor_lst:
        floors.add(floor(f[0], f[1],f[2],f[3]))
    bird = Bird(2, (START, 400))
    scroll_x = 0  # スクロール機能
    scroll_speed = 5
    tmr = 0
    jump = Jump()
    font = pg.font.Font(None, 74)
    gameover_text = font.render("Game Over ^^", True, (255, 0, 0))
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
        bird.update(key_lst, screen, floors, jump) # 床、ジャンプのグループを追加で渡す
        # 床のアップデート
        floors.update(bird)
        floors.draw(screen)

        # ゲームオーバー画面の表示
        if bird.rect.bottom >= HEIGHT:
            pg.time.wait(500)
            screen.fill((0, 0, 0))
            text_posi = (screen.get_width() // 2 - gameover_text.get_width() // 2,
                         screen.get_height() // 2 - gameover_text.get_height() // 2)
            screen.blit(gameover_text, (text_posi))
            pg.display.update()
            pg.time.wait(2000)
            return
        
        game.game_update(screen, bird)
        pg.display.update()
        tmr += 1        
        clock.tick(60)    
        
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