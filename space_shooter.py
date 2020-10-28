import pyxel
import random
import AI

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
GAME_TITLE = "AI Space Shooter"
AI_MODE_ENABLED = False
ai = AI.Kalman(25)


def draw_text_centered(text, y, col=7):
    pyxel.text(pyxel.width/2 - len(text)*2, y, text, 7)


class Background:
    speed = -0.5

    def __init__(self):
        self.stars = list()
        for i in range(110):
            x = random.randrange(0, pyxel.width, 2)
            y = random.randrange(0, pyxel.height, 2)
            col = random.choice([7, 6, 15, 13])
            self.stars.append([x, y, col])

    def update(self):
        for i in range(len(self.stars)):
            self.stars[i][0] += self.speed
            if self.stars[i][0] < 0:
                self.stars[i][0] = pyxel.width
                self.stars[i][1] = random.randrange(0, pyxel.height, 2)

    def draw(self):
        for (x, y, col) in self.stars:
            pyxel.pset(x, y, col)


class Player:
    moving_speed = 1.5
    size = 8

    def __init__(self):
        self.x = 10
        self.y = pyxel.height/2
        self.alive = True

    def update(self):
        # moving controlls
        if pyxel.btn(pyxel.KEY_UP) or ai.up:
            self.y -= self.moving_speed
            ai.up = False

        if pyxel.btn(pyxel.KEY_DOWN) or ai.down:
            self.y += self.moving_speed
            ai.down = False

        if self.y < 0:
            self.y = 0

        if self.y > pyxel.height-self.size:
            self.y = pyxel.height-self.size

        # shooting controlls
        if pyxel.btnp(pyxel.KEY_SPACE) or ai.shoot:
            Bullet.shoot_player()
            ai.shoot = False
        self.up = False
        self.down = False
        self.shoot = False

    def draw(self):
        #pyxel.rect(self.x, self.y, self.size, self.size, 9)
        pyxel.blt(self.x, self.y, 0, 0, 8, self.size, self.size, colkey=0)

    def hit(self):
        self.alive = False
        pyxel.play(0, 2)
        global CURRENT_SCREEN
        CURRENT_SCREEN = "game_over"

class Bullet:
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
        if AI_MODE_ENABLED:
            search = False
            if self.aggresive:
                search = True
            count = 0
            if search:
                for i in range(len(ai.bullets)):
                    count = i
                    if ai.bullets[i][0] == self.x and ai.bullets[i][1] == self.y:
                        ai.bullets[i][0] += self.speed
                        break
                
                
        # moving
        self.x += self.speed

        # freeing memory
        if self.x > pyxel.width or self.x < -self.width:
            BULLETS.remove(self)
            if AI_MODE_ENABLED:
                if search:
                    del ai.bullets[count]

        # hitting logic
        if not self.aggresive:
            for enemy in ENEMIES:
                if enemy.x < self.x+self.width < enemy.x+enemy.size and\
                        enemy.y-self.height < self.y < enemy.y+enemy.size:

                    pyxel.play(0, 0)
                    enemy.hit()
                    # error happen if you hit two enemies at the same time
                    try:
                        BULLETS.remove(self)
                    except:
                        pass
        else:
            if PLAYER.x < self.x < PLAYER.x+PLAYER.size and\
                    PLAYER.y-self.height < self.y < PLAYER.y+PLAYER.size:
                PLAYER.hit()
                BULLETS.remove(self)
                if AI_MODE_ENABLED:
                    if search:
                        del ai.bullets[count]

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
        if AI_MODE_ENABLED:
            ai.bullets.append([bl.x,bl.y, 0])


class Bullet_Diagonal(Bullet):

    def __init__(self, x, y, agressive, up):
        super().__init__(x, y, agressive)
        self.speed_y = self.speed*(1 if up else -1)*0.5

    def update(self):
        if AI_MODE_ENABLED:
            count = 0
            for i in range(len(ai.bullets)):
                if ai.bullets[i][0] == self.x and ai.bullets[i][1] == self.y:
                    ai.bullets[i][1] += self.speed_y
                    break
                count = i

        self.y += self.speed_y
        if self.y < -self.height or self.y > pyxel.height:
            BULLETS.remove(self)
            if AI_MODE_ENABLED:
                del ai.bullets[count]
        super().update()

    @classmethod
    def shoot_enemy(cls, x, y, up):
        bl = cls(x, y, True, up)
        BULLETS.append(bl)
        if AI_MODE_ENABLED:
            if bl.speed_y > 0:
                ai.bullets.append([bl.x, bl.y, 1])
            elif bl.speed_y < 0:
                ai.bullets.append([bl.x, bl.y, -1])

