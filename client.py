import socket
import sys
import math, random
import pygame
import json
import pygame as pg

from time import sleep
from requests import get

from data import db_session
from settings import SERVER_HOST, SERVER_PORT, SERVER_PORT_WEB
import os
from untitled import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtCore, QtGui, QtWidgets
from untitled import Ui_MainWindow

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.connect((SERVER_HOST, int(SERVER_PORT)))


all_sprites = pg.sprite.Group()  # создание групп спрайтов для каждого типа объектов
players = pg.sprite.Group()
rocks = pg.sprite.Group()
grasses = pg.sprite.Group()
patrons = pg.sprite.Group()
boom = pg.sprite.Group()
health = pg.sprite.Group()
fires = pg.sprite.Group()

pole_info = {}

login = None  # логин игрока
password = None  # логин игрока


class Example(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label_3.setText(f'<a href="http://{SERVER_HOST}:{SERVER_PORT_WEB}/register"> Регистрация </a>')
        self.label_3.setOpenExternalLinks(True)
        self.pushButton.clicked.connect(self.act)
        self.checkBox_3.stateChanged.connect(self.act2)
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        remember_info = {}
        with open('remember.txt', mode='rt') as file:
            try:
                remember_info = json.load(file)
            except Exception:
                pass
        if 'password' in remember_info:
            self.lineEdit_2.setText(remember_info['password'])
        if 'mail' in remember_info:
            self.lineEdit.setText(remember_info['mail'])

    def act(self):
        for i in range(4):
            sock.send(json.dumps({'password': self.lineEdit_2.text(),
                                  'login': self.lineEdit.text()}).encode())
            try:
                info_start = json.loads(sock.recv(2 ** 20).decode())
                sleep(0.5)
            except Exception:
                info_start = {}

            if 'id' in info_start:
                global pole_info, login, password
                pole_info = info_start
                login = self.lineEdit.text()
                password = self.lineEdit_2.text()
                self.close()
            if 'error' in info_start:
                self.statusbar.showMessage(info_start['error'])
            remember_data = {}
        with open('remember.txt', mode='rt') as file:
            try:
                remember_data = json.load(file)
            except Exception:
                pass
        if self.checkBox.isChecked():
            remember_data['mail'] = self.lineEdit.text()
        if self.checkBox_2.isChecked():
            remember_data['password'] = self.lineEdit_2.text()
        with open('remember.txt', mode='wt') as file:
            json.dump(remember_data, file)

    def act2(self):
        if not self.checkBox_3.isChecked():
            self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        else:
            self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Normal)


if True:  # окно авторизации
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    app.exec()
    positions = get(f'http://{SERVER_HOST}:{SERVER_PORT_WEB}/api/getpos').json()
    if not pole_info:
        sys.exit()
    if 'id' in pole_info:
        player_id = pole_info['id']
    if 'pos' in positions:
        player_pos = positions['pos'][player_id % positions['max_players']]
    if 'angle' in pole_info:
        player_angle = pole_info['angle']
    if 'settings' in pole_info:
        FPS = pole_info['settings']['fps']
        SPEED_TANK = pole_info['settings']['speed_tank']
        SPEED_PATRON = pole_info['settings']['speed_patron']
        TANK_A0 = pole_info['settings']['tank_a0']
        GRASS_STONES = pole_info['settings']['grass_stones']
        RELOAD = pole_info['settings']['reload']
        SLOWING = pole_info['settings']['slowing']
        TANK_A = round(TANK_A0, 1)
        SIZE = WIDTH, HEIGHT = pole_info['settings']['size']

    if 'generation' in positions:
        rocks_pos, grasses_pos = positions['generation'][0], positions['generation'][1]

  # настройки pygame
x = 100
y = 45
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)
os.environ['SDL_VIDEO_CENTERED'] = '0'
pg.init()
screen = pg.Surface(SIZE)
# screen2 = pg.display.set_mode(SIZE_WINDOW)
SIZE_WINDOW = (1200, 800)
screen2 = pygame.display.set_mode(SIZE_WINDOW)


