from os import wait
from matplotlib.pyplot import xcorr
import numpy as np
import json
import pygame as pygame
from pygame import color
import random as rand

from pygame.constants import TIMER_RESOLUTION

def parse_json(filepath):
    with open(filepath, 'r') as rawinput:
        data = json.load(rawinput)
        floor_plan = data['planBoundary']
        room_dict = data['rooms']
    # return  ( FloorPlanCoordinates, RoomDictionary )
    return floor_plan, room_dict

floor_plan, room_dict = parse_json("/Users/samrouppe/Hackaton/example.json")



def fitted(floor_plan, rooms):
    minFloorX = min(floor_plan, key=lambda c: c['x'])['x']
    maxFloorX = max(floor_plan, key=lambda c: c['x'])['x']
    minFloorY = min(floor_plan, key=lambda c: c['y'])['y']
    maxFloorY = max(floor_plan, key=lambda c: c['y'])['y']

    #rooms.sort(key=lambda room: -room["height"])
    fitted_rooms = rooms

    return fitted_rooms 

#print('here:',fitted(floor_plan, room_dict))

#print(type(fitted(floor_plan, room_dict)))


def main():
    (width, height) = (600, 600)
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    floor_plan, room_dict = parse_json(
        "/Users/samrouppe/Hackaton/ArealizeAI/main/example.json")
    
    pygame.mouse.set_pos(115, 40)

    stuckroms = []
    element = fitted(floor_plan, room_dict)
    i = 0
    done = False

    while True:
            
        screen.fill((255, 255, 255), (0, 0, width, height))
    
        col = (rand.randint(1, 254), rand.randint(
            1, 254), rand.randint(1, 254))
        mouse_x = pygame.mouse.get_pos()[0]
        mouse_y = pygame.mouse.get_pos()[1]

        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION and not done:
                pygame.draw.rect(
                    screen, col, (element[i]["anchorTopLeftX"]+mouse_x, element[i]["anchorTopLeftY"]+mouse_y, element[i]["width"], element[i]["height"]), 4)
                
        
            if event.type == pygame.MOUSEBUTTONDOWN and not done:
                x = element[i]["anchorTopLeftX"]+mouse_x
                y = element[i]["anchorTopLeftY"]+mouse_y
                w = element[i]["width"]
                h = element[i]["height"]
                placement_info = (x, y, w, h)
                #placement = True
                stuckroms.append(placement_info)
                if i == len(element)-1:
                    done = True
                    print(True)
                else:
                    i += 1

        if not done:
            pygame.draw.rect(
                screen, col, (element[i]["anchorTopLeftX"]+mouse_x, element[i]["anchorTopLeftY"]+mouse_y, element[i]["width"], element[i]["height"]), 4)

        for j in stuckroms:
            pygame.draw.rect(screen,(0,0,0),j,4)

        pygame.display.flip()
        pygame.display.update()


main()