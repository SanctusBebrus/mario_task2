import pygame
import os
import sys
import time

pygame.mixer.init()
pygame.mixer.music.load('data/love_u.mp3')


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


pygame.init()
SIZE = WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode(SIZE)
sprite_group = pygame.sprite.Group()
hero_group = pygame.sprite.Group()

tile_image = {'wall': load_image('box.png'),
              'empty': load_image('grass.png')}
player_image = load_image('mar.png')

tile_width = tile_height = 50


class ScreenFrame(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pygame.Rect(0, 0, 800, 600)


class SpriteGroup(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_event(ev):
        for x in ev:
            x.get_event(ev)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    @staticmethod
    def get_event(ev):
        pass


class Tile(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        self.image = tile_image[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(hero_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = (pos_x, pos_y)

    def move(self, x, y):
        self.pos = (x, y)
        self.rect = self.image.get_rect().move(tile_width * self.pos[0] + 15,
                                               tile_height * self.pos[1] + 5)


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["Лютый Марио летел на голубом вертолете",
                  "но внезапно оказался в Backrooms посреди каких-то левых коробок",
                  'и теперь не знает, что ему делать...',
                  'Нажмите любую клавишу чтобы помочь сбежать Лютому',
                  '(не нажимайте escape на следующем экране)']
    background = pygame.transform.scale(load_image('fon.jpg'), SIZE)
    screen.blit(background, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
            elif ev.type == pygame.KEYDOWN or ev.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


def load_level(filename):
    filename = 'data/' + filename
    with open(filename, 'r') as mapFile:
        lvl_map = [line.strip() for line in mapFile]
    max_width = max(map(len, lvl_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), lvl_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                level[y][x] = '.'
    return new_player, x, y


def move(plr, movement):
    x, y = plr.pos
    if movement == 'up':
        if y > 0 and lvl_map[y - 1][x] == '.':
            plr.move(x, y - 1)
    elif movement == 'down':
        if y < max_y - 1 and lvl_map[y + 1][x] == '.':
            plr.move(x, y + 1)
    elif movement == 'left':
        if x > 0 and lvl_map[y][x - 1] == '.':
            plr.move(x - 1, y)
    elif movement == 'right':
        if x < max_x - 1 and lvl_map[y][x + 1] == '.':
            plr.move(x + 1, y)


if __name__ == '__main__':
    print('Введите название уровня:')
    # map.txt
    # h&s.txt
    # heart.txt
    # corridors.txt
    # map_data = 'heart.txt'
    map_data = ''.join(sys.stdin.read().splitlines())
    try:
        lvl_map = load_level(map_data)
    except FileNotFoundError:
        print('Файл не найден')
        exit()
    else:
        pygame.display.set_caption('Лютый Марио')
        player = None
        running = True
        start_screen()
        hero, max_x, max_y = generate_level(lvl_map)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        screen.blit(pygame.image.load('data/no_escape.jpg'), (0, 0))
                        pygame.mixer.music.set_volume(100)
                        pygame.mixer.music.play(-1)
                        pygame.display.set_caption('ТЫ НЕ СМОЖЕШЬ')

                        pygame.display.flip()
                        time.sleep(9999)

                    if event.key == pygame.K_UP:
                        move(hero, 'up')
                    if event.key == pygame.K_DOWN:
                        move(hero, 'down')
                    if event.key == pygame.K_RIGHT:
                        move(hero, 'right')
                    if event.key == pygame.K_LEFT:
                        move(hero, 'left')
            screen.fill(pygame.Color('black'))
            sprite_group.draw(screen)
            hero_group.draw(screen)
            pygame.display.flip()
        pygame.quit()
