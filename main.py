#!/usr/bin/env python3
import pygame


def display_angle(hex_angle):return (256-hex_angle)*1.40625
def full_size(radius):return radius * 2 - 1

class player:
    def __init__(self):
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
        
        self.xpos = 0x800 # 8 pixels
        self.ypos = 0x1200
        self.body_width = 0x9 # for ground collision. Collision uses full pixels
        self.body_height = 0x13
        self.push_width = 0xA # for pushing things
        self.push_height = 0xA
        self.xsp = 0 # x speed
        self.ysp = 0 # y speed
        self.gsp = 0 # ground speed
        self.slope = slp # current slope factor
        self.ang = 0 # one byte angle. 0x00 right, 0x40 up, 0x80 left, 0xC0 down. 
    def sensors(self, tiles):
        a = self.xpos // 0x100 - self.body_width
        b = self.xpos // 0x100 - self.body_width
        height = self.ypos // 0x100 + self.body_height
        a_tile = a // 16
        a_pixel = a % 16
        b_tile = b // 16
        b_pixel = b % 16
        height_tile = height // 16
        height_pixel = height % 16
        a_height = tiles[a_tile][height_tile].heights[a_pixel]
        if a_height == 0:a_height = tiles[a_tile][height_tile+1].heights[a_pixel]-16
        if a_height == 16:a_height = tiles[a_tile][height_tile-1].heights[a_pixel]+16
        b_height = tiles[b_tile][height_tile].heights[b_pixel]
        if b_height == 0:b_height = tiles[b_tile][height_tile+1].heights[b_pixel]-16
        if b_height == 16:b_height = tiles[b_tile][height_tile-1].heights[b_pixel]+16

class tile:
    def __init__(self, heights, angle):
        self.heights = heights
        self.angle = angle
solid = [16] * 16
empty = [0] * 16
        
tiles = [
    [tile(empty, 0), tile([4]* 16, 0), tile(solid, 0)],
    [tile(empty, 0), tile([4]* 16, 0), tile(solid, 0)],    
]

pygame.init()
screenX = 320
screenY = 224
screen = pygame.display.set_mode((screenX, screenY))
