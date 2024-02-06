import cv2, time
from datetime import datetime
import pandas as pd

# We get the camera of out computer. If we have multiple cameras, the index will represent each of them. 
video = cv2.VideoCapture(1)

# We initialize a first_frame instance
first_frame = None
status_list = [None, None]
times = []
df = pd.DataFrame(columns=["Start", "End"])

# Give some time for the camera to initialize
time.sleep(2)

while True:
    # Check the frame of the camera
    check, frame = video.read()

    # We define status = 0 because at first there is no object detected
    status = 0
    

    # We generate a gray version of the image we are capturing. 
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # We apply a Gaussian Blur to erase noise and improve accuracy -> for delta calculation.
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Only if the fist_frame is None, we update the first_frame value.
    if first_frame is None: 
       first_frame = gray

       # We skip to the next iteration
       continue
    
    # We compute the delta as the difference between the current frame and our original frame.
    delta_frame = cv2.absdiff(first_frame, gray)

    # We define a threshold to get only the most significant differences between our original delta and our current delta . 
    thresh_delta = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1] # We acess the second element

    # We dilate the image to erase the smallest changes. 
    thresh_delta = cv2.dilate(thresh_delta, None, iterations=2)

    (cnts, _) = cv2.findContours(thresh_delta.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in cnts: 
        if cv2.contourArea(contour) < 50000: # We only get those movements corresponding to big objects. 
            continue

        # If an object is detected, we set the status to 1
        status = 1
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)

    # We track the movement within our image
    status_list.append(status)
    if status_list[-1] == 1 and status_list[-2] == 0:
       times.append(datetime.now())
    if status_list[-1] == 0 and status_list[-2] == 1:
       times.append(datetime.now())

    cv2.imshow("Capturing", gray)
    cv2.imshow("Delta Frame", delta_frame)
    cv2.imshow("Threshold Frame", thresh_delta)
    cv2.imshow("Color Frame", frame)

    # Pressing any button the system will stop
    #cv2.waitKey(0)

    key = cv2.waitKey(1)

    if key ==ord("q"):

        # If we quit with an object on screen, record as the exiting time the time we break the loop. 
        if status == 1:
            times.append(datetime.now())
        break

    print(status)

print(times)
print(status_list)

# We generate a dataframe containing all the movements detected in our videocam. 
for i in range(0, len(times), 2):
    df = df._append({"Start":times[i], "End": times[i+1]}, ignore_index = True)
df.to_csv("03_video_objects_detection/Output/Datetime.csv")

video.release()
cv2.destroyAllWindows() 