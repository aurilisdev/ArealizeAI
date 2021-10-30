import numpy as np
import json
import pygame as pygame
from pygame import color
import random as rand

from pygame.constants import TIMER_RESOLUTION

def returnType(e):
    return e["type"]

def brute_force(floor_plan, rooms):
    fitted_rooms = [rooms[0]]
    min_x_coord = min(floor_plan, key=lambda c: c["x"])["x"]
    max_x_coord = max(floor_plan, key=lambda c: c["x"])["x"]
    fp_width = min_x_coord + max_x_coord
    min_y_coord = min(floor_plan, key=lambda c: c["y"])["y"]
    max_y_coord = max(floor_plan, key=lambda c: c["y"])["y"]
    fp_height = min_y_coord + max_y_coord
    for roomNumber, room in enumerate(rooms):
        if roomNumber == 0:
            continue
        prev_room = fitted_rooms[-1]
        potential_x_anchor = prev_room["anchorTopLeftX"] + prev_room["width"]
        potential_y_anchor = prev_room["anchorTopLeftY"] + prev_room["height"]
        if potential_x_anchor + room["width"] <= fp_width:
            room["anchorTopLeftX"] = potential_x_anchor
            fitted_rooms.append(room)
        elif potential_y_anchor + room["height"] <= fp_height:
            room["anchorTopLeftY"] = potential_y_anchor
            fitted_rooms.append(room)
    if len(rooms) == len(fitted_rooms):
        return fitted_rooms
    raise RuntimeError("Did not manage to fit all rooms into the floor plan.")


def isRectangleOverlap(R1, R2):
    if (R1[0] >= R2[2]) or (R1[2] <= R2[0]) or (R1[3] <= R2[1]) or (R1[1] >= R2[3]):
        return False
    return True


