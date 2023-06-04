import cv2
import torch
import numpy as np
import math
import json

class Tracker:
    def __init__(self):
        # Store the center positions of the objects
        self.center_points = {}
        # Keep the count of the IDs
        # each time a new object id detected, the count will increase by one
        self.id_count = 0


    def update(self, objects_rect):
        # Objects boxes and ids
        objects_bbs_ids = []

        # Get center point of new object
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2

            # Find out if that object was detected already
            same_object_detected = False
            for id, pt in self.center_points.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])

                if dist < 35:
                    self.center_points[id] = (cx, cy)
#                    print(self.center_points)
                    objects_bbs_ids.append([x, y, w, h, id])
                    same_object_detected = True
                    break

            # New object is detected we assign the ID to that object
            if same_object_detected is False:
                self.center_points[self.id_count] = (cx, cy)
                objects_bbs_ids.append([x, y, w, h, self.id_count])
                self.id_count += 1

        # Clean the dictionary by center points to remove IDS not used anymore
        new_center_points = {}
        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center

        # Update dictionary with IDs not used removed
        self.center_points = new_center_points.copy()
        return objects_bbs_ids

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

cap = cv2.VideoCapture('highway.mp4')

# Initialize the VideoWriter
output_file = 'output.mp4'
output_fps = 5  # Adjust the desired output frame rate
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
output_dimensions = (1020, 600)  # Adjust the desired output dimensions
out = cv2.VideoWriter(output_file, fourcc, output_fps, output_dimensions)

count = 0
tracker = Tracker()

cv2.namedWindow('FRAME')

area1 = [(535, 445), (320, 445), (320, 480), (535, 480)]
area2 = [(580, 410), (770, 410), (770, 435), (580, 435)]
area_1 = set()
area_2 = set()

# Dictionary to store the results
results_dict = {"frames": []}

while True:
    ret, frame = cap.read()
    if not ret:
        break
    count += 1
    if count % 3 != 0:
        continue
    frame = cv2.resize(frame, (1020, 600))

    results = model(frame)

    objectList = []
    for index, rows in results.pandas().xyxy[0].iterrows():
        x = int(rows[0])
        y = int(rows[1])
        x1 = int(rows[2])
        y1 = int(rows[3])
        objName = str(rows['name'])
        objectList.append([x, y, x1, y1])

    id_bbox = tracker.update(objectList)
    vehicle_counts = {}
    for bbox in id_bbox:
        x2, y2, x3, y3, id = bbox
        cv2.rectangle(frame, (x2, y2), (x3, y3), (0, 255, 0), 2)
        cv2.circle(frame, (x3, y3), 4, (0, 0, 255), -1)
        result1 = cv2.pointPolygonTest(np.array(area1, np.int32), ((x3, y3)), False)
        result2 = cv2.pointPolygonTest(np.array(area2, np.int32), ((x3, y3)), False)
        if result1 > 0:
            area_1.add(id)
            obj_name = str(rows['name'])
            if id in vehicle_counts:
                if obj_name in vehicle_counts[id]:
                    vehicle_counts[id][obj_name] += 1
                else:
                    vehicle_counts[id][obj_name] = 1
            else:
                vehicle_counts[id] = {obj_name: 1}
        if result2 > 0:
            area_2.add(id)

    cv2.polylines(frame, [np.array(area1, np.int32)], True, (255, 0, 255), 2)
    cv2.polylines(frame, [np.array(area2, np.int32)], True, (255, 0, 255), 2)

    a1 = len(area_1)
    a2 = len(area_2)

    # Store the values in the results dictionary for the current frame
    frame_results = {"a1": a1, "a2": a2, "vehicle_counts": vehicle_counts}
    results_dict["frames"].append(frame_results)

    cv2.putText(frame, str(a1), (549, 465), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
    cv2.putText(frame, str(a2), (800, 410), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

    cv2.imshow("FRAME", frame)
    out.write(frame)

    # Save the results dictionary to a JSON file
    with open('output.json', 'w') as json_file:
        json.dump(results_dict, json_file)

    if cv2.waitKey(0) & 0xFF == 27:
        break

out.release()
cap.release()
cv2.destroyAllWindows()
