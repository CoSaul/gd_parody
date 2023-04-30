import pygame as k
import sys
import os

import pygame.transform

OBJECTS = {'-': ['Wall', 'wall.png', ''], '/': ['Spike', 'spike.png', ''], '@': ['Soft_Wall', 'wall.png', ''],
           '+': ['Portal', 'portal_ship.png', ', mode="ship"'], 'o': ['Orb', 'yellow_orb.png', ', "yellow"'],
           '=': ['Jumper', 'yellow_jumper.png', ', "yellow"']}


def load_image(name, colorkey=None):
    name = f'data_for_gd/{name}'
    if not os.path.isfile(name):
        print(f"Файл с изображением '{name}' не найден")
        sys.exit()
    image = k.image.load(name)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


JUMP_POWER = 9
G = 0.4
ABSOLUTE_G = 0.4
MOVE_SPEED = 5
MOVE_SPEED_ABSOLUTE = 5


class Player(k.sprite.Sprite):
    def __init__(self, START_POS):
        k.sprite.Sprite.__init__(self)
        self.image = load_image('cube.png')
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = START_POS
        self.jump = False
        self.on_ground = False
        self.vy = 0
        self.vx = MOVE_SPEED
        self.death_counter = 0
        self.mode = 'cube'

    def update(self, objects, up):
        global G
        if self.mode == 'cube':
            G = ABSOLUTE_G
        if self.mode == 'ship':
            G = ABSOLUTE_G / 2
        if self.death_counter == 0:
            if self.jump or up:
                if self.mode == 'cube':
                    if self.on_ground:
                        self.vy -= JUMP_POWER
                if self.mode == 'ship':
                    self.vy -= JUMP_POWER / 30
                if self.mode == 'ball':
                    if self.on_ground:
                        G = -G
                # if self.mode == 'wave':
                #     self.vy =
            if not self.on_ground and self.mode != 'wave':
                self.vy += G
            if self.rect.x < 0 or self.rect.y < 0:
                self.death()
            self.on_ground = False  # Мы не знаем, когда мы на земле
            self.rect.y += self.vy
            self.collide(0, self.vy, objects)
            self.rect.x += self.vx
            self.collide(self.vx, 0, objects)
        else:
            self.death()

    def collide(self, vx, vy, objects):
        for i in objects:
            if k.sprite.collide_rect(self, i):  # если есть пересечение платформы с игроком
                if i.types == 'jumper':
                    i.render()
                if i.types == 'obstacle':  # если объект является препятствием и
                    if vx > 0:  # если игрок движется вправо
                        if not i.save_collide_full:  # если блок не мягок
                            self.death()  # то игрок умирает
                        else:  # и блок мягок
                            self.rect.right = i.rect.left
                    if vx < 0:  # если игрок движется влево
                        if not i.save_collide_full:  # и блок не мягок
                            self.death()  # то игрок умирает
                        else:  # и блок мягок
                            self.rect.left = i.rect.right  # то игрок не движется
                    if self.mode != 'wave':  # и режим - не волна
                        if vy > 0:  # если игрок падает вниз
                            if i.save_collide_full or i.save_collide:  # и блок безопасен
                                self.rect.bottom = i.rect.top  # то игрок не падает вниз
                                self.on_ground = True  # и становится на что-то твердое
                                self.vy = 0  # и энергия падения пропадает
                            else:  # и блок опасен
                                self.death()  # то игрок умирает
                        if vy < 0:  # если игрок движется вверх
                            if i.save_collide_full:  # и блок безопасен
                                self.rect.top = i.rect.bottom  # то игрок не движется вверх
                                self.vy = 0  # и энергия прыжка пропадает
                            else:  # и блок опасен
                                self.death()  # то игрок умирает
                    else:  # и режим - волна
                        if vy > 0:  # если игрок падает вниз
                            if i.save_collide_full:  # и блок безопасен
                                self.rect.bottom = i.rect.top  # то игрок не падает вниз
                                self.on_ground = True  # и становится на что-то твердое
                                self.vy = 0  # и энергия падения пропадает
                            else:  # и блок опасен
                                self.death()  # то игрок умирает
                        if vy < 0:  # если игрок движется вверх
                            if i.save_collide_full:  # и блок безопасен
                                self.rect.top = i.rect.bottom  # то игрок не движется вверх
                                self.vy = 0  # и энергия прыжка пропадает
                            else:  # и блок опасен
                                self.death()  # то игрок умирает
                else:
                    i.render()

    def death(self):
        self.death_counter += 1
        if self.death_counter > 30:
            self.rect.x, self.rect.y = START_POS
            self.vx = MOVE_SPEED
            self.death_counter = 0
            self.mode = 'cube'
            for i in all_sprites:
                if i.types == 'jumper':
                    i.active = True
            hero.image = load_image('cube.png')


