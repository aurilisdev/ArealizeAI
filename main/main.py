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
    print("jada")
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
        
    heightFirstBottomRight = 0
    widthFirstBottomRight = 0
    widthFirstBottomRightVertical=0
    doorSize = 20  
    

    fitted_units = []
    fitted_rooms=[]
    anchorXCheck=minFloorX
    anchorYCheck=minFloorY
    boundingsTop=[]
    boundingsLeft=[]
    
    for unitNumber, unit in enumerate(units):
        if anchorXCheck + unit["width"] <= maxFloorX and anchorYCheck + unit["height"]<=maxFloorY:
            fitted_units.append(unit)
            for room in unit["rooms"]:
                room["anchorTopLeftX"] = anchorXCheck
                room["anchorTopLeftY"] = minFloorY
                fitted_rooms.append(room)
                boundingsTop.append([room["anchorTopLeftX"], room["anchorTopLeftY"], room["anchorTopLeftX"] + room["width"], room["anchorTopLeftY"]+room["height"]])
                anchorXCheck=room["anchorTopLeftX"]+room["width"]
   
    #over her 1

    units2=[]
    for unit in units:
        if unit in fitted_units:
            pass
        else:
            units2.append(unit)
    units=units2.copy()
    if len(fitted_rooms)>0:
        anchorYCheck=minFloorY+fitted_rooms[0]["height"]+doorSize
    else:
        anchorYCheck=minFloorY
    anchorXCheck=minFloorX
    
    for unitNumber, unit in enumerate(units):
        unit["width"], unit["height"]=unit["height"] , unit["width"]
        if unitNumber == 0:
            continue
        if anchorYCheck + unit["height"] <= maxFloorY and minFloorX + unit["width"]<=maxFloorX:
            fitted_units.append(unit)
            for room in unit["rooms"]:
                room["width"], room["height"]=room["height"] , room["width"]
                room["anchorTopLeftX"] = minFloorX
                room["anchorTopLeftY"] = anchorYCheck
                fitted_rooms.append(room)
                boundingsLeft.append([room["anchorTopLeftX"], room["anchorTopLeftY"], room["anchorTopLeftX"] + room["width"], room["anchorTopLeftY"]+room["height"]])
                anchorYCheck=room["anchorTopLeftY"]+room["height"]

    #over her 2

    heightFirstBottomRight=maxFloorY+doorSize
    widthFirstBottomRight=maxFloorX+doorSize

    units2=[]
    for unit in units:
        if unit in fitted_units:
            pass
        else:
            units2.append(unit)
    units=units2.copy()

    anchorYCheck=maxFloorY
    anchorXCheck=maxFloorX
    
    forste = 1
    for unitNumber, unit in enumerate(units):
        unit["width"], unit["height"]=unit["height"] , unit["width"]
        if anchorXCheck - unit["width"] >= minFloorX and maxFloorY- unit["height"]>=minFloorY:
            kreasj=0
            midanchorX=anchorXCheck
            midanchorY=anchorYCheck
            for room in unit["rooms"]:
                bounds = [midanchorX - room["width"], midanchorY - room["height"], midanchorX , midanchorY]
                for bound in boundingsTop + boundingsLeft:
                    if isRectangleOverlap(bounds, bound):
                        kreasj=1
                        break
                midanchorX-=room["width"]
            if kreasj == 0:
                fitted_units.append(unit)
                forste2=-1
                for room in unit["rooms"]:
                    forste2+=1
                    if forste == 1 and forste2==1:
                        anchorXCheck-=doorSize
                        forste =0
                        heightFirstBottomRight=fitted_rooms[-1]["anchorTopLeftY"]
                        widthFirstBottomRight=fitted_rooms[-1]["anchorTopLeftX"]
                    room["anchorTopLeftX"] = anchorXCheck-room["width"]
                    room["anchorTopLeftY"] = maxFloorY-room["height"]
                    fitted_rooms.append(room)

                    anchorXCheck-=room["width"]

    #over her 3

    widthFirstBottomRightVertical=maxFloorX+doorSize

    units2=[]
    for unit in units:
        if unit in fitted_units:
            pass
        else:
            units2.append(unit)
    units=units2.copy()
    anchorXCheck=maxFloorX
    anchorYCheck=heightFirstBottomRight

    forste = 1
    for unitNumber, unit in enumerate(units):
        unit["width"], unit["height"]=unit["height"] , unit["width"]
        if anchorXCheck - unit["width"] >= minFloorX and anchorYCheck- unit["height"]>=minFloorY:
            kreasj=0
            midanchorX=anchorXCheck
            midanchorY=anchorYCheck
            for room in unit["rooms"]:
                room["width"], room["height"]=room["height"] , room["width"]
                bounds = [midanchorX - room["width"], midanchorY - room["height"], midanchorX , midanchorY]
                for bound in boundingsTop + boundingsLeft:
                    if isRectangleOverlap(bounds, bound):
                        kreasj=1
                        break
                midanchorY-=room["height"]
            if kreasj == 0:
                fitted_units.append(unit)
                forste2=-1
                for room in unit["rooms"]:
                    forste2+=1
                    if forste == 1 and forste2==0:
                        widthFirstBottomRightVertical=maxFloorX-room["width"]
                        anchorYCheck-=doorSize
                        forste=0
                    room["anchorTopLeftX"] = maxFloorX-room["width"]
                    room["anchorTopLeftY"] = anchorYCheck-room["height"]
                    fitted_rooms.append(room)
                    anchorYCheck-=room["height"] 

    #over her 4
    if len(fitted_rooms)==0:
        raise RuntimeError("Did not manage to fit all rooms into the floor plan.")
    if len(rooms) == len(fitted_rooms):
        return fitted_rooms
    Inside_rooms=[]
    for room in rooms:
        if room in fitted_rooms:
            pass
        else:
            Inside_rooms.append(room)
    #her skriv inn koordinatene til rom 1 ned mot høyre(x koordinatet kan være fra det første rommet nedover, bruk boundleft, bound top)
    #skriv inn koordinatene til rommet nederst til venstre 
    if len(boundingsLeft)>1:
        coordinateminx=max(boundingsTop[0][2] , boundingsLeft[0][2]) +doorSize
    else:
        coordinateminx=boundingsTop[0][2] +doorSize

    coordinatemaxx=min(widthFirstBottomRight, widthFirstBottomRightVertical)-doorSize
    coordinateminy=boundingsTop[0][3] +doorSize
    coordinatemaxy=heightFirstBottomRight -doorSize
    coordinates = [{"x" : coordinateminx, "y": coordinateminy}, {"x": coordinatemaxx, "y": coordinatemaxy}]
    print(coordinates)
    print(widthFirstBottomRightVertical, widthFirstBottomRight)
    fitted_rooms.extend(fitted(coordinates, Inside_rooms))
    return fitted_rooms


def parse_json(filepath):
    with open(filepath, "r") as rawinput:
        data = json.load(rawinput)
        floor_plan = data["planBoundary"]
        room_dict = data["rooms"]
    # return  ( FloorPlanCoordinates, RoomDictionary )
    return (floor_plan, room_dict)


def main():
    floor_plan, room_dict = parse_json(
        "example.json")
    parsed = fitted(floor_plan, room_dict)
    (width, height) = (max(floor_plan, key=lambda c: c["x"])["x"], max(floor_plan, key=lambda c: c["y"])["y"])
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    screen.fill((0, 0, 0), (0, 0, width, height))
    for element in parsed:
        if element["type"]=="workRoom":
            col = (255,0,0)
        if element["type"]=="meetRoom":
            col = (0,0,255)
        if element["type"]=="openWork":
            col = (0,255,0)
        #col =(rand.randint(0, 255), rand.randint(0, 255),rand.randint(0, 255))
        pygame.draw.rect(
            screen, col, (element["anchorTopLeftX"], element["anchorTopLeftY"], element["width"], element["height"]), 4)
    pygame.display.flip()
    pygame.display.update()
    while True:
        pass

main()
