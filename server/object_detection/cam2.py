# import the necessary packages
import datetime
import imutils
from imutils.video import VideoStream
import time
import cv2
from pygame import mixer
import random
import requests

mixer.init()

soundArray = []
for i in range(1, 10):
    soundArray.append(mixer.Sound(f'audio\\nicetalk{i}.wav'))


# Now, we'll setup the AWS Kinesis Video Stream
# Initialize the video source (webcam)
video_source = None
min_area = 1000
cv2.CAP_DSHOW = 700

# Take the camera and turn it on
vs = VideoStream(src=2).start()
time.sleep(2.0); 

# Initialize the first frame in the video stream - used to compare for motion
first_frame = None

timer = 0
frameCount = 0

#Sound Flags
sound_played = False
last_played_time = 0
sound_delay = 5 #seconds

while True:
    frameCount += 1
    if frameCount % 600 == 0:
        print("Frame count: ", frameCount)
        # take a new frame every 10 seconds
        first_frame = None
        frameCount = 0; 
    
    # Initialize the "first frame" which is intended to be a blank frame
    # There must be no objects right now
    frame = vs.read()
    if video_source is not None:
        frame = frame[1]  # Extract a frame from video capture

    text = "No trash"

    # If no camera available still, quit/break
    if frame is None:
        break

    # Pre-process the images
    # Resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # If the first frame is None, initialize it
    if first_frame is None:
        first_frame = gray
        continue

    # Compute absolute difference between first and current frame
    frame_delta = cv2.absdiff(first_frame, gray)

    # VERY IMPORTANT, DON'T UNDERSTAND BUT DON'T TOUCH
    thresh = cv2.threshold(frame_delta, 55, 180, cv2.THRESH_BINARY)[1]

    # Dilate the "threshold" to fill in holes, find contours on the images
    thresh = cv2.dilate(thresh, None, iterations=4)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # Loop over the contours
    for c in cnts:
        # If contour is too small, ignore
        if cv2.contourArea(c) < min_area:
            continue

        # Compute the bounding box, draw it, and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Trash in Frame"
        # Pay soudn effect

        if timer > 4000 and not sound_played:
            timer = 0
            sound = random.choice(soundArray)
            sound.play()
            sound_played = True
            last_played_time = time.time()

            # Send a request to the server
            try:
                current_time = datetime.datetime.now()
                print(f"Playing {sound} at {current_time}")
                formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
                payload = {
                    "trash_outside": False,
                }

                response = requests.post('http://localhost:8000/detectTrash', json=payload)
                if response.status_code == 200:
                    print("Successfully logged sound play to server.")
                else:
                    print(f"Failed to log sound play to server: {response.status_code}")
            except Exception as e:
                print(f"Error sending request to server: {e}")
                continue
                
        timer += 10
    
    if sound_played and (time.time() - last_played_time) > sound_delay:
        sound_played = False

    # Draw the text and timestamp on the frame
    cv2.putText(frame, "Litter Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    cv2.imshow("Security Feed", frame)
    cv2.imshow("Thresh", thresh)
    cv2.imshow("Frame Delta", frame_delta)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# Cleanup the camera and close any open windows
if video_source is None:
	vs.stop()
else:
	vs.release()
cv2.destroyAllWindows()