class Object(k.sprite.Sprite):
    def __init__(self, group, name, x, y, type, reverse_x=False, reverse_y=False):
        k.sprite.Sprite.__init__(self, group)
        self.image = load_image(name)
        self.image = pygame.transform.flip(self.image, reverse_x, reverse_y)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.types = type
        self.reverse_x = reverse_x
        self.reverse_y = reverse_y


class Wall(Object):
    def __init__(self, group, name, x, y, reverse_x=False, reverse_y=False):
        Object.__init__(self, group, name, x, y, 'obstacle', reverse_x, reverse_y)
        self.save_collide_full = False
        self.save_collide = True


class Spike(Object):
    def __init__(self, group, name, x, y, reverse_x=False, reverse_y=False):
        Object.__init__(self, group, name, x, y, 'obstacle', reverse_x, reverse_y)
        self.save_collide_full = False
        self.save_collide = False


class Soft_Wall(Object):
    def __init__(self, group, name, x, y, reverse_x=False, reverse_y=False):
        Object.__init__(self, group, name, x, y, 'obstacle', reverse_x, reverse_y)
        self.save_collide_full = True
        self.save_collide = True


class Portal(Object):
    def __init__(self, group, name, x, y, mode=False, speed=False, gravity=False, reverse_x=False, reverse_y=False):
        Object.__init__(self, group, name, x, y, 'special', reverse_x, reverse_y)
        self.mode = mode
        self.speed = speed
        self.gravity = gravity

    def render(self):
        if self.mode:
            hero.mode = self.mode
            hero.image = load_image(str(self.mode + '.png'))
        if self.speed:
            global MOVE_SPEED
            MOVE_SPEED = self.speed * MOVE_SPEED_ABSOLUTE


class Jumper(Object):
    def __init__(self, group, name, x, y, color='yellow', reverse_x=False, reverse_y=False):
        Object.__init__(self, group, name, x, y, 'jumper', reverse_x, reverse_y)
        self.color = color
        self.active = True

    def render(self):
        global JUMP_POWER, G
        if self.active:
            hero.vy = 0
            if self.color == 'yellow':
                hero.vy = hero.vy - (JUMP_POWER * 1.3)
                G = G * 2
            elif self.color == 'blue':
                hero.vy = hero.vy - (JUMP_POWER * 1.5)
                JUMP_POWER = -(JUMP_POWER)
                G = -(G)
            elif self.color == 'pink':
                hero.vy = hero.vy - (JUMP_POWER * 0.8)
            elif self.color == 'green':
                JUMP_POWER = -(JUMP_POWER)
                G = -(G)
        self.active = False


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = k.Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l + WIN_WIDTH / 2, -t + WIN_HEIGHT / 2

    l = min(0, l)  # Не движемся дальше левой границы
    l = max(-(camera.width - WIN_WIDTH), l)  # Не движемся дальше правой границы
    t = max(-(camera.height - WIN_HEIGHT), t)  # Не движемся дальше нижней границы
    t = min(0, t)  # Не движемся дальше верхней границы

    return k.Rect(l, t, w, h)


