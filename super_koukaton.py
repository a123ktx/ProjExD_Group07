import os
import sys
import pygame as pg

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def main():
    pg.display.set_caption("はばたけ！こうかとん")
    screen = pg.display.set_mode((800, 600))
    clock  = pg.time.Clock()
    bg_img = pg.image.load("fig/pg_bg.jpg")   
    bg_flip = pg.transform.flip(bg_img, True, False)
    k3_img = pg.image.load("fig/3.png")     
    k3_img = pg.transform.flip(k3_img, True, False)   
    k3_rct = k3_img.get_rect()  # 画像Surfaceに対応する画像Rectを取得する
    k3_rct.center = 400, 200    
    tmr = 0
    scroll_x = 0
    scroll_speed = 5

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
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
        screen.blit(k3_img, k3_rct)  # 画像SurfaceをスクリーンSurfaceにRectに従って貼り付ける
        pg.display.update()
        tmr += 1        
        clock.tick(60)     


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()