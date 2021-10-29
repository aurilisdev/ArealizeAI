from os import wait
import numpy as np
import json
import pygame as pygame
from pygame import color
import random as rand

from pygame.constants import TIMER_RESOLUTION

def brute_force(floor_plan, rooms):
    fitted_rooms = [rooms[0]]
    min_x_coord = min(floor_plan, key=lambda c: c['x'])['x']
    max_x_coord = max(floor_plan, key=lambda c: c['x'])['x']
    fp_width = min_x_coord + max_x_coord
    min_y_coord = min(floor_plan, key=lambda c: c['y'])['y']
    max_y_coord = max(floor_plan, key=lambda c: c['y'])['y']
    fp_height = min_y_coord + max_y_coord
    for roomNumber, room in enumerate(rooms):
        if roomNumber == 0:
            continue
        prev_room = fitted_rooms[-1]
        potential_x_anchor = prev_room['anchorTopLeftX'] + prev_room['width']
        potential_y_anchor = prev_room['anchorTopLeftY'] + prev_room['height']
        if potential_x_anchor + room['width'] <= fp_width:
            room['anchorTopLeftX'] = potential_x_anchor
            fitted_rooms.append(room)
        elif potential_y_anchor + room['height'] <= fp_height:
            room['anchorTopLeftY'] = potential_y_anchor
            fitted_rooms.append(room)
    if len(rooms) == len(fitted_rooms):
        return fitted_rooms
    raise RuntimeError('Did not manage to fit all rooms into the floor plan.')


def fitted(floor_plan, rooms):
    minFloorX = min(floor_plan, key=lambda c: c['x'])['x']
    maxFloorX = max(floor_plan, key=lambda c: c['x'])['x']
    minFloorY = min(floor_plan, key=lambda c: c['y'])['y']
    maxFloorY = max(floor_plan, key=lambda c: c['y'])['y']

    rooms.sort(key=lambda room: -room["height"])
    fitted_rooms = [rooms[0]]

    horizontal = True
    isFirstHorizontal = True
    topLeft = False
    for roomNumber, room in enumerate(rooms):
        if roomNumber == 0:
            continue
        prevRoom = fitted_rooms[-1]
        anchorXCheck = prevRoom['anchorTopLeftX'] + prevRoom['width']
        if topLeft:
            if horizontal:
                if anchorXCheck + room['width'] <= maxFloorX:
                    room['anchorTopLeftX'] = anchorXCheck
                    fitted_rooms.append(room)
                else:
                    horizontal = False
                    prevRoom["anchorTopLeftY"] = rooms[0]["height"] + 30
                    anchorXCheck = 0
            if not horizontal:
                anchorYCheck = prevRoom['anchorTopLeftY'] + prevRoom['height']
                if isFirstHorizontal:
                    prevRoom["anchorTopLeftY"] = 0
                    anchorYCheck -= prevRoom['height']
                    isFirstHorizontal = False
                if anchorYCheck + room['height'] <= maxFloorY:
                    room['anchorTopLeftY'] = anchorYCheck
                    fitted_rooms.append(room)
                else:
                    topLeft = False
        if not topLeft:
            
        
    if len(rooms) == len(fitted_rooms):
        return fitted_rooms
    raise RuntimeError('Did not manage to fit all rooms into the floor plan.')

def parse_json(filepath):
    with open(filepath, 'r') as rawinput:
        data = json.load(rawinput)
        floor_plan = data['planBoundary']
        room_dict = data['rooms']
    # return  ( FloorPlanCoordinates, RoomDictionary )
    return ( floor_plan, room_dict )


def main():
    (width, height) = (600, 600)
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    floor_plan, room_dict = parse_json("/Users/sebastianjohansen/Desktop/ArealizeAI/ArealizeAI/main/example.json")
    parsed = fitted(floor_plan, room_dict)
    while True:
        screen.fill((0, 0, 0), (0, 0, width, height))
        for element in parsed:
            col = (rand.randint(0, 255), rand.randint(0, 255), rand.randint(0, 255))
            pygame.draw.rect(screen, col,(element["anchorTopLeftX"], element["anchorTopLeftY"], element["width"], element["height"]), 4)
        pygame.display.flip()
        pygame.display.update()
        pass
main()