import numpy as np
import json
import pygame as pygame
from pygame import color
import random as rand

from pygame.constants import TIMER_RESOLUTION

#def returnType(e):
#    return e["type"]

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
    roomtypes={"names":[],"contained":[]}
    floorWidth=maxFloorX-minFloorX
    floorHeight=maxFloorY-minFloorY
    for room in rooms:
        newHeight = max(room["height"], room["width"])
        newWidth = min(room["height"], room["width"])
        room["width"] = newWidth
        room["height"] = newHeight
        if room["type"] in roomtypes["names"]:
            typeIndex=roomtypes["names"].index(room["type"])
            roomtypes["contained"][typeIndex]+=1
        else:
            roomtypes["names"].append(room["type"])
            roomtypes["contained"].append(1)
    rooms.sort(key=lambda room: -room["height"])

    #rooms.sort(key=returnType)
    #Sorterer rom etter type attpå type
    units=[]
    while 0 < len(rooms):
        unit=[rooms[0]]
        topop=[0]
        typeIndex=roomtypes["names"].index(rooms[0]["type"])
        roomtypes["contained"][typeIndex]-=1
        if not roomtypes["contained"][typeIndex]==0:            
            for roomNumber, room in enumerate(rooms):
                if roomNumber == 0:
                    continue
                if room["type"]==rooms[0]["type"]:
                    unit.append(room)
                    roomtypes["contained"][typeIndex]-=1
                    topop.append(roomNumber)
                    if not roomtypes["contained"][typeIndex]==1:
                        break
        for n in reversed(topop):
            rooms.pop(n)
        units.append(unit)
    for unitNumb, unit in enumerate(units):
        width=0
        for room in unit:
            width+=room["width"]
        for roomindeks, room in enumerate(unit):
            room["indeks"]=roomindeks
            room["antall"]=len(unit)
            room["unit"] = unitNumb
            rooms.append(room)
        unit={
            "width":width,
            "height":unit[0]["height"],
            "id":unitNumb,
            "rooms":unit
        }
        units[unitNumb]=unit
        
            
    rooms[0]["anchorTopLeftX"], rooms[0]["anchorTopLeftY"] = minFloorX, minFloorY
    fitted_rooms = [rooms[0]]

    horizontal = True
    isFirstVertical = True
    topLeft = True
    isFirstBottomRight = True
    heightFirstBottomRight = 0
    widthFirstBottomRight = 0
    widthFirstBottomRightVertical=0
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
                    room["anchorTopLeftY"] = minFloorY
                    fitted_rooms.append(room)
                    boundingsTop.append([room["anchorTopLeftX"], room["anchorTopLeftY"], room["anchorTopLeftX"] + room["width"], room["anchorTopLeftY"]+room["height"]])
                else:
                    if room["indeks"]!=0:
                        #hopp tilbake så mange steg
                        anchorXCheck=fitted_rooms[-room["indeks"]]["anchorTopLeftX"]
                        anchorYCheck=fitted_rooms[-room["indeks"]]["anchorTopLeftY"]
                        for i in range(room["indeks"]):
                            fitted_rooms.pop()
                        for unit in units[room["unit"]+1:]:
                            if anchorXCheck+unit["width"]<=maxFloorX:
                                for room2 in unit["rooms"]:
                                    room2["anchorTopLeftX"] = anchorXCheck
                                    room2["anchorTopLeftY"] = minFloorY
                                    fitted_rooms.append(room2)
                                    anchorXCheck= anchorXCheck+room2["width"]
                                    boundingsTop.append([room2["anchorTopLeftX"], room2["anchorTopLeftY"], room2["anchorTopLeftX"] + room2["width"], room2["anchorTopLeftY"]+room2["height"]])
                                break
                        

                    horizontal = False
                    prevRoom["anchorTopLeftY"] = rooms[0]["height"] + doorSize +minFloorY
                    anchorXCheck = 0
                    
            if not horizontal:
                anchorYCheck = prevRoom["anchorTopLeftY"] + prevRoom["height"]
                room["anchorTopLeftX"]=minFloorX
                room["width"], room["height"]=room["height"] , room["width"]
                if isFirstVertical:
                    prevRoom["anchorTopLeftY"] = minFloorY
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
                    room["width"], room["height"]=room["height"] , room["width"]
                    anchorYCheck = maxFloorY - room["height"]
                    anchorXCheck = maxFloorX - room["width"]
                    room["anchorTopLeftX"] = anchorXCheck
                    room["anchorTopLeftY"] = anchorYCheck
                    heightFirstBottomRight = anchorYCheck
                    widthFirstBottomRight = anchorXCheck
                    isFirstBottomRight = False
                    fitted_rooms.append(room)
                    continue
                canPlace = True
                for bound in boundingsLeft + boundingsTop:
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
                    widthFirstBottomRightVertical=maxFloorX-room["width"]
                    prevRoom["anchorTopLeftY"] = maxFloorY-fitted_rooms[-1]["height"]
                    isFirstVertical = False
                bounds = [anchorXCheck - room["width"], anchorYCheck, anchorXCheck - room["width"] + room["width"], anchorYCheck + room["height"]]
                canPlace = True
                for bound in boundingsTop + boundingsLeft:
                    if isRectangleOverlap(bounds, bound):
                        canPlace = False
                        break
                if canPlace:
                    room["anchorTopLeftX"] = anchorXCheck
                    room["anchorTopLeftY"] = anchorYCheck
                    fitted_rooms.append(room)
                else:
                    break

    if len(rooms) <= len(fitted_rooms):
        return fitted_rooms
    Inside_rooms=[]
    for room in rooms:
        if room in fitted_rooms:
            pass
        else:
            Inside_rooms.append(room)
    print(len(rooms), len(fitted_rooms),  len(Inside_rooms))
    print(len(fitted_rooms)+len(Inside_rooms)-len(rooms), "dette tallet")
    #her skriv inn koordinatene til rom 1 ned mot høyre(x koordinatet kan være fra det første rommet nedover, bruk boundleft, bound top)
    #skriv inn koordinatene til rommet nederst til venstre 
    if len(boundingsLeft)>1:
        coordinateminx=max(boundingsLeft[0][2] , boundingsLeft[1][2]) +doorSize
    else:
        coordinateminx=boundingsLeft[0][2] +doorSize
    coordinatemaxx=min(widthFirstBottomRight, widthFirstBottomRightVertical)-doorSize
    coordinateminy=boundingsLeft[0][3] +doorSize
    coordinatemaxy=heightFirstBottomRight -doorSize
    coordinates = [{"x" : coordinateminx, "y": coordinateminy}, {"x": coordinatemaxx, "y": coordinatemaxy}]
    print("ja")
    fitted_rooms.extend(fitted(coordinates, Inside_rooms))
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
    drawn_rooms = []
    (width, height) = (800, 800)
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    floor_plan, room_dict = parse_json(
        "example.json")
    index = 0

    element = fitted(floor_plan, room_dict)

    while True:
        screen.fill((0, 0, 0), (0, 0, width, height))

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if element[index]["type"]=="workRoom":
                    col = (255,0,0)
                if element[index]["type"]=="meetRoom":
                    col = (0,0,255)
                if element[index]["type"]=="openWork":
                    col = (0,255,0)
                #col =(rand.randint(0, 255), rand.randint(0, 255),rand.randint(0, 255))
                drawn_rooms.append((element[index]["anchorTopLeftX"], element[index]["anchorTopLeftY"], element[index]["width"], element[index]["height"]))
                index += 1

            
        for dim in drawn_rooms:
            pygame.draw.rect(screen, col, dim, 4)

        pygame.display.flip()
        pygame.display.update()


main()