pg.display.set_caption('Tanks_online(epic)')
clock = pg.time.Clock()
fire = False  # наличие огня
running = True
players_inf = {}  # спрайты других игроков
time = 0  # время, чтобы замедлять анимацию из-за высокого FPS
reload = False


def load_image(name, colorkey=None):  # загрузка изображения для спрайта
    fullname = os.path.join('pictures', name)
    # если файла не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Stone(pg.sprite.Sprite):  # класс камня
    stone = pg.transform.scale(load_image('stone.png'), GRASS_STONES)  # открытие картинки с камнем

    def __init__(self, pos):
        super().__init__(rocks)  # добавление спрайта в группу камней
        self.image = self.stone
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.mask = pygame.mask.from_surface(self.image)  # создание маски для камня


class Grass(pg.sprite.Sprite):  # класс куста
    grass = pg.transform.scale(load_image('grass.png'), GRASS_STONES)  # открытие картинки с кустом

    def __init__(self, pos):
        super().__init__(grasses)
        self.image = self.grass
        self.rect = self.image.get_rect()
        self.rect.center = pos


for pos1 in rocks_pos:
    all_sprites.add(Stone(pos1))
for pos2 in grasses_pos:
    all_sprites.add(Grass(pos2))

boom_sound1 = pygame.mixer.Sound('sounds/boom.mp3')  # звуки
boom_sound2 = pygame.mixer.Sound('sounds/probitie1.mp3')
boom_sound3 = pygame.mixer.Sound('sounds/probitie-2.mp3')
rik_sound1 = pygame.mixer.Sound('sounds/rikoshet.mp3')
rik_sound2 = pygame.mixer.Sound('sounds/rikoshet1.mp3')
game_over = pygame.mixer.Sound('sounds/tank-unichtozhen.mp3')
pojar = pygame.mixer.Sound('sounds/pojar.mp3')
pojar_channel = pygame.mixer.Channel(0)


def angle_p(vec):  # рассчет угла поворота исходя из вектора скорости
    x, y = vec
    result = None
    if x == 0 or y == 0:
        if x == 0:
            if y < 0:
                result = 0
            elif y > 0:
                result = 180
        elif y == 0:
            if x < 0:
                result = 270
            elif x > 0:
                result = 90
    else:
        angle1 = math.degrees(math.atan(abs(y) / abs(x)))
        if x < 0 and y < 0:
            result = 270 + angle1
        elif x > 0 and y > 0:
            result = 90 + angle1
        elif x > 0 and y < 0:
            result = 90 - angle1
        elif x < 0 and y > 0:
            result = 270 - angle1
    return result


class AnimatedSprite(pygame.sprite.Sprite):  # анимация спрайтов
    def __init__(self, x, y, sheet, columns, rows, count_frames=None,
                 paddings=(0, 0, 0, 0)):
        super().__init__(all_sprites)
        self.frames = []
        if count_frames is not None:
            self.count_frames = count_frames
        else:
            self.count_frames = columns * rows
        self.cut_sheet(sheet, columns, rows, paddings)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect.center = x, y

    def cut_sheet(self, sheet, columns, rows, paddings):  # нарезка кадров для анимации
        self.rect = pygame.Rect(
            0, 0, (sheet.get_width() - paddings[1] - paddings[3]) // columns,
                  (sheet.get_height() - paddings[0] - paddings[2]) // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (
                    paddings[3] + self.rect.w * i,
                    paddings[0] + self.rect.h * j
                )
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))
                if self.count_frames == len(self.frames):
                    return

    def update(self):  # сама анимация
        self.cur_frame = self.cur_frame + 1
        self.image = self.frames[self.cur_frame]


