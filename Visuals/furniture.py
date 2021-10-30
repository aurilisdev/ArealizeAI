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
    for unit in units:
        for room in unit:
            rooms.append(room)
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

    if len(rooms) == len(fitted_rooms):
        return fitted_rooms
    Inside_rooms=rooms[len(fitted_rooms):]
    #her skriv inn koordinatene til rom 1 ned mot høyre(x koordinatet kan være fra det første rommet nedover, bruk boundleft, bound top)
    #skriv inn koordinatene til rommet nederst til venstre
    coordinates = [{"x" : max(boundingsLeft[0][2] , boundingsLeft[1][2]) +doorSize, "y": boundingsLeft[0][3] +doorSize}, {"x": min(widthFirstBottomRight, widthFirstBottomRightVertical)-doorSize, "y": heightFirstBottomRight -doorSize}]
    fitted_rooms.extend(fitted(coordinates, Inside_rooms))
    return fitted_rooms

    raise RuntimeError("Did not manage to fit all rooms into the floor plan.")


furniDim = 120
padding=15
def furnish(parsed):
    #furniture types: 1=desk, 2=cupboard, 3=plant, 4=table
    #desk width = 70x70, plant width=70x70, cupboard width = 140x70, table width = 70x70
    #everything needs 15 px padding on either side
    furniturePos=[]
    noFurn=[]

    for room in parsed:
        furnNum=0
        roomFurniture = {}
        if room['width']>100 and room['height']>100:
            numSpots = (room['width']-(padding))//furniDim
            print("Numspots: ", numSpots)
            #if numSpots!=0: #create atleast one desk
            roomFurniture['anchorTopLeftX']=room['anchorTopLeftX']+padding
            roomFurniture['anchorTopLeftY'] = room['anchorTopLeftY']
            roomFurniture['type']=1

            if len(roomFurniture)!=0: #dict not empty
                furniturePos.append(roomFurniture.copy())
                roomFurniture.clear()
                print("drawing desk")
            furnNum+=1
            for i in range(1, numSpots+1): #adding furniture in the top row, adds one peice of furniture per iteration
                typeOfFurniture = rand.randint(1,5) #fordi vi vil ha færre planter
                print(typeOfFurniture)
                if typeOfFurniture==5:
                    roomFurniture['anchorTopLeftX']=room['anchorTopLeftX']+(int(furniDim/1.5))*i+padding
                    roomFurniture['anchorTopLeftY'] = room['anchorTopLeftY']
                    roomFurniture['type']=3
                    if len(roomFurniture)!=0: #dict not empty
                        furniturePos.append(roomFurniture.copy())
                        roomFurniture.clear()
                    print("drawing plant")
                    furnNum+=1
                if room['type']=="workRoom" or room['type']=="openWork":
                    if typeOfFurniture==1 or typeOfFurniture==2: #random spacing between desks.
                        roomFurniture['anchorTopLeftX']=room['anchorTopLeftX']+furniDim*i+padding
                        roomFurniture['anchorTopLeftY'] = room['anchorTopLeftY']
                        roomFurniture['type']=1
                        if len(roomFurniture)!=0: #dict not empty
                            furniturePos.append(roomFurniture.copy())
                            roomFurniture.clear()
                        print("drawing desk")
                        furnNum+=1

                if room['type']=="workRoom":
                    if typeOfFurniture==3 or typeOfFurniture==4:
                        if i<=(num-3): #then we can place a cupboard
                            roomFurniture['anchorTopLeftX']=room['anchorTopLeftX']+furniDim*i+padding
                            roomFurniture['anchorTopLeftY'] = room['anchorTopLeftY']
                            roomFurniture['type']=2
                            if len(roomFurniture)!=0: #dict not empty
                                furniturePos.append(roomFurniture.copy())
                                roomFurniture.clear()
                            print("cupboard")
                            furnNum+=1

                if len(roomFurniture)!=0: #dict not empty

                    furniturePos.append(roomFurniture.copy())
                    roomFurniture.clear()


                plantInBottomLeft = rand.randint(0,1)
                plantInBottomRight = rand.randint(0,1)

                roomFurniture.clear()
                if plantInBottomLeft==1:
                    roomFurniture['anchorTopLeftX']=room['anchorTopLeftX']+padding
                    roomFurniture['anchorTopLeftY'] = room['anchorTopLeftY']+room['height']-int(furniDim/1.5)
                    roomFurniture['type']=3
                    furnNum+=1
                if len(roomFurniture)!=0:
                    furniturePos.append(roomFurniture.copy())
                    roomFurniture.clear()
                if plantInBottomRight==1:
                    roomFurniture['anchorTopLeftX']=room['anchorTopLeftX']+room['width']-int(furniDim/1.5)-padding
                    roomFurniture['anchorTopLeftY'] = room['anchorTopLeftY']+room['height']-int(furniDim/1.5)
                    roomFurniture['type']=3
                    furnNum+=1
                if len(roomFurniture)!=0:
                    furniturePos.append(roomFurniture.copy())
                    roomFurniture.clear()
        noFurn.append(furnNum)
        furnNum=0
    #print(" furniture pos: ", furniturePos)



            # elif room['width']>100 and room['height']<100:
            #
            # elif room['width']<100 and room['height']>100:
            #
            # else:

    return noFurn, furniturePos






