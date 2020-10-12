#!/usr/bin/env python3
import pygame
import json
import os

def colour(collision):
    if collision == 0:return (0, 0, 0)
    elif collision == 1:return (255, 255, 0)
    elif collision == 2:return (0, 255, 0)
    elif collision == 3:return (255, 255, 255)

class tile:
    def __init__(self, tileset, number):
        self.image = pygame.image.load('graphics/tileset/{}/{}.png'.format(tileset, number))
        with open('graphics/tileset/{}/{}.json'.format(tileset, number)) as f:tree = json.load(f)
        self.solidity = tree[:-1]
        self.angle = tree[-1]
        self.mask = pygame.Surface((16, 16))
        self.mask.set_alpha(128)
        self.mask.set_colorkey((0, 0, 0))
        pixels = pygame.PixelArray(self.mask)
        for x in range(16):
            for y in range(16):
                pixels[x, y] = colour(self.solidity[y][x])
        pixels.close()
        self.display = self.image.copy()
        self.display.blit(self.mask,(0, 0))
        self.mask.set_alpha(255)
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
                line[index] = tile(tree['tileset'], line[index])
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
            self.data[-1].append(tile(name, i))
    def draw(self, screen, offset = 0):
        difference = 19
        for y in range(len(self.data)):
            for x in range(len(self.data[y])):
                screen.blit(self.data[y][x].visible(), (x * difference, y * difference - offset * difference))


pygame.init()

screenX = 316
screenY = 224
screen = pygame.display.set_mode((screenX, screenY))

clock = pygame.time.Clock()

with open('test levels/zone/1.json') as f:tree = json.load(f)
level = act(tree)

tiles = tileset(tree['tileset'])

tilemode = False
showsolid = True
showtile = True

offset = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:tilemode = not tilemode
            elif event.key == pygame.K_x:showsolid = not showsolid
            elif event.key == pygame.K_z:showtile = not showtile
            elif event.key == pygame.K_DOWN:
                if tilemode:offset += 1
                #else: # TODO add scrolling
            elif event.key == pygame.K_UP:
                if tilemode:offset -= 1
                elif event.key == pygame.K_q:exit()
        screen.fill((0, 0, 0))

        if tilemode:tiles.draw(screen, offset)
        else:level.draw(screen)

        pygame.display.flip()
        clock.tick(60)