class Boom(AnimatedSprite):  # анимация взрыва
    sheet = load_image('boom.png')

    def __init__(self, x, y):
        super().__init__(x, y, self.sheet, 8, 4)
        boom.add(self)  # добавление спрайта в группу взрывов

    def update(self):  # анимация взрыва
        self.cur_frame = self.cur_frame + 1
        if self.cur_frame == self.count_frames - 1:  # уничтожение спрайта, если анимация окончена
            self.kill()
        self.image = self.frames[self.cur_frame]


class Fire(AnimatedSprite):  # анимация пожара
    sheet = load_image('fire.png')

    def __init__(self, player, time):
        super().__init__(player.rect.centerx, player.rect.centery - 40, self.sheet, 4, 4)
        fires.add(self)  # добавление спрайта в группу пожара
        self.time = time  # время действия пожара
        self.player = player  # игрок с этим эффектом

    def update(self):  # анимация взрыва
        global fire
        self.rect.center = self.player.rect.centerx, self.player.rect.centery - 40
        self.cur_frame = self.cur_frame + 1
        self.cur_frame %= self.count_frames
        self.time -= 1
        if self.time <= 0 or self.player.hp <= 0:  # уничтожение спрайта, если эффект окончен
            self.kill()
        self.image = self.frames[self.cur_frame]
        self.player.damage(0.089)  # урон от пожара


class HealthBar(pg.sprite.Sprite):  # класс полоски здоровья
    def __init__(self, size, pos, height):
        super().__init__(health)
        bar = pygame.Surface(size)  # рисование полоски
        bar.fill(pygame.Color("green"))
        pygame.draw.rect(bar, pygame.Color("black"), (0, 0, *size), 3)
        self.image = bar
        self.rect = self.image.get_rect()
        self.rect.center = pos  # позиция полоски
        self.size = size
        self.height = height  # высота полоски над центром спрайта игрока

    def update(self, player):  # обновление состояние полоски
        self.image.fill(pygame.Color("white"))
        pygame.draw.rect(self.image, pygame.Color("Green"), (2, 0, (self.size[0] - 3) * player.hp / 100, self.size[1]),
                         0)
        pygame.draw.rect(self.image, pygame.Color("black"), (0, 0, *self.size), 3)
        self.image = self.image.convert()  # делаем прозрачной полоску в месте белого цвета
        self.image.set_colorkey(pygame.Color("white"))
        self.image = self.image.convert_alpha()
        self.rect.center = player.rect.centerx, player.rect.centery - self.height  # рисование полоски с учетом высоты


