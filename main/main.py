import numpy as np
import json

def parse_json(filepath):
    with open(filepath, 'r') as rawinput:
        data = json.load(rawinput)
        floor_plan = data['planBoundary']
        room_dict = data['rooms']
    # return  ( FloorPlanCoordinates, RoomDictionary )
    return floor_plan, room_dict