def parse_json(filepath):
    with open(filepath, "r") as rawinput:
        data = json.load(rawinput)
        floor_plan = data["planBoundary"]
        room_dict = data["rooms"]
    # return  ( FloorPlanCoordinates, RoomDictionary )
    return (floor_plan, room_dict)

def text_objects(text, font):
    textSurface = font.render(text, True, (0,0,0))
    return textSurface, textSurface.get_rect()

floor_plan, room_dict = parse_json("example.json")
parsed = fitted(floor_plan, room_dict)
noFurn, furn = furnish(parsed)
print(noFurn)
print(furn)

desk = pygame.transform.scale(pygame.image.load("desk.png"), (furniDim,furniDim))
plant = pygame.transform.scale(pygame.image.load("plant.png"), (int(furniDim/1.5),int(furniDim/1.5)))



def main():
    (width, height) = (1000, 1000)
    pygame.init()
    screen = pygame.display.set_mode((width, height))


    screen.fill((255,255,255), (0, 0, width, height))
    for element in parsed:
        if element["type"]=="workRoom":
            col = (255,0,0)
        if element["type"]=="meetRoom":
            col = (0,0,255)
        if element["type"]=="openWork":
            col = (0,255,0)
        col =(rand.randint(0, 255), rand.randint(0, 255),rand.randint(0, 255))





        # if element['width']>100 and element['height']>100:
        #     pygame.draw.rect(screen, (255,255,255), (element["anchorTopLeftX"], element["anchorTopLeftY"], element["width"], element["height"]), 4)
        #
        # elif element['width']>100 and element['height']<100:
        #     pygame.draw.rect(screen, (255,255,0), (element["anchorTopLeftX"], element["anchorTopLeftY"], element["width"], element["height"]), 4)
        #
        # elif element['width']<100 and element['height']>100:
        #     pygame.draw.rect(screen, (255,0,0), (element["anchorTopLeftX"], element["anchorTopLeftY"], element["width"], element["height"]), 4)
        #
        # else:

        largeText = pygame.font.Font('freesansbold.ttf',15)
        TextSurf, TextRect = text_objects(str(element['width'])+"x"+str(element['height']), largeText)
        TextRect.center = (element['anchorTopLeftX']+element['width']/2, element['anchorTopLeftY']+element['height']/2)
        screen.blit(TextSurf, TextRect)

        pygame.draw.rect(screen, (0,0,0), (element["anchorTopLeftX"], element["anchorTopLeftY"], element["width"], element["height"]), 4)


        for f in furn:
            xval = f['anchorTopLeftX']
            yval = f['anchorTopLeftY']
            furnType = f['type']

            if furnType==1:
                furnW=furniDim
                furnH=furniDim
                #pygame.draw.rect(screen, (0,255,255), (xval,yval, furnW,furnH), 4)
                screen.blit(desk, (xval,yval, furnW,furnH))
            if furnType==3:
                furnW=furniDim
                furnH=furniDim
                #pygame.draw.rect(screen, (0,255,0), (xval,yval, furnW,furnH), 4)
                screen.blit(plant, (xval,yval, furnW,furnH))
            if furnType==4:
                furnW=furniDim
                furnH=furniDim
                pygame.draw.rect(screen, (0,0,255), (xval,yval, furnW,furnH), 4)
            if furnType == 2:
                furnW=2*furniDim
                furnH=furniDim
                pygame.draw.rect(screen, (255,0,0), (xval,yval, furnW,furnH), 4)


    pygame.display.flip()
    pygame.display.update()
    # for i in range(3*10**8):
    #     pass
while True:
    main()
