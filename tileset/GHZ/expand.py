#!/usr/bin/env python3
import pygame
import json

pygame.init()

blocks = pygame.image.load('BlockList.png')
solidimg = pygame.image.load('SolidGraph.png')
solids = pygame.PixelArray(solidimg)
maps = open('blocks.txt')
with open('angles.txt') as f:angles = f.read().split('\n')

def crop(surface, pos):
    result = pygame.Surface((pos[2], pos[3]))
    result.blit(surface, (-pos[0], -pos[1]))
    return result

index = 0
filename = 0

for line in maps.readlines():
    line = line.split(';')[0]
    if line[-1] == '\n':line = line[0:-1]
    if line != '--':
        pygame.image.save(crop(blocks, (0, index*16, 16, 16)), 'tiles/{}.png'.format(filename))
        point = int(line, 16)
        x = point % 32
        y = point // 32
        data = []
        for push in range(16):
            data.append([])
            for side in range(16):
                data[-1].append(3 if solids[x * 16 + side, y * 16 + push] else 0)
        print(point)
        angle = int(angles[point].split(';')[0], 16)
        data.append(-1 if angle == 255 else (256-angle) % 256)
        with open('tiles/{}.json'.format(filename), 'w') as f:json.dump(data, f)
        filename += 1
    index += 1
