import pyxel
import random

"""
sounds
0 - destroy_asteroid
1 - shoot_bullet
2 - game_Over
"""


BULLETS = []
ENEMIES = []
SCORE = 0
PLAYER = None
FPS = 60
CURRENT_SCREEN = "title"


def draw_text_centered(text, y, col=7):
    pyxel.text(pyxel.width/2 - len(text)*2, y, text, 7)


class Player():
    moving_speed = 1.5
    size = 8

    def __init__(self):
        self.x = 10
        self.y = pyxel.height/2
        self.alive = True

    def update(self):
        # moving controlls
        if pyxel.btn(pyxel.KEY_UP):
            self.y -= self.moving_speed

        if pyxel.btn(pyxel.KEY_DOWN):
            self.y += self.moving_speed

        if self.y < 0:
            self.y = 0

        if self.y > pyxel.height-self.size:
            self.y = pyxel.height-self.size

        # shooting controlls
        if pyxel.btnp(pyxel.KEY_SPACE):
            Bullet.shoot_player()

    def draw(self):
        #pyxel.rect(self.x, self.y, self.size, self.size, 9)
        pyxel.blt(self.x, self.y, 0, 0, 8, self.size, self.size, colkey=0)

    def hit(self):
        self.alive = False
        pyxel.play(0, 2)
        global CURRENT_SCREEN
        CURRENT_SCREEN = "game_over"


class Bullet():
    speed = 2
    height = 2
    width = 5

    def __init__(self, x, y, agressive):
        pyxel.play(0, 1)
        self.x = x
        self.y = y - self.height/2
        self.aggresive = agressive
        if agressive:
            self.speed *= -1

    def update(self):
        # moving
        self.x += self.speed

        # freeing memory
        if self.x > pyxel.width or self.x < -self.width:
            BULLETS.remove(self)

        # hitting logic
        if not self.aggresive:
            for enemy in ENEMIES:
                if enemy.x < self.x+self.width < enemy.x+enemy.size and\
                        enemy.y-self.height < self.y < enemy.y+enemy.size:

                    pyxel.play(0, 0)
                    enemy.hit()
                    try:
                        BULLETS.remove(self)
                    except:  # error happen if you hit two enemies at the same time
                        pass
        else:
            if PLAYER.x < self.x < PLAYER.x+PLAYER.size and\
                    PLAYER.y-self.height < self.y < PLAYER.y+PLAYER.size:
                PLAYER.hit()
                BULLETS.remove(self)

    def draw(self):
        pyxel.rect(self.x, self.y, self.width, self.height, 3)

    @classmethod
    def shoot_player(cls):
        bl = cls(PLAYER.x+PLAYER.size, PLAYER.y+PLAYER.size/2, False)
        BULLETS.append(bl)

    @classmethod
    def shoot_enemy(cls, x, y):
        bl = cls(x, y, True)
        BULLETS.append(bl)


class Spawner():
    def update(self):
        if pyxel.frame_count % (FPS*2) == 0:  # each wave

            # passive enemies
            amount = random.randint(1, 3)
            for i in range(amount):
                ENEMIES.append(Enemy_Basic.spawn_random())

            # active enemies
            amount = random.randrange(1, 2, step=8)
            for i in range(amount):
                ENEMIES.append(Enemy_Agressive.spawn_random())


class Enemy_Basic():
    size = 8
    speed = -0.5
    point_value = 10

    def __init__(self, y):
        self.y = y
        self.x = pyxel.width+self.size

    def update(self):
        self.x += self.speed

    def draw(self):
        #pyxel.rect(self.x, self.y, self.size, self.size, 11)
        pyxel.blt(self.x, self.y, 0, 8, 0, self.size, self.size, colkey=0)

    def hit(self):
        global SCORE
        SCORE += self.point_value
        ENEMIES.remove(self)

    @classmethod
    def spawn_random(cls):
        return cls(random.randrange(pyxel.height-cls.size))


class Enemy_Agressive():
    size = 8
    speed = -0.5
    point_value = 20
    fire_rate = 3

    def __init__(self, y):
        self.y = y
        self.x = pyxel.width+self.size
        self.offset = random.randint(1, FPS*self.fire_rate)

    def update(self):
        self.x += self.speed
        if pyxel.frame_count % (FPS*self.fire_rate) == self.offset:
            Bullet.shoot_enemy(self.x, self.y+self.size/2)

    def draw(self):
        #pyxel.rect(self.x, self.y, self.size, self.size, 11)
        pyxel.blt(self.x, self.y, 0, 8, 8, self.size, self.size, colkey=0)

    def hit(self):
        global SCORE
        SCORE += self.point_value
        ENEMIES.remove(self)

    @classmethod
    def spawn_random(cls):
        return cls(random.randrange(pyxel.height-cls.size))


class App:
    def __init__(self):
        # pyxel init
        pyxel.init(256, 90, fps=FPS, caption="AI shooter")
        pyxel.load("tmp.pyxres")
        # game init
        global PLAYER
        PLAYER = Player()
        self.spawner = Spawner()
        # game start
        pyxel.run(self.update, self.draw)

    def update(self):
        if CURRENT_SCREEN == 'title':
            self.update_title()
        elif CURRENT_SCREEN == "main":
            self.update_main()
        elif CURRENT_SCREEN == "game_over":
            self.update_game_over()
        else:
            print("Unknown screen", CURRENT_SCREEN)
            pyxel.quit()

    def draw(self):
        if CURRENT_SCREEN == "title":
            self.draw_title()
        elif CURRENT_SCREEN == "main":
            self.draw_main()
        elif CURRENT_SCREEN == "game_over":
            self.draw_game_over()
        else:
            print("Unknown screen", CURRENT_SCREEN)
            pyxel.quit()

    def update_main(self):
        if not PLAYER.alive:
            return
        # enmy spawn logic
        self.spawner.update()
        # update objects
        PLAYER.update()
        for bullet in BULLETS:
            bullet.update()
        for enemy in ENEMIES:
            enemy.update()

    def draw_main(self):
        pyxel.cls(0)
        # Objects
        PLAYER.draw()
        for bullet in BULLETS:
            bullet.draw()
        for enemy in ENEMIES:
            enemy.draw()
        # HUD
        pyxel.text(10, 5, str(SCORE), 7)

    def update_title(self):
        if pyxel.btnp(pyxel.KEY_ENTER):
            global CURRENT_SCREEN
            CURRENT_SCREEN = "main"

    def draw_title(self):
        pyxel.cls(0)
        draw_text_centered("HELLO WORLD", pyxel.height*0.25)
        draw_text_centered("- PRESS ENTER -", pyxel.height*0.75)

    def update_game_over(self):
        pass

    def draw_game_over(self):
        pyxel.cls(0)
        draw_text_centered("GAME OVER", pyxel.height*0.25)
        draw_text_centered(f"SCORE: {SCORE}", pyxel.height*0.75)


if __name__ == '__main__':
    App()
