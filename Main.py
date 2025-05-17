import pgzrun
import math
import random
from pygame import Rect

WIDTH = 640
HEIGHT = 510
TILE_SIZE = 64

state = "menu"
music_on = True

frames_left = [
    'mage_walk_left_1', 'mage_walk_left_2',
    'mage_walk_left_3', 'mage_walk_left_4'
]
frames_right = [
    'mage_walk_right_1', 'mage_walk_right_2',
    'mage_walk_right_3', 'mage_walk_right_4'
]
fireball_frames = [
    'fireball_1', 'fireball_2', 'fireball_3',
    'fireball_4', 'fireball_5', 'fireball_6'
]
enemy_frames = [
    'enemy_walk_1', 'enemy_walk_2', 'enemy_walk_3', 'enemy_walk_4',
    'enemy_walk_5', 'enemy_walk_6', 'enemy_walk_7', 'enemy_walk_8'
]

def play_music():
    if music_on:
        music.play('background_theme')
        music.set_volume(0.3)
    else:
        music.stop()

play_music()

map_data = [
    "WW      WW",
    "W        W",
    "          ",
    "          ",
    "          ",
    "          ",
    "W        W",
    "WW      WW"
]

enemies = []
projectiles = []
score = 0
speed = 3

current_frame = 0
frame_delay = 10
frame_count = 0
last_direction = 'right'

cooldown_frames = 30
frames_since_last_shot = cooldown_frames

mage = Actor(frames_right[0])
mage.pos = 320, 240


class Projectile:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.frame = 0
        self.frame_count = 0
        self.frame_delay = 4
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        self.dx = dx / dist
        self.dy = dy / dist
        self.speed = 5
        self.active = True

    def update(self):
        if not self.active:
            return

        new_x = self.x + self.dx * self.speed
        new_y = self.y + self.dy * self.speed

        if collided_with_wall(new_x, new_y):
            if music_on:
                sounds.fireball_hit.play()
            self.active = False
            return

        self.x = new_x
        self.y = new_y

        self.frame_count += 1
        if self.frame_count >= self.frame_delay:
            self.frame_count = 0
            self.frame = (self.frame + 1) % len(fireball_frames)

    def draw(self):
        if self.active:
            screen.blit(fireball_frames[self.frame], (self.x, self.y))


class Enemy:
    def __init__(self):
        sides = ['top', 'bottom', 'left', 'right']
        side = random.choice(sides)
        margin = 100

        if side == 'top':
            self.x = random.randint(0, WIDTH)
            self.y = -margin
        elif side == 'bottom':
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT + margin
        elif side == 'left':
            self.x = -margin
            self.y = random.randint(0, HEIGHT)
        else:
            self.x = WIDTH + margin
            self.y = random.randint(0, HEIGHT)

        self.frame = 0
        self.frame_delay = 20
        self.frame_count = 0
        self.speed = 1.2
        self.active = True

    def update(self):
        if not self.active:
            return

        dx = mage.x - self.x
        dy = mage.y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        self.x += self.speed * dx / dist
        self.y += self.speed * dy / dist

        self.frame_count += 1
        if self.frame_count >= self.frame_delay:
            self.frame_count = 0
            self.frame = (self.frame + 1) % len(enemy_frames)

    def draw(self):
        if self.active:
            screen.blit(enemy_frames[self.frame], (self.x, self.y))

    def collided_with(self, other_x, other_y, radius=30):
        distance = math.hypot(self.x - other_x, self.y - other_y)
        return distance < radius + 16


def collided_with_wall(x, y):
    grid_x = int(x // TILE_SIZE)
    grid_y = int(y // TILE_SIZE)
    if 0 <= grid_y < len(map_data) and 0 <= grid_x < len(map_data[0]):
        return map_data[grid_y][grid_x] == "W"
    return True


def spawn_enemy():
    if state == "game":
        enemies.append(Enemy())


def reset_game():
    global enemies, projectiles, score, mage
    enemies = []
    projectiles = []
    score = 0
    mage.pos = 320, 240


button_start = Rect((220, 150), (200, 50))
button_sound = Rect((220, 230), (200, 50))
button_exit = Rect((220, 310), (200, 50))


def draw_menu():
    screen.clear()
    title_area = Rect(0, 50, WIDTH, 50)
    screen.draw.textbox("Roguelike Game - Menu", title_area, color="white")
    screen.draw.filled_rect(button_start, "darkblue")
    screen.draw.textbox("Start Game", button_start, color="white")
    screen.draw.filled_rect(button_sound, "darkblue")
    text_sound = "Sound: ON" if music_on else "Sound: OFF"
    screen.draw.textbox(text_sound, button_sound, color="white")
    screen.draw.filled_rect(button_exit, "darkblue")
    screen.draw.textbox("Exit", button_exit, color="white")


def draw_game():
    screen.clear()
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            pos = (x * TILE_SIZE, y * TILE_SIZE)
            screen.blit("wall" if tile == 'W' else "floor", pos)
    mage.draw()
    for proj in projectiles:
        proj.draw()
    for enemy in enemies:
        enemy.draw()
    screen.draw.text(f"Score: {score}", topleft=(10, 10), fontsize=30, color="white")


def draw():
    if state == "menu":
        draw_menu()
    elif state == "game":
        draw_game()


def update():
    global current_frame, frame_count, last_direction
    global frames_since_last_shot, score, state

    if state != "game":
        return

    frames_since_last_shot += 1
    moving = False
    key_pressed = None

    if keyboard.a:
        mage.x -= speed
        key_pressed = 'left'
    if keyboard.d:
        mage.x += speed
        key_pressed = 'right'
    if keyboard.w:
        mage.y -= speed
        key_pressed = 'up'
    if keyboard.s:
        mage.y += speed
        key_pressed = 'down'

    if key_pressed:
        moving = True
        if key_pressed in ['left', 'right'] and key_pressed != last_direction:
            current_frame = 0
            frame_count = 0
            last_direction = key_pressed
        elif key_pressed in ['up', 'down']:
            key_pressed = last_direction

    if moving:
        frame_count += 1
        if frame_count >= frame_delay:
            frame_count = 0
            current_frame = (current_frame + 1) % len(frames_left)
        mage.image = frames_left[current_frame] if last_direction == 'left' else frames_right[current_frame]
    else:
        current_frame = 0
        mage.image = frames_left[0] if last_direction == 'left' else frames_right[0]

    for proj in projectiles:
        proj.update()

    for enemy in enemies:
        enemy.update()
        for proj in projectiles:
            if enemy.collided_with(proj.x, proj.y):
                enemy.active = False
                proj.active = False
                if music_on:
                    sounds.enemy_hit.play()
                score += 1

        if enemy.collided_with(mage.x, mage.y, radius=30):
            reset_game()
            state = "menu"

    enemies[:] = [e for e in enemies if e.active]
    projectiles[:] = [p for p in projectiles if p.active and 0 <= p.x <= WIDTH and 0 <= p.y <= HEIGHT]


def on_mouse_down(pos):
    global frames_since_last_shot, state, music_on

    if state == "menu":
        if button_start.collidepoint(pos):
            reset_game()
            state = "game"
        elif button_sound.collidepoint(pos):
            music_on = not music_on
            play_music()
        elif button_exit.collidepoint(pos):
            exit()

    elif state == "game":
        if frames_since_last_shot >= cooldown_frames:
            if music_on:
                sounds.fireball_cast.play()
            projectiles.append(Projectile(mage.x, mage.y, pos[0], pos[1]))
            frames_since_last_shot = 0


clock.schedule_interval(spawn_enemy, 2.0)

pgzrun.go()
