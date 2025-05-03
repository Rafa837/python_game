import pgzrun
from pygame import Rect

class Platform:
    def __init__(self, x, y):
        self.actor = Actor("platform1.png")
        self.actor.topleft = (x, y)
    
    def draw(self):
        original_pos = self.actor.pos
        self.actor.pos = (self.actor.x - camera_offset[0], self.actor.y - camera_offset[1])
        self.actor.draw()
        self.actor.pos = original_pos
    
    def get_rect(self):
        return Rect(self.actor.topleft, self.actor.size)
        
class Hero:
    def __init__(self):
        self.lives = 3
        self.invincible = False
        self.invincibility_timer = 0
        self.pos = [100, 300]
        self.vel_y = 0
        self.on_ground = False
        self.direction = "right"
        self.frame = 0
        self.timer = 0
        self.state = "idle"
        self.gravity = 0.5
        self.jump_strength = -10
        self.ground_level = 300
        self.images_idle = [Actor("shadow_idle1.png"),Actor("shadow_idle2.png"),Actor("shadow_idle3.png"),Actor("shadow_idle4.png"),Actor("shadow_idle5.png"),Actor("shadow_idle6.png")]
        self.images_run = [Actor("shadow_run1.png"),Actor("shadow_run2.png"),Actor("shadow_run3.png"),Actor("shadow_run4.png"),Actor("shadow_run5.png")]
        self.images_jump = [Actor("shadow_jump1.png"),Actor("shadow_jump2.png"),Actor("shadow_jump3.png"),Actor("shadow_jump4.png"),Actor("shadow_jump5.png"),Actor("shadow_jump6.png")]
    
    def update(self):
        previous_state = self.state
        keys = keyboard
        speed = 3

        moving = False
        if keys.right:
            self.pos[0] += speed
            self.direction = "right"
            self.state = "run"
            moving = True
        elif keys.left:
            platform_limit = platforms[0].actor.left
            if self.pos[0] - 20 > platform_limit:
                self.pos[0] -= speed
                self.direction = "left"
                self.state = "run"
                moving = True

        if keys.up and self.on_ground:
            self.vel_y = self.jump_strength
            self.on_ground = False
            if sound_on:
                sounds.jump.play()
                sounds.jump.set_volume(0.5)

        self.vel_y += self.gravity
        self.pos[1] += self.vel_y

        for platform in platforms:
            platform_rect = platform.get_rect()
            hero_rect = Rect((self.pos[0] - 20, self.pos[1]), (40, 1))

            if hero_rect.colliderect(platform_rect) and self.vel_y >= 0:
                self.pos[1] = platform_rect.top
                self.vel_y = 0
                self.on_ground = True
                break
        
        if self.pos[1] >= self.ground_level:
            self.pos[1] = self.ground_level
            self.vel_y = 0
            self.on_ground = True
        
        if self.invincible:
            self.invincibility_timer += 1
            if self.invincibility_timer > 60:
                self.invincible = False
                self.invincibility_timer = 0

        self.timer += 1
        if self.timer % 10 == 0:
            current_images = self.get_current_images()
            self.frame = (self.frame + 1) % len(current_images)
        
        if self.state != previous_state:
            self.frame = 0

        if not self.on_ground:
            self.state = "jump"
        elif keyboard.left or keyboard.right:
            self.state = "run"
        else:
            self.state = "idle"

    def get_current_images(self):
        if not self.on_ground:
            return self.images_jump
        elif self.state == "run":
            return self.images_run
        else:
            return self.images_idle  

    def draw(self):
        if self.invincible and (self.invincibility_timer // 5) % 2 == 0:
            return
        img = self.get_current_images()[self.frame]
        img.pos = (self.pos[0] - camera_offset[0], self.pos[1] - camera_offset[1])
        img.flip_x = (self.direction == "left")
        img.draw()

class Enemy:
    def __init__(self, x, y, patrol_range):
        self.pos = [x, y]
        self.patrol_range = patrol_range
        self.direction = "left"
        self.frame = 0
        self.timer = 0
        self.speed = 2
        self.state = "walk"
        self.images_walk = [Actor("enemy_walk1.png"), Actor("enemy_walk2.png")]
        self.images_idle = [Actor("enemy_idle1.png"), Actor("enemy_idle2.png")]
        self.start_x = x

        self.paused = False
        self.pause_timer = 0
        self.pause_duration = 120

        self.move_timer = 0
        self.move_duration = 180
    
    def get_current_images(self):
        if self.paused:
            return self.images_idle
        return self.images_walk
    
    def update(self):
        self.timer += 1

        if self.paused:
            self.pause_timer += 1
            if self.pause_timer >= self.pause_duration:
                self.paused = False
                self.pause_timer = 0
                self.move_timer = 0
        else:
            self.move_timer += 1
            if self.move_timer >= self.move_duration:
                self.paused = True
                self.move_timer = 0

        if self.timer % 10 == 0:
            self.frame = (self.frame + 1) % len(self.get_current_images())
        
        if self.paused:
            return
        
        if self.direction == "left":
            self.pos[0] -= self.speed
            if self.pos[0] < self.start_x - self.patrol_range:
                self.direction = "right"
        else:
            self.pos[0] += self.speed
            if self.pos[0] > self.start_x + self.patrol_range:
                self.direction = "left"
    
    def draw(self):
        img = self.get_current_images()[self.frame]
        img.pos = (self.pos[0] - camera_offset[0], self.pos[1] - camera_offset[1])
        img.flip_x = (self.direction == "right")
        img.draw()

class GoalItem:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.collected = False
        self.image = Actor("emeralds.png")
        self.image.pos = self.pos

    def draw(self):
        if not self.collected:
            self.image.pos = (self.pos[0] - camera_offset[0], self.pos[1] - camera_offset[1])
            self.image.draw()

    def check_collision(self, hero_pos):
        hero_rect = Rect(hero_pos, (30,60))
        item_rect = Rect(self.pos, (30, 30))
        return hero_rect.colliderect(item_rect)

goal_item = GoalItem(990, 171)

hero = Hero()

camera_offset = [0, 0]

enemies = [
    Enemy(250, 300, 60),
    Enemy(700, 250, 70),
    Enemy(885, 200, 70)
]

platforms = [
    Platform(50, 300),
    Platform(240, 300),
    Platform(430, 300),
    Platform(620, 250),
    Platform(810, 200)
]

WIDTH = 800
HEIGHT = 600
TITLE = "Shadow Awakens"

restart_button = Rect((WIDTH // 2 - 100, 220), (200, 50))
quit_button = Rect((WIDTH // 2 - 100, 290), (200, 50))
gameover_restart_button = Rect((WIDTH // 2 - 100, 200), (200, 50))

#Estados do jogo
game_state = 'menu'
sound_on = True
victory_music_played = False
defeat_sound_played = False

#Botões
start_button = Rect((WIDTH // 2 - 100, 150), (200, 50))
sound_button = Rect((WIDTH // 2 - 100, 220), (200, 50))
exit_button = Rect((WIDTH // 2 - 100, 290), (200, 50))

#Música
music.play('background_music.mp3')
music.set_volume(0.3) 

def update():
    global game_state

    if game_state not in ["playing"]:
        return
    
    if game_state == "playing":
        hero.update()
        update_camera()
    for enemy in enemies:
        enemy.update()
    check_collisions()

    if not goal_item.collected and goal_item.check_collision(hero.pos):
       goal_item.collected = True
       change_game_state("win")
    elif game_state == "gameover":
        global defeat_sound_played
        if not defeat_sound_played:
            music.play("defeat.mp3")
            defeat_sound_played = True

def change_game_state(state):
    global game_state, hero, enemies, victory_music_played
    game_state = state

    if state == "playing":
        hero = Hero()
        enemies = [
            Enemy(400, 200, 60),
            Enemy(600, 100, 70)
        ]
        victory_music_played = False
        if sound_on:
            music.play("background_music.mp3")
    
    elif state == "win":
        if not victory_music_played:
            music.stop()
            if sound_on:
                music.play_once("victory.mp3")
                music.set_volume(0.3)
            victory_music_played = True

def update_camera():
        camera_offset[0] = hero.pos[0] - WIDTH // 2
        camera_offset[1] = hero.pos[1] - HEIGHT // 2

def check_collisions():
        global game_state
        for enemy in enemies:
            hero_rect = Rect(hero.pos, (20, 60))
            enemy_rect = Rect(enemy.pos, (20, 60))
            if hero_rect.colliderect(enemy_rect) and not hero.invincible:
                hero.lives -= 1
                hero.invincible = True
                if sound_on:
                    sounds.hit.play()
                    sounds.hit.set_volume(0.5)
                print(f"Vidas restantes: {hero.lives}")
                if hero.lives <= 0:
                    game_state = "gameover"
                    music.stop()
                else:
                    if enemy.pos[0] > hero.pos[0]:
                        hero.pos[0] -= 50
                    else:
                        hero.pos[0] += 50

#Função de desenho
def draw():
    screen.clear()
    if game_state == 'menu':
        draw_menu()
    elif game_state == 'playing':
        draw_game()
        for platform in platforms:
            platform.draw()
        for enemy in enemies:
            enemy.draw()
        hero.draw()
    elif game_state == 'win':
        draw_win_screen()
    elif game_state == 'gameover':
        draw_game_over_screen()

def draw_win_screen():
    screen.clear()
    screen.draw.text("You Win!", center=(WIDTH // 2, 100), fontsize=60, color="yellow")
    screen.draw.filled_rect(restart_button, "darkgreen")
    screen.draw.text("Play Again", center=restart_button.center, color="white")
    screen.draw.filled_rect(quit_button, "darkred")
    screen.draw.text("Exit", center=quit_button.center, color="white")

def draw_game_over_screen():
    screen.clear()
    screen.draw.text("Game Over", center=(WIDTH // 2, 100), fontsize=60, color="red")
    screen.draw.filled_rect(restart_button, "darkgreen")
    screen.draw.text("Try Again", center=restart_button.center, color="white")

def draw_menu():
    screen.draw.text("Shadow Awakens", center=(WIDTH // 2, 100), fontsize=60, color="white")
    screen.draw.filled_rect(start_button, "darkgreen")
    screen.draw.text("Start Game", center=start_button.center, color="white")

    screen.draw.filled_rect(sound_button, "darkblue")
    sound_text = "Sound: ON" if sound_on else "Sound: OFF"
    screen.draw.text(sound_text, center=sound_button.center, color="white")

    screen.draw.filled_rect(exit_button, "darkred")
    screen.draw.text("Exit", center=exit_button.center, color="white")

def draw_game():
    for enemy in enemies:
        enemy.draw()
    screen.draw.text(f"Lives: {hero.lives}", topleft=(10, 40), fontsize=30, color="red")
    goal_item.draw()


def on_mouse_down(pos):
    global game_state, sound_on
    if game_state == 'menu':
        if start_button.collidepoint(pos):
            game_state = 'playing'
            music.stop()
            if sound_on:
                music.play("level.mp3")
                music.set_volume(0.3)
        elif exit_button.collidepoint(pos):
            quit()
    
    elif game_state == 'win':
        if restart_button.collidepoint(pos):
            restart_game()
        elif quit_button.collidepoint(pos):
            quit()
    elif game_state == 'gameover':
        if gameover_restart_button.collidepoint(pos):
            restart_game()


def restart_game():
    global hero, enemies, goal_item, game_state, victory_music_played, defeat_sound_played
    hero = Hero()
    enemies = [
        Enemy(250, 300, 60),
        Enemy(700, 250, 70),
        Enemy(885, 200, 70)
]
    goal_item = GoalItem(990, 171)
    game_state = 'playing'
    victory_music_played = False
    defeat_sound_played = False
    music.stop()
    if sound_on:
        music.play('level.mp3')
        music.set_volume(0.3)

pgzrun.go()