def img_to_lvl():
    from PIL import Image

    OBJECTS = {0: 'Wall(all_sprites, "wall.png", x, y',
               1: 'Spike(all_sprites, "spike.png", x, y',
               2: 'Soft_Wall(all_Sprites, "wall.png", x, y',
               3: 'Portal(all_sprites, "portal_ship.png", x, y, mode="ship"',
               4: 'Orb(all_sprites, "yellow_orb.png", x, y, "yellow"',
               5: 'Jumper(all_sprites, "yellow_jumper.png", x, y, "yellow"'}
    MODIFIERS_1 = {0: '', 1: ', reverse_x=True', 2: ', reverse_y=True', 3: ', reverse_x=True, reverse_y=True'}
    MODIFIERS_2 = {255:''}
    MODIFIERS_3 = {255: ')'}

    import random
    import yadisk

    yade = yadisk.YaDisk(token="y0_AgAAAABWM5k3AAnWlAAAAADiH8VqnFNp1fMeRgKONKIxTUM0wxqEE2o")
    levels_listes = []
    for i in yade.get_files():
        print(i['path'].split('/')[1])
        if i['path'].split('/')[1] == 'levels':
            levels_listes.append('/'.join(i['path'].split('/')[1:]))
    print(levels_listes)
    yade.download(random.choice(levels_listes), 'data_for_gd/level.png')

    im = Image.open(f'data_for_gd/level.png', 'r')
    width, height = im.size
    pixel_values = list(im.getdata())
    l = []
    for x in range(width):
        p = []
        for y in range(height):
            k = list(map(lambda _: int(_), str(pixel_values[width * y + x]).strip('(').strip(')').split(', ')))
            # print(x, y)
            if k[0] in OBJECTS.keys():
                if k[1] in MODIFIERS_1.keys():
                    if k[2] in MODIFIERS_2.keys():
                        if k[3] in MODIFIERS_3.keys():
                            p.append(OBJECTS[k[0]] + MODIFIERS_1[k[1]] + MODIFIERS_2[k[2]] + MODIFIERS_3[k[3]])
                        else:
                            p.append('2')
                    else:
                        p.append('2')
                else:
                    p.append('2')
            else:
                p.append('2')
        l.append(p)
    l = [list(col) for col in zip(*l)]
    return (l, width, height)


WIN_WIDTH = 950  # Ширина создаваемого окна
WIN_HEIGHT = 600  # Высота
SIZE = 50
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)  # Группируем ширину и высоту в одну переменную

k.init()  # Инициация PyGame, обязательная строчка
screen = k.display.set_mode(DISPLAY)  # Создаем окошко
k.display.set_caption("GD bparody")  # Пишем в шапку
bg = load_image('bg.png')
all_sprites = k.sprite.Group()  # Все объекты
level, size_ofl_x, size_ofl_y = img_to_lvl()
x = y = 0  # координаты
for row in level:  # вся строка
    for col in row:  # каждый символ
        e = eval(col)
        x += SIZE  # блоки платформы ставятся на ширине блоков
    y += SIZE  # то же самое и с высотой
    x = 0  # на каждой новой строчке начинаем с нуля
total_level_width = size_ofl_x * SIZE  # Высчитываем фактическую ширину уровня
total_level_height = size_ofl_y * SIZE  # высоту
START_POS = (0, total_level_height - 100)
hero = Player(START_POS)  # создаем героя по (x,y) координатам
up = False
tap = 0
timer = k.time.Clock()
camera = Camera(camera_configure, total_level_width, total_level_height)
camera.update(hero)
while 1:  # Основной цикл программы
    timer.tick(90)
    right = True
    for e in k.event.get():  # Обрабатываем события
        if e.type == k.QUIT or (e.type == k.KEYDOWN and e.key == k.K_ESCAPE):
            sys.exit()
        if (e.type == k.KEYDOWN and e.key in [k.K_UP, k.K_KP_ENTER, k.K_SPACE,
                                              k.K_w]) or e.type == k.MOUSEBUTTONDOWN:#   k.KSCAN_KP_ENTER, k.KSCAN_SPACE, k.KSCAN_UP, k.KSCAN_W
            up = True
            tap = 7
        if (e.type == k.KEYUP and e.key in [k.K_UP, k.K_KP_ENTER, k.K_SPACE,
                                            k.K_w]) or e.type == k.MOUSEBUTTONUP:    #   k.KSCAN_KP_ENTER, k.KSCAN_SPACE, k.KSCAN_UP, k.KSCAN_W
            up = False
        if e.type == k.KEYDOWN and e.key == k.K_r:
            screen.fill('black')
            hero.death()
    if tap > 0:
        tap -= 1
    screen.blit(bg, (0, 0))  # Каждую итерацию необходимо всё перерисовывать
    camera.update(hero)  # центризируем камеру относительно персонажа
    hero.update(all_sprites, up)  # передвижение
    # entities.draw(screen) # отображение
    for e in all_sprites:
        screen.blit(e.image, camera.apply(e))
    screen.blit(hero.image, camera.apply(hero))

    k.display.update()  # обновление и вывод всех изменений на экран
os.remove('data_for_gd/level.png')