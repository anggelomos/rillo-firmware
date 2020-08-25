import cv2
import numpy as np

def camera_reader(model, image_size: tuple=(600, 400), image_crop: float=2/3, blur_amount: int=5):
    """ Read the camera input and processes it to get a string using ocr.

    Parameters
    ----------
    model : [type]
        Trained ocr model
    image_size : tuple, optional
        Dimensions of the image resizing, by default (600, 400)
    image_crop : float, optional
        Zone of the image that will be processed (from 0 to 1.0), by default 2/3
    blur_amount : int, optional
        Amount of blur in the processed image, by default 5

    Returns
    -------
    read_character: str
        Recognized character
    """

    capture = cv2.VideoCapture(0)
    ret, img = capture.read()
    img = cv2.resize(img,image_size)
    width = len(img[0])*image_crop
    img = img[:,0:int(width)]
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(blur_amount,)*2,0)
    thresh = cv2.adaptiveThreshold(blur,255,1,1,31,2)
    contours,hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        if cv2.contourArea(cnt)>2000:
            [x,y,w,h] = cv2.boundingRect(cnt)
            if  h>100:
                try:
                    roi = thresh[y-50:y+h,x:x+w]
                except cv2.error:
                    roi = thresh[y:y+h,x:x+w]
                roismall = cv2.resize(roi,(10,10))
                roismall = roismall.reshape((1,100))
                roismall = np.float32(roismall)
                retval, results, neigh_resp, dists = model.findNearest(roismall, k = 1)
                read_character = str(chr((results[0][0])))

    capture.release()
    cv2.destroyAllWindows()
    return read_character