def fitted(floor_plan, rooms):
    minFloorX = min(floor_plan, key=lambda c: c["x"])["x"]
    maxFloorX = max(floor_plan, key=lambda c: c["x"])["x"]
    minFloorY = min(floor_plan, key=lambda c: c["y"])["y"]
    maxFloorY = max(floor_plan, key=lambda c: c["y"])["y"]
    networks=[[],[]]

    for room in rooms:
        newHeight = max(room["height"], room["width"])
        newWidth = min(room["height"], room["width"])
        room["width"] = newWidth
        room["height"] = newHeight
        if room["type"] in networks[0]:
            networks[1][networks[0].index(room["type"])].append(room)
        else:
            tempArray=[room]
            networks[0].append(room["type"])
            networks[1].append(tempArray)
    rooms.sort(key=lambda room: -room["height"])
    rooms.sort(key=returnType)
    fitted_rooms = [rooms[0]]

    horizontal = True
    isFirstVertical = True
    topLeft = True
    isFirstBottomRight = True
    heightFirstBottomRight = 0
    doorSize = 20
    boundingsTop = [[rooms[0]["anchorTopLeftX"], rooms[0]["anchorTopLeftY"], rooms[0]["anchorTopLeftX"] + rooms[0]["width"], rooms[0]["anchorTopLeftY"]+rooms[0]["height"]]]
    boundingsLeft = [[rooms[0]["anchorTopLeftX"], rooms[0]["anchorTopLeftY"], rooms[0]["anchorTopLeftX"] + rooms[0]["width"], rooms[0]["anchorTopLeftY"]+rooms[0]["height"]]]
    for roomNumber, room in enumerate(rooms):
        if roomNumber == 0:
            continue
        prevRoom = fitted_rooms[-1]
        anchorXCheck = prevRoom["anchorTopLeftX"] + prevRoom["width"]
        if topLeft:
            if horizontal:
                if anchorXCheck + room["width"] <= maxFloorX:
                    room["anchorTopLeftX"] = anchorXCheck
                    fitted_rooms.append(room)
                    boundingsTop.append([room["anchorTopLeftX"], room["anchorTopLeftY"], room["anchorTopLeftX"] + room["width"], room["anchorTopLeftY"]+room["height"]])
                else:
                    horizontal = False
                    prevRoom["anchorTopLeftY"] = rooms[0]["height"] + doorSize
                    anchorXCheck = 0
            if not horizontal:
                anchorYCheck = prevRoom["anchorTopLeftY"] + prevRoom["height"]
                room["width"], room["height"]=room["height"] , room["width"]
                if isFirstVertical:
                    prevRoom["anchorTopLeftY"] = 0
                    anchorYCheck -= prevRoom["height"]
                    isFirstVertical = False
                if anchorYCheck + room["height"] <= maxFloorY:
                    room["anchorTopLeftY"] = anchorYCheck
                    fitted_rooms.append(room)
                    boundingsLeft.append([room["anchorTopLeftX"], room["anchorTopLeftY"], room["anchorTopLeftX"] + room["width"], room["anchorTopLeftY"]+room["height"]])
                else:
                    topLeft = False
                    horizontal = True
                    isFirstVertical = True
        if not topLeft:
            anchorXCheck = prevRoom["anchorTopLeftX"]
            anchorYCheck = maxFloorY - room["height"]
            bounds = [anchorXCheck - room["width"], anchorYCheck, anchorXCheck - room["width"] + room["width"], anchorYCheck + room["height"]]
            if horizontal:
                if isFirstBottomRight:
                    anchorXCheck = maxFloorX - room["width"]
                    room["anchorTopLeftX"] = anchorXCheck
                    room["anchorTopLeftY"] = anchorYCheck
                    heightFirstBottomRight = anchorYCheck
                    isFirstBottomRight = False
                    fitted_rooms.append(room)
                    continue
                canPlace = True
                for bound in boundingsLeft:
                    if isRectangleOverlap(bounds, bound):
                        canPlace = False
                        break
                if canPlace:
                    room["anchorTopLeftX"] = bounds[0]
                    room["anchorTopLeftY"] = bounds[1]
                    fitted_rooms.append(room)
                else:
                    horizontal = False
                    isFirstVertical = True
                    prevRoom["anchorTopLeftY"] = heightFirstBottomRight - doorSize

            if not horizontal:
                room["width"], room["height"]=room["height"] , room["width"]
                anchorXCheck = maxFloorX - room["width"]
                anchorYCheck = prevRoom["anchorTopLeftY"] - room["height"]
                if isFirstVertical:
                    prevRoom["anchorTopLeftY"] = maxFloorY-fitted_rooms[-1]["height"]
                    isFirstVertical = False
                bounds = [anchorXCheck - room["width"], anchorYCheck, anchorXCheck - room["width"] + room["width"], anchorYCheck + room["height"]]
                canPlace = True
                for bound in boundingsTop:
                    if isRectangleOverlap(bounds, bound):
                        canPlace = False
                        break
                if canPlace:
                    room["anchorTopLeftX"] = anchorXCheck
                    room["anchorTopLeftY"] = anchorYCheck
                    fitted_rooms.append(room)
                else:
                    break
    if len(rooms) == len(fitted_rooms):
        return fitted_rooms
    raise RuntimeError("Did not manage to fit all rooms into the floor plan.")


def parse_json(filepath):
    with open(filepath, "r") as rawinput:
        data = json.load(rawinput)
        floor_plan = data["planBoundary"]
        room_dict = data["rooms"]
    # return  ( FloorPlanCoordinates, RoomDictionary )
    return (floor_plan, room_dict)


def main():
    (width, height) = (600, 600)
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    floor_plan, room_dict = parse_json(
        "main/example.json")
    parsed = fitted(floor_plan, room_dict)
    screen.fill((0, 0, 0), (0, 0, width, height))
    for element in parsed:
        if element["type"]=="workRoom":
            col = (255,0,0)
        if element["type"]=="meetRoom":
            col = (0,0,255)
        if element["type"]=="openWork":
            col = (0,255,0)
        pygame.draw.rect(
            screen, col, (element["anchorTopLeftX"], element["anchorTopLeftY"], element["width"], element["height"]), 4)
    pygame.display.flip()
    pygame.display.update()
    while True:
        pass


main()
