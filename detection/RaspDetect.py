import cv2
import time
import requests
import shutil
import os

# save screenshot
save_path = './detection/'

# read camera 
camera = cv2.VideoCapture(-1)

if (camera.isOpened()):
    print('Open')
else:
    print('Camera lost')


fps = 5

pre_frame = None

while(1):
    start = time.time()
    # read steam
    ret, frame = camera.read()

    # covert to gray image
    gray_lwpCV = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if not ret:
        break
    end = time.time()

    cv2.imshow("capture", frame)

    # detect motion
    seconds = end - start
    if seconds < 1.0 / fps:
        time.sleep(1.0 / fps - seconds)
    gray_lwpCV = cv2.resize(gray_lwpCV, (500, 500))
    # Gaussian blur the steam
    gray_lwpCV = cv2.GaussianBlur(gray_lwpCV, (21, 21), 0)

    # if there is no current background. use current image as the bg
    if pre_frame is None:
        pre_frame = gray_lwpCV
    else:
        # absdiff calculate the difference and input on one image
        img_delta = cv2.absdiff(pre_frame, gray_lwpCV)
        thresh = cv2.threshold(img_delta, 25, 255, cv2.THRESH_BINARY)[1]

        # dilate the thresholded image to fill in holes, then find contours
	    # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        _, contours, _= cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            # set sensitive value
            # contourArea calcuate the detect object area
            if cv2.contourArea(c) < 1000:
                continue
            else:
                print("Detected!" + str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
                r = requests.post('http://10.50.0.127:3000/motion', json = {"detected": 1, "time":
                                                                            str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))})
                
                cv2.imwrite('test.jpg', frame)
                src = "/home/pi/Desktop/Incubator-IoT-master/detection/test.jpg"
                dst = "/var/www/html/image/test.jpg"
                shutil.move(src,dst)
                
                break
        pre_frame = gray_lwpCV

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


camera.release()
# close all windows
cv2.destroyAllWindows()