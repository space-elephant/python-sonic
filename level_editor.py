#!/usr/bin/env python3
import pygame
import json
import os
import sys

pygame.init()

font = pygame.font.SysFont('monospace', 12, True, False)

def colour(collision):
    if collision == 0:return (0, 0, 0)
    elif collision == 1:return (255, 255, 0)
    elif collision == 2:return (0, 255, 0)
    elif collision == 3:return (255, 255, 255)

class tile:
    def __init__(self, tileset, number, hflip, vflip):
        self.hflip = hflip
        self.vflip = vflip
        self.image = pygame.transform.flip(pygame.image.load('graphics/tileset/{}/{}.png'.format(tileset, number)), hflip, vflip)
        with open('graphics/tileset/{}/{}.json'.format(tileset, number)) as f:tree = json.load(f)
        self.solidity = tree[:-1]
        self.angle = tree[-1]
        self.mask = pygame.Surface((16, 16))
        self.mask.set_alpha(160)
        self.mask.set_colorkey((0, 0, 0))
        pixels = pygame.PixelArray(self.mask)
        for x in range(16):
            for y in range(16):
                pixelx = 15 - x if hflip else x
                pixely = 15 - y if vflip else y
                pixels[pixelx, pixely] = colour(self.solidity[y][x])
        pixels.close()
        self.display = self.image.copy()
        self.display.blit(self.mask,(0, 0))
        self.mask.set_alpha(255)
        self.number = number
    def visible(self):
        if showsolid:
            if showtile:return self.display
            else:return self.mask
        else:
            if showtile:return self.image
            else:return pygame.Surface((16, 16))

class act:
    def __init__(self, tree):
        self.data = tree['tiles']
        for line in self.data:
            for index in range(len(line)):
                if isinstance(line[index], int):line[index] = tile(tree['tileset'], line[index], False, False)
                else:line[index] = tile(tree['tileset'], line[index][0], line[index][1], line[index][2])
    def draw(self, screen, offset = 0):
        for y in range(len(self.data)):
            for x in range(len(self.data[y])):
                screen.blit(self.data[y][x].visible(), (x * 16, y * 16 - offset * 16))

class tileset(act):
    def __init__(self, name):
        length = len(os.listdir('graphics/tileset/{}/'.format(name)))//2
        # png files and json files
        self.data = []
        for i in range(length):
            if i % 16 == 0:self.data.append([])
            self.data[-1].append(tile(name, i, False, False))
    def draw(self, screen, offset = 0):
        for y in range(len(self.data)):
            for x in range(len(self.data[y])):
                screen.blit(self.data[y][x].visible(), (x * tileset.difference, y * tileset.difference - offset * tileset.difference))

tileset.difference = 19

screenX = 320
screenY = 224

scale = int(sys.argv[1]) if len(sys.argv) > 1 else 1
if scale == 1:screen = pygame.display.set_mode((screenX, screenY))
else:
    screen = pygame.Surface((screenX, screenY))
    window = pygame.display.set_mode((screenX * scale, screenY * scale))

clock = pygame.time.Clock()

with open('test levels/zone/1.json') as f:tree = json.load(f)
level = act(tree)

tiles = tileset(tree['tileset'])

tilemode = False
showsolid = True
showtile = True
drawmode = False

offset = 0

pointer = 0
hflip = False
vflip = False

pos = (0, 0)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:tilemode = not tilemode
            elif event.key == pygame.K_x:showsolid = not showsolid
            elif event.key == pygame.K_z:showtile = not showtile
            elif event.key == pygame.K_d:hflip = not hflip
            elif event.key == pygame.K_c:vflip = not vflip
            elif event.key == pygame.K_DOWN:
                if tilemode:offset += 1
                #else: # TODO add scrolling
            elif event.key == pygame.K_UP:
                if tilemode:offset -= 1
            elif event.key == pygame.K_q:exit()
            elif event.key == pygame.K_s:
                tree['tiles'] = []
                for line in level.data:
                    tree['tiles'].append([])
                    for point in line:
                        tree['tiles'][-1].append([point.number, point.hflip, point.vflip])
                with open('test levels/zone/1.json', 'w') as f:json.dump(tree,f)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            drawmode = True
            if not tilemode:
                level.data[event.pos[1] // (scale * 16)][event.pos[0] // (scale * 16)] = tile(tree['tileset'], pointer, hflip, vflip)
        elif event.type == pygame.MOUSEBUTTONUP:
            drawmode = False
            if tilemode:
                pointer = tiles.data[event.pos[1] // (scale * tileset.difference)][event.pos[0] // (scale * tileset.difference)].number
                tilemode = False
                hflip = False
                vflip = False
        elif event.type == pygame.MOUSEMOTION:
            pos = event.pos
            if drawmode and not tilemode:level.data[event.pos[1] // (scale * 16)][event.pos[0] // (scale * 16)] = tile(tree['tileset'], pointer, hflip, vflip)
    screen.fill((0, 0, 0))

    if tilemode:
        tiles.draw(screen, offset)
        screen.blit(font.render(hex(pos[0] // (scale * tileset.difference) + pos[1] // (scale * tileset.difference) * 16)[2:], True, (255, 0, 0)), (pos[0], pos[1] + 10))
    else:level.draw(screen)

    if scale != 1:pygame.transform.scale(screen, (screenX * scale, screenY * scale), window)
        
    pygame.display.flip()
    clock.tick(60)
