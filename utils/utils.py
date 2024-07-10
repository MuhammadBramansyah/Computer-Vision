import cv2 
import numpy as np 
import pytz 
import json 

from datetime import datetime 

wib_timezone = pytz.timezone('Asia/Jakarta')
limits_jajargenjang = np.array([[439, 597], [1431, 990], [1593, 343], [1074, 314]], np.int32)
def save_json(timestamp, stream_id, location, number_of_cars, file_path):
    data = {
        "timestamp": timestamp,
        "stream_id": stream_id,
        "location": location,
        "number_of_cars": number_of_cars
    }

    with open(file_path, 'a') as json_file: 
        json.dump(data, json_file)
        json_file.write('\n')

def calculate_duration(enter_times, id):
    exit_time = datetime.now().astimezone(wib_timezone)
    enter_time = enter_times.get(id)
    if enter_time:
        duration = exit_time - enter_time
        return duration.total_seconds()
    else:
        return 0
    
def draw_parallelogram(frame):
    color = (0, 255, 0)  
    isClosed = True 
    thickness = 2
    cv2.polylines(frame, [limits_jajargenjang], isClosed, color, thickness)