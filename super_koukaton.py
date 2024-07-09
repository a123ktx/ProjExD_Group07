import os
import sys
import pygame as pg

def main():
    pg.display.set_caption("はばたけ！こうかとん")
    screen = pg.display.set_mode((800, 600))
    clock  = pg.time.Clock()
    bg_img = pg.image.load("fig/pg_bg.jpg")     #背景画像「pg_bg.jpg」（画像サイズ：幅1600 高さ900）を読み込み，surfaceを生成せよ．
    bg_flip = pg.transform.flip(bg_img, True, False)
    k3_img = pg.image.load("fig/3.png")     #こうかとん画像「3.png」を読み込み，surfaceを生成せよ．
    k3_img = pg.transform.flip(k3_img, True, False)   #そして，左右を反転せよ．
    k3_rct = k3_img.get_rect()  #画像surfaceに対応する画像rectを取得する
    k3_rct.center = 300, 200

    goal_img = pg.image.load("fig/goal.png")  # ゴール画像「goal.png」を読み込み，aSurfaceを生成せよ．
    goal_img = pg.transform.scale(goal_img, (550, 550))  # 画像のサイズを変更してウィンドウ内に収める
    goal_rct = goal_img.get_rect()
    goal_rct.center = 600, 350  # ゴールの位置を設定

    font = pg.font.Font(None, 74)
    goal_text = font.render("Game Clearing!", True, (0, 255, 0)) 
    
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.quit: 
                return

        x = tmr%4800         #こうかとんが画面右に向かって進んでいるように見せるために，背景画像を右から左に動くように，背景画像の横座標を修正せよ．そして，1600フレーム後に背景画像が間延びしないように，工夫せよ．
        screen.blit(bg_img, [-x, 0])    #背景画像を表示せよ．
        screen.blit(bg_flip, [-x+1600, 0])
        screen.blit(bg_img, [-x+3200, 0])
        screen.blit(bg_flip, [-x+4800, 0])
        # screen.blit(k3_img, [-x, 0]) 
        key_lst = pg.key.get_pressed()
        a = [0, 0]
        if key_lst[pg.K_UP]:
            a[0] = -1
            a[1] = -1
        elif key_lst[pg.K_DOWN]:
            a[0] = -1
            a[1] = 1            
        elif key_lst[pg.K_RIGHT]:
            a[0] = 2
            a[1] = 0            
        elif key_lst[pg.K_LEFT]:
            a[0] = -1
            a[1] = 0
        else:
            a[0] = -1
            a[1] = 0
        k3_rct.move_ip(a)  #横300，縦200の位置に，こうかとんsurfaceをblitせよ．
        
        if k3_rct.centerx >= goal_rct.centerx:
            pg.time.wait(2000)
            screen.fill((255, 255, 255))
            clear_text = font.render("Game Clearing!", True, (0, 255, 0))
            screen.blit(clear_text, (screen.get_width() // 2 - clear_text.get_width() // 2, screen.get_height() // 2 - clear_text.get_height() // 2))
            pg.display.update()
            pg.time.wait(2000)
            return
                
        screen.blit(k3_img, k3_rct)   #画像surfaceをスクリーンsurfaceにrectに従って貼り付ける
        screen.blit(goal_img, goal_rct)
        pg.display.update()
        tmr += 1        
        clock.tick(200)     #. fpsを200に変更せよ．



if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()