class Tank(pg.sprite.Sprite):  # класс танка
    pictures = [pygame.transform.scale(load_image('tank1.png'), (40, 55)),
            pygame.transform.scale(load_image('tank2.png'), (40, 55)),
            pygame.transform.scale(load_image('tank1.png'), (40, 55)),
            pygame.transform.scale(load_image('tank2.png'), (40, 55))]  # загрузка изображений двух игроков

    def __init__(self, pos, rotation, player, control, time, shoot_button, mail):
        super().__init__(players)
        self.mail = mail
        self.kills = 0
        self.first_position = pos
        self.pos = pos
        self.shoot_button = shoot_button
        self.player = player  # номер игрока
        self.control = control  # клавиши для управления танком
        self.image = pygame.transform.rotate(self.pictures[player % 4],
                                             360 - rotation)  # картинки для спрайтов исходя из номера игрока
        self.image2 = self.pictures[player % 4]  # а также поворот картинки
        self.mask = pygame.mask.from_surface(self.image)  # создание маски
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.angle = rotation  # переменная дл хранения изменяющегося угла танка
        self.rotation = rotation  # хранения поворота при спавне
        self.velocity = [0, 0]  # изначальный вектор скорости
        self.data = [False, False, False, False]  # возможность ускорений танка по всем направлениям
        self.slowing = 1  # замедление танка
        self.hp = 100  # здоровье танка
        self.health_bar = HealthBar([100, 18], (self.pos[0], self.pos[1] - 50), 50)  # задание полоски здоровья
        self.reload_center = (75, 38)  # центр значка перезарядки относительно центра танка
        self.time = time
        self.colision = False
        self.boom_sounds = pygame.mixer.Channel(1)
        self.rik_sounds = pygame.mixer.Channel(2)
        self.player_inf = {'pos': self.first_position,  # информация, идущая на сервер
                           'shoot': [None, None]}

    def change_id(self, id_player):
        self.player = id_player
        self.image = pygame.transform.rotate(self.pictures[(self.player - 1) % 4],
                                             360 - self.rotation)  # картинки для спрайтов исходя из номера игрока
        self.image2 = self.pictures[(self.player - 1) % 4]  # а также поворот картинки

    def kill(self):
        self.health_bar.kill()
        super(Tank, self).kill()

    def move(self, events):  # управление танком
        for i in events:
            if i.type == pg.KEYDOWN:  # при удерживании кнопки управления танком значение передвижения в данном направлении становится True
                if i.key == self.control[0] and not self.data[0]:
                    self.data[0] = not self.data[0]
                if i.key == self.control[1] and not self.data[1]:
                    self.data[1] = not self.data[1]
                if i.key == self.control[2] and not self.data[2]:
                    self.data[2] = not self.data[2]
                if i.key == self.control[3] and not self.data[3]:
                    self.data[3] = not self.data[3]
            elif i.type == pg.KEYUP:
                if i.key == self.control[0] and self.data[0]:
                    self.data[0] = not self.data[0]
                if i.key == self.control[1] and self.data[1]:
                    self.data[1] = not self.data[1]
                if i.key == self.control[2] and self.data[2]:
                    self.data[2] = not self.data[2]
                if i.key == self.control[3] and self.data[3]:
                    self.data[3] = not self.data[3]
        self.velocity = [round(self.velocity[0], 1), round(self.velocity[1],
                                                           1)]  # округление скоростей, так как почему-то в процессе прибавления и убавления они изменяются
        if self.data[0] and self.velocity[1] > -SPEED_TANK:  # ускорение танка в соответсвии с удерживаемыми кнопками
            self.velocity[1] -= TANK_A
        elif self.velocity[1] < 0:
            self.velocity[1] += TANK_A
        if self.data[1] and self.velocity[0] < SPEED_TANK:
            self.velocity[0] += TANK_A
        elif self.velocity[0] > 0:
            self.velocity[0] -= TANK_A
        if self.data[2] and self.velocity[1] < SPEED_TANK:  # и, следовательно, замедление в случае отпускания кнопок
            self.velocity[1] += TANK_A
        elif self.velocity[1] > 0:
            self.velocity[1] -= TANK_A
        if self.data[3] and self.velocity[0] > -SPEED_TANK:
            self.velocity[0] -= TANK_A
        elif self.velocity[0] < 0:
            self.velocity[0] += TANK_A

        if angle_p(self.velocity) != None and any(self.data):  # поворот танка исходя из вектора скорости
            self.rotate(angle_p(self.velocity))

        if self.rect.centerx >= WIDTH - 20 and self.velocity[0] > 0:  # танк не может уйти за границы карты
            self.velocity[0] = 0
        if self.rect.centery >= HEIGHT - 20 and self.velocity[1] > 0:
            self.velocity[1] = 0
        if self.rect.centerx <= 20 and self.velocity[0] < 0:
            self.velocity[0] = 0
        if self.rect.centery <= 20 and self.velocity[1] < 0:
            self.velocity[1] = 0

        self.rect.move_ip(self.velocity[0] / self.slowing,
                          self.velocity[1] / self.slowing)  # передвижение танка с учетом замедления
        self.mask = pg.mask.from_surface(self.image)  # обновление маски, так как он все время поворачивается
        self.slowing = 1
        if pg.sprite.spritecollide(self, rocks, dokill=False,
                                   collided=pg.sprite.collide_mask):  # при столкновении с камнем снижается скорость и наносится урон
            self.slowing = SLOWING
            self.damage(0.02)

    def rotate(self, angle):  # поворот танка
        self.image = pg.transform.rotate(self.image2, 360 - angle)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center  # сохранение центра необходимо для корректного вылета пули
        self.angle = angle

    def shoot(self):  # выстрел
        self.player_inf['shoot'][0] = True
        a, b = math.sin(math.radians(self.angle)) * SPEED_PATRON, -math.cos(
            math.radians(self.angle)) * SPEED_PATRON  # рассчет вектора скорости пули исходя из угла поворота танка
        self.player_inf['shoot'][1] = (a, b), self.rect.center, self.angle, self.player

    def shoot_data(self, data):
        if self.time >= RELOAD * FPS:
            Patron(*data)  # создание пули
            self.time = 0
            print(data)

    def update(self):  # обновление состояние танка
        self.time += 1
        self.health_bar.update(self)  # обновление полоски со здоровьем
        angle = (self.time / (RELOAD * FPS)) * 2 * math.pi
        pygame.draw.arc(screen, pygame.Color('blue'), (self.rect.centerx + self.reload_center[0] - 20,
                                                       self.rect.centery - self.reload_center[1] - 20, 20, 20),
                        0, angle, 5)  # состояние перезарядки
        if self.player != player_main.player:  # показ количества убийств
            text = font.render(str(self.kills), True, pygame.Color('red'))  # рендер текста
            text_x, text_y = (self.rect.centerx - self.reload_center[0] + 5, self.rect.centery - self.reload_center[1] - 30)  # размещение текста в верхнем левом углу
            screen.blit(text, (text_x, text_y))  # отображение текста
            text = font3.render(self.mail, True, pygame.Color('green'))  # рендер текста
            text_x, text_y = (self.rect.centerx - self.reload_center[0] + 10,
                          self.rect.centery - self.reload_center[1] - 45)  # размещение текста в верхнем левом углу
            screen.blit(text, (text_x, text_y))  # отображение текста

    def damage(self, dam):  # нанесение урона танку
        self.hp -= dam

    def return_tank(self):  # возвращение танка в начальную позицию
        self.hp = 100
        self.velocity = [0, 0]
        self.angle = self.rotation
        self.data = [False, False, False, False]
        self.image = pg.transform.rotate(self.image2, 360 - self.rotation)
        self.rect.center = self.first_position
        self.time = RELOAD * FPS


class Patron(pg.sprite.Sprite):
    pat = pg.transform.scale(pg.transform.rotate(load_image('patron.png', (255, 255, 255)), 90),
                             (10, 40))  # открытие избражения с пулей и ее сжатие

    def __init__(self, speed, pos, rotation, player_id, dam, angle_rik):
        super().__init__(patrons)
        self.number1 = 0
        self.number2 = 0
        self.speed = speed
        self.image = pg.transform.rotate(self.pat,
                                         360 - rotation)  # поворот ее на соответствующий градус исходя из поворота танка
        self.mask = pygame.mask.from_surface(self.image)  # создание маски для пули
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.player_id = player_id
        self.collide_with_tank = True  # возможность столкновения с танком
        self.dam = dam
        self.angle_rik = angle_rik

    def update(self):
        global fire, index
        for elem in players:
            if elem.player != self.player_id:
                if not pg.sprite.collide_mask(self,
                                              elem):  # если не сталкивается с другим игроком, то продолжает движение
                    self.rect.move_ip(*self.speed)
                else:
                    if self.collide_with_tank:
                        dam = self.dam[self.number1 % 4]
                        elem.damage(dam)  # нанесение урона при обратном
                        self.number1 += 1
                        if dam >= 20:  # попадание по танку
                            boom_sound = boom_sound2 if random.randint(1, 2) == 2 else boom_sound3
                            elem.boom_sounds.queue(boom_sound1), elem.boom_sounds.queue(boom_sound)  # звук взрыва
                            Boom(*self.rect.center)  # взрыв пули
                            self.kill()  # уничтожение пули
                            if random.randint(1, 10) == 1:  # c небольшой вероятностью вызывается пожар
                                time_fire = random.randint(5 * FPS, 20 * FPS)
                                fire = True
                                elem.fire = [True, time_fire]
                                elem.time_delete_fire = 0

                        else:  # если произошел рикошет - меняем направление пули
                            elem.rik_sounds.queue(rik_sound1), elem.rik_sounds.queue(rik_sound2)  # звук рикошета

                            angle = self.angle_rik[self.number2 % 4]
                            self.number2 += 1
                            self.speed = (math.sin(math.radians(angle)) * SPEED_PATRON,
                                          -math.cos(math.radians(angle)) * SPEED_PATRON)
                            self.image = pg.transform.rotate(self.pat, 360 - angle)
                            self.mask = pygame.mask.from_surface(self.image)
                        self.collide_with_tank = False
            else:
                self.rect.move_ip(*self.speed)

        if pg.sprite.spritecollide(self, rocks, dokill=False,
                                   collided=pygame.sprite.collide_mask):  # столкновение с камнем
            pygame.mixer.Sound('sounds/rock_boom.mp3').play()
            Boom(*self.rect.center)  # взрыв пули
            self.kill()  # уничтожение пули
        if self.rect.centerx >= WIDTH + self.rect.width or self.rect.centerx <= -self.rect.width:  # уничтожение пули при вылете за границы для оптимизации игры
            self.kill()  # уничтожение пули
        if self.rect.centery >= HEIGHT + self.rect.width or self.rect.centery <= -self.rect.width:
            self.kill()  # уничтожение пули


pole = load_image('pole.jpg')  # загрузка изображения игрового поля

game = True  # статус игры
time_for_quit = 0
fullscreen = False
font, font2, font3 = pg.font.Font(None, 50), pg.font.Font(None, 36), pg.font.Font(None, 23)  # шрифты для текста

player_main = Tank(player_pos, player_angle, player_id, [pg.K_w, pg.K_d, pg.K_s, pg.K_a], RELOAD * FPS, pg.MOUSEBUTTONDOWN, login)  # создание игрока


screen3 = pygame.Surface(SIZE)
for j in range(0, HEIGHT % pole.get_height() + 2):
    pole = pygame.transform.flip(pole, False, True)
    for i in range(0, WIDTH % pole.get_width() + 2):
        screen3.blit(pole, (i * pole.get_width(), j * pole.get_height()))


all_sprites.add(player_main)


while running and time_for_quit <= 3:
    time += 1  # время для замедления анимаций из-за большого числа кадров
    if time % 4 == 0:
        player_main.player_inf['shoot'][0] = False
    if fires:
        fire = True
    else:
        fire = False
    if fire:
        if pojar_channel.get_queue():  # звук пожара
            pojar_channel.unpause()
        else:
            pojar_channel.queue(pojar)
    else:
        pojar_channel.pause()
    for player in players:
        if player.hp <= 0 and game:
            pygame.mixer.Sound.play(game_over)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == player_main.shoot_button and game and player_main.time >= RELOAD * FPS and player_main.hp > 0:
            player_main.shoot()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l:
                fullscreen = not fullscreen
                if fullscreen:
                    screen2 = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen2 = pygame.display.set_mode(SIZE_WINDOW)
    if reload:  # перезагрузка игры
        pojar_channel.pause()  # остановка пожара
        game = True
        for fire in fires:  # уничтожение пожаров
            fire.kill()
        fire = False
        for player in players:
            player.return_tank()  # восстановление здоровья у игроков
        reload = False

    if game and player_main.hp > 0:
        player_main.move(events)  # передвижение игроков
    else:
        player_main.data = [False, False, False, False]
    if True:
        for player1 in players:  # обработка столкновений
            data = pygame.sprite.spritecollide(player1, players, dokill=False, collided=pygame.sprite.collide_mask)
            if len(data) > 1:
                for player2 in data:
                    if player2 != player1:
                        player1.slowing, player2.slowing = SLOWING, SLOWING
            else:
                player1.colision = False
    player_main.player_inf['velocity'] = player_main.velocity  # информация для передачи
    player_main.player_inf['hp'] = player_main.hp
    player_main.player_inf['angle'] = player_main.angle
    player_main.player_inf['pos'] = player_main.rect.center
    # if player_main['shoot'][0]:
    #     time = 0
    if running:
        sock.send(json.dumps(player_main.player_inf).encode())  # отправление информации о игроке
    else:
        time += 1
        exit0 = {'exit': [login, password]}
        sock.send(json.dumps(exit0).encode())
    screen.blit(screen3, (0, 0)), rocks.draw(screen), players.draw(screen)  # отрисовка кадра
    patrons.draw(screen), fires.draw(screen), grasses.draw(screen), health.draw(screen), boom.draw(screen)
    if time % 2 == 0:
        boom.update()
        fires.update()
    players.update(), patrons.update()  # обновление спрайтов(анимация, движение, взрывы, обновление полоски здоровья)
    clock.tick(FPS)
    size_window = screen2.get_size()
    coords = -player_main.rect.centerx + size_window[0] / 2, -player_main.rect.centery + size_window[1] / 2
    coords = coords[0] if coords[0] > -WIDTH + size_window[0] else -WIDTH + size_window[0], coords[1] if coords[1] > -HEIGHT + size_window[1] else -HEIGHT + size_window[1]
    coords = coords[0] if coords[0] < 0 else 0, coords[1] if coords[1] < 0 else 0
    screen2.blit(screen, coords)
    if not game:  # если игра окончена, выводится сообщение с результатом
        text = font.render(f'Игра окончена', True, pygame.Color('red'))  # рендер текста
        text2 = font2.render('Ждите перезапуска', True, pygame.Color('yellow'))
        text_x = screen2.get_width() // 2 - text.get_width() // 2  # размещение текста в центре экрана
        text_y = screen2.get_height() // 2 - text.get_height() // 2
        screen2.blit(text, (text_x, text_y))  # отображение текста
        screen2.blit(text2, (text_x, text_y + 50))
    else:
        result = []
    text = font.render(f'Убийств: {player_main.kills}', True, pygame.Color('green'))  # рендер текста
    text_x, text_y = text.get_width() // 8, text.get_height() // 2  # размещение текста в верхнем левом углу
    screen2.blit(text, (text_x, text_y))  # отображение текста
    pg.display.flip()  # обновление дисплея
    try:  # принятие информации о поле
        info = json.loads(sock.recv(2 ** 20).decode())
        if 'players' in info:
            data_players = info['players']
            for id0 in data_players.keys():
                player_info = data_players[id0]
                if int(id0) != player_main.player:
                    if id0 not in players_inf:
                        players_inf[id0] = Tank(player_info['pos'], 90, int(id0), [pg.K_w, pg.K_d, pg.K_s, pg.K_a],
                                               RELOAD * FPS, pg.KEYDOWN, player_info['nickname'])
                    players_inf[id0].hp = player_info['hp']
                    players_inf[id0].rotate(player_info['angle'])
                    players_inf[id0].rect.center = player_info['pos']
                    players_inf[id0].velocity = player_info['velocity']
                    players_inf[id0].kills = player_info['kills']
                    if player_info['fire'][0]:
                        Fire(players_inf[id0], player_info['fire'][1])
                    for data_patron in player_info['patrons']:
                        players_inf[id0].shoot_data(data_patron)
                else:
                    player_main.hp = player_info['hp']
                    player_main.kills = player_info['kills']
                    if player_info['fire'][0]:
                        Fire(player_main, player_info['fire'][1])
                    for data_patron in player_info['patrons']:
                        player_main.shoot_data(data_patron)

            for key_id in players_inf.keys():
                if key_id not in data_players.keys():
                    players_inf[key_id].kill()
                    del players_inf[key_id]
        if 'fire_sound' in info:
            fire = info['fire_sound']
        if 'reload' in info:
            reload = info['reload']
        game = info.get('game', game)
    except Exception:
        # info = sock.recv(2 ** 20).decode()
        pass
pygame.quit()