class Enemy:
    size = 8
    speed = -0.5

    def __init__(self, y):
        self.y = y
        self.x = pyxel.width+self.size

    def update(self):
        if AI_MODE_ENABLED:
            count = 0
            for i in range(len(ai.enemy_positions)):
                count = i
                if ai.enemy_positions[i][0] == self.x and ai.enemy_positions[i][1] == self.y:
                    ai.enemy_positions[i][0] += self.speed
                    break
            
        self.x += self.speed

        if self.x < -self.size:
            ENEMIES.remove(self)
            if AI_MODE_ENABLED:
                del ai.enemy_positions[count]
    def draw(self):
        #pyxel.rect(self.x, self.y, self.size, self.size, 11)
        pyxel.blt(self.x, self.y, 0, 8, self.draw_y,
                  self.size, self.size, colkey=0)

    def hit(self):
        global SCORE
        SCORE += self.point_value
        ENEMIES.remove(self)
        if AI_MODE_ENABLED:
            count = 0
            for i in range(len(ai.enemy_positions)):
                count = i
                if ai.enemy_positions[i][0] == self.x and ai.enemy_positions[i][1] == self.y:
                    del ai.enemy_positions[count]
                    break
        

    @classmethod
    def spawn_random(cls):
        return cls(random.randrange(pyxel.height-cls.size))


class Enemy_Basic(Enemy):
    point_value = 10
    draw_y = 0


class Enemy_Agressive(Enemy):
    point_value = 40
    draw_y = 8
    fire_rate = 3

    def __init__(self, y):
        super().__init__(y)
        self.offset = random.randint(1, FPS*self.fire_rate)

    def update(self):
        super().update()
        if pyxel.frame_count % (FPS*self.fire_rate) == self.offset:
            Bullet.shoot_enemy(self.x, self.y+self.size/2)


class Enemy_Moving(Enemy):
    point_value = 20
    draw_y = 16
    fire_rate = 3
    move_chance = 50
    move_rate = 2

    def __init__(self, y):
        super().__init__(y)
        self.move_distance = self.size
        self.offset = random.randint(1, FPS*self.fire_rate)

    def update(self):
        super().update()
        
        if pyxel.frame_count % (FPS*self.move_rate) == self.offset:
            roll = random.randint(0, 100)
            if roll <= self.move_chance:
                self.y += self.move_distance * \
                    (1 if roll <= self.move_chance/2 else -1)
        

        if pyxel.frame_count % (FPS*self.fire_rate) == self.offset:
            Bullet.shoot_enemy(self.x, self.y+self.size/2)


class Enemy_Diagonal(Enemy):
    point_value = 50
    draw_y = 24

    fire_rate = 3

    def __init__(self, y):
        super().__init__(y)
        self.offset = random.randint(1, FPS*self.fire_rate)

    def update(self):
        super().update()
        if pyxel.frame_count % (FPS*self.fire_rate) == self.offset:
            Bullet_Diagonal.shoot_enemy(self.x, self.y+self.size/2, True)
            Bullet_Diagonal.shoot_enemy(self.x, self.y+self.size/2, False)


class Spawner:

    enemy_spawn_rates = {
        Enemy_Basic:     [[0, 2], [1, 2], [1, 2], [2, 4]],
        Enemy_Agressive: [[0, 0], [0, 1], [1, 2], [1, 2]],
        Enemy_Moving:    [[0, 0], [0, 0], [0, 1], [0, 3]],
        Enemy_Diagonal:  [[0, 0], [0, 0], [0, 1], [1, 2]]
    }

    def update(self):
        if pyxel.frame_count % (FPS*2) == 0:  # each wave
            # difficulty scaling
            if 0 <= SCORE <= 50:
                phase = 0
            elif 50 < SCORE <= 150:
                phase = 1
            elif 150 < SCORE <= 300:
                phase = 2
            else:
                phase = 3

            # enemy spawning
            for enemt_type in self.enemy_spawn_rates:
                amount = random.randint(
                    *self.enemy_spawn_rates[enemt_type][phase])
                for i in range(amount):
                    ENEMIES.append(enemt_type.spawn_random())
                    if AI_MODE_ENABLED:
                        ai.enemy_positions.append([ENEMIES[len(ENEMIES) - 1].x, ENEMIES[len(ENEMIES) - 1].y, ENEMIES[len(ENEMIES) - 1].point_value, ENEMIES[len(ENEMIES) - 1].size/2, 0])


class App:
    def __init__(self):
        # pyxel init
        pyxel.init(256, 120, fps=FPS, caption=GAME_TITLE)
        pyxel.load("tmp.pyxres")
        # game init
        global PLAYER
        PLAYER = Player()
        ai.PLAYER_POSITION = []
        ai.PLAYER_POSITION.append(PLAYER.x)
        ai.PLAYER_POSITION.append(PLAYER.y)
        self.spawner = Spawner()
        self.background = Background()
        self.game_mode = 0
        # game start
        pyxel.run(self.update, self.draw)
        ai.win_height = pyxel.height/2

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
        # update background
        self.background.update()
        # enmy spawn logic
        self.spawner.update()
        # update objects
        PLAYER.update()
        for bullet in BULLETS:
            bullet.update()
        for enemy in ENEMIES:
            enemy.update()
        if AI_MODE_ENABLED:
            ai.PLAYER_POSITION = []
            ai.PLAYER_POSITION.append(PLAYER.x)
            ai.PLAYER_POSITION.append(PLAYER.y)
            ai.take_action()

    def draw_main(self):
        pyxel.cls(0)
        # background
        self.background.draw()
        # Objects
        PLAYER.draw()
        for bullet in BULLETS:
            bullet.draw()
        for enemy in ENEMIES:
            enemy.draw()
        # HUD
        pyxel.text(10, 5, str(SCORE), 7)

    def update_title(self):
        if pyxel.btnp(pyxel.KEY_UP):
            self.game_mode += 1

        if pyxel.btnp(pyxel.KEY_DOWN):
            self.game_mode -= 1

        self.game_mode %= 2

        if pyxel.btnp(pyxel.KEY_ENTER):

            global AI_MODE_ENABLED
            if self.game_mode == 1:
                ai.on = False
                AI_MODE_ENABLED = False
            else:
                ai.on = True
                AI_MODE_ENABLED = True

            global CURRENT_SCREEN
            CURRENT_SCREEN = "main"

    def draw_title(self):
        pyxel.cls(0)
        self.background.draw()
        draw_text_centered(GAME_TITLE.upper(), pyxel.height*0.25)
        if self.game_mode == 1:
            offset = 0.7
        else:
            offset = 0.8
        draw_text_centered("-          -", pyxel.height*offset)
        draw_text_centered("PLAY HUMAN", pyxel.height*0.7)
        draw_text_centered("PLAY AI", pyxel.height*0.8)
        #draw_text_centered("- PRESS ENTER -", pyxel.height*0.75)

    def update_game_over(self):
        if pyxel.btnp(pyxel.KEY_R):
            global SCORE
            SCORE = 0
            global PLAYER
            PLAYER = Player()
            global ENEMIES
            ENEMIES = []
            global BULLETS
            BULLETS = []
            global CURRENT_SCREEN
            CURRENT_SCREEN = 'main'
            if AI_MODE_ENABLED:
                ai.enemy_positions = []
                ai.bullets = []
                ai.PLAYER_POSITION = []
                ai.PLAYER_POSITION.append(PLAYER.x)
                ai.PLAYER_POSITION.append(PLAYER.y)
                            
                ai.up = False
                ai.down = False
                ai.shoot = False
                
                ai.enemies_in_range = 0

    def draw_game_over(self):
        pyxel.cls(0)
        self.background.draw()
        for bullet in BULLETS:
            bullet.draw()
        for enemy in ENEMIES:
            enemy.draw()
        draw_text_centered("GAME OVER", pyxel.height*0.25)
        draw_text_centered(f"SCORE: {SCORE}", pyxel.height*0.5)
        draw_text_centered("- PRESS R TO RESTART -", pyxel.height*0.75)


if __name__ == '__main__':
    """
    while(True):
        mode = input("Enter A for AI player or H for Human ")
        if mode != "A" and mode !="a" and mode != "H" and mode != "h":
            print("Please enter a valid input")
        elif  mode == "A" or mode =="a":
            ai.on = True
            break
        elif mode == "H" or mode == "h":
            ai.on = False
            break
    """
    App()
