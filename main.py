#!/usr/bin/env python3
import pygame
import sys
import json
from math import sin, cos, tan, pi

def radians(hex_angle):return hex_angle / 128 * pi

def display_angle(hex_angle):return hex_angle*1.40625
def full_size(radius):return radius * 2 - 1

# animations
roll = 0
stand = 1

# modes
air = 0
floor = 1
left = 2
top = 3
right = 4

class Sonic:
    def __init__(self):
        self.animation = stand
        self.mode = floor
        self.acc = 0xC # acceleration
        self.dec = 0x80 # deceleration
        self.frc = 0xC # friction
        self.top = 0x600 # top speed
        self.slp = 0x20
        self.slprollup = 0x14
        self.slprolldown = 0x50
        self.fall = 0x280 # tolerance ground speed for sticking to walls and ceilings
        
        self.air = 0x18 # air acceleration
        self.jmp = 0x680 # jump force
        # self.jmp = 0x600 # for knuckles
        self.grv = 0x38 # gravity
        
        self.xpos = 0x1300 # 0x13 pixels
        self.ypos = 0x1A00
        self.body_width = 0x9 # for ground collision. Collision uses full pixels
        self.body_height = 0x13
        self.push_width = 0xA # for pushing things
        self.push_height = 0xA
        self.xsp = 0 # x speed
        self.ysp = 0 # y speed
        self.gsp = 0 # ground speed
        self.slope = self.slp # current slope factor
        self.ang = 0 # one byte angle. 0x00 right, 0x40 up, 0x80 left, 0xC0 down.

        self.image = pygame.image.load('graphics/character/sonic/idle/1.png')
    def draw(self, screen):
        error = (255, 255, 255)
        width, height = self.image.get_size()
        x = self.xpos // 256
        y = self.ypos // 256
        screen.blit(self.image, (x - width // 2, y - height // 2))
        pygame.draw.line(screen, error, (x - self.push_width, y), (x + self.push_width, y))
        pygame.draw.line(screen, error,
                         (x - self.body_width, y - self.body_height),
                         (x - self.body_width, y + self.body_height))
        pygame.draw.line(screen, error,
                         (x + self.body_width, y - self.body_height),
                         (x + self.body_width, y + self.body_height))
    def sensors(self, act):
        if self.mode == air:pass # TODO
        elif self.mode == floor:
            y = self.ypos // 256
            x = self.xpos // 256
            if self.xsp > 0:
                if act.solid(x + self.push_width, y):
                    offset = 0
                    while offset < 16:
                        if not act.solid(x + self.push_width - offset, y):break
                        offset += 1
                    self.xpos = (self.xpos // 256 - offset) * 256
                    self.gsp = 0
            elif self.xsp < 0:
                if act.solid(x - self.push_width, y):
                    offset = 0
                    while offset < 16:
                        if not act.solid(x - self.push_width + offset, y):break
                        offset += 1
                    self.xpos = (self.xpos // 256 + offset) * 256
                    self.gsp = 0

            points = []
            y = self.ypos // 256 + self.body_height
            for x in (self.xpos // 256 - self.body_width, self.xpos // 256 + self.body_width):
                if act.solid(x, y):
                    offset = -1
                    while offset > -16:
                        if not act.solid(x, y+offset):break
                        offset -= 1
                else:
                    offset = 1
                    while offset < 16:
                        if act.solid(x, y+offset):break
                        offset += 1
                    offset -= 1
                points.append((offset, act.tiles[y//16][x//16].angle))
            if points[0][0] < points[1][0]:
                offset = points[0][0]
                self.angle = points[0][1]
            else:
                offset = points[1][0]
                self.angle = points[1][1]
            self.ypos = (self.ypos // 256 + offset) * 256
            
    def move(self, keys):
        if self.mode == air:pass
        elif self.mode == floor:
            left = keys[pygame.K_LEFT]
            right = keys[pygame.K_RIGHT]
            if left and right:
                left = False
                right = False
            if self.gsp > 0:
                if right:
                    if self.gsp < self.top:
                        self.gsp += self.acc
                        if self.gsp > self.top:self.gsp = self.top
                elif left:self.gsp -= self.dec
                else:self.gsp -= self.frc
            else:
                if left:
                    if self.gsp > -self.top:
                        self.gsp -= self.acc
                        if self.gsp < -self.top:self.gsp = -self.top
                elif right:self.gsp += self.dec
                else:self.gsp += self.frc
                
            self.xsp = int(self.gsp * cos(radians(self.ang)))
            self.ysp = int(self.gsp * sin(radians(self.ang)))

            self.xpos += self.xsp
            self.ypos += self.ysp
            

                


class Tile:
    def __init__(self, tileset, number):
            self.image = pygame.image.load('graphics/tileset/{}/{}.png'.format(tileset, number))
            with open('graphics/tileset/{}/{}.json'.format(tileset, number)) as f:data = json.load(f)
            self.map = data[:-1]
            self.angle = data[-1]

class Act:
    def __init__(self, json):
        self.name = json['name']
        self.number = json['number']
        alltiles = json['tileset']
        self.tiles = json['tiles']
        tileset = {}
        for row in range(len(self.tiles)):
            for point in range(len(self.tiles[row])):
                if not self.tiles[row][point] in tileset:
                    tileset[self.tiles[row][point]] = Tile(alltiles, self.tiles[row][point])
                self.tiles[row][point] = tileset[self.tiles[row][point]]
    def draw(self, screen): # static camera
        for row in range(len(self.tiles)):
            for tile in range(len(self.tiles[row])):
                screen.blit(self.tiles[row][tile].image, (tile*16, row*16))
    def solid(self, x, y):
        xtile = x // 16
        xpixel = x % 16
        ytile = y // 16
        ypixel = y % 16
        return self.tiles[ytile][xtile].map[ypixel][xpixel]

        
pygame.init()

screenX = 256
screenY = 256
screen = pygame.Surface((screenX, screenY))

window = pygame.display.set_mode((screenX * 2, screenY * 2))

clock = pygame.time.Clock()

with open('test levels/zone/1.json') as f:act = Act(json.load(f))

player = Sonic()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:exit()
    keys = pygame.key.get_pressed()
    screen.fill((0, 0, 0))
    act.draw(screen)
    player.draw(screen)
    player.move(keys)
    player.sensors(act)
    pygame.transform.scale(screen, (screenX * 2, screenY * 2), window)
    pygame.display.flip()
    clock.tick(60)
    
