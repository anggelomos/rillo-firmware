#Testing code for OCR
import cv2
import numpy as np
import sys

#---------------------------------------------------------LOADING DATA---------------------------------------------------
#Loading of data
samples = np.loadtxt('generalsamples.data',np.float32)
responses = np.loadtxt('generalresponses.data',np.float32)
print("Tamaño muestras: ", samples.shape)
print("Tamaño de respuestas: ", responses.shape)
responses = responses.reshape((responses.size,1))

#Model creation and training
model = cv2.ml.KNearest_create()
model.train(samples, cv2.ml.ROW_SAMPLE, responses)

#---------------------------------------------------------TESTING MODEL---------------------------------------------------

#Loading test image and creation of base image to add the results of identification
img = cv2.imread("Testing/Image_3.jpg", cv2.IMREAD_COLOR)
img = cv2.resize(img,(600,400))
out = np.zeros(img.shape,np.uint8)
width = len(img[0])*(2/3)
img = img[:,0:int(width)]


#Processing of testing image
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

#Image Smoothing
blur = cv2.GaussianBlur(gray,(5,5),0)#suaviza los bordes
cv2.imshow("Smoothed", blur)

#Thresholding of one-dimensional image
thresh = cv2.adaptiveThreshold(blur,255,1,1,31,2)


cv2.imshow("Preprocessed image", thresh)

#Countours identification with simple methods
contours,hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:
    if cv2.contourArea(cnt)>2000:
        [x,y,w,h] = cv2.boundingRect(cnt)
        if  h>100:
            try:
                cv2.rectangle(img,(x,y-50),(x+w,y+h),(0,0,255),2)
                roi = thresh[y-50:y+h,x:x+w]
                cv2.imshow("LETRA", roi)
            except cv2.error:
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
                roi = thresh[y:y+h,x:x+w]
                cv2.imshow("LETRA", roi)
            roismall = cv2.resize(roi,(10,10))
            roismall = roismall.reshape((1,100))
            roismall = np.float32(roismall)
            retval, results, neigh_resp, dists = model.findNearest(roismall, k = 1)
            string = str(chr((results[0][0])))
            cv2.putText(out,string,(x,y+h),0,8,(255,255,255))

cv2.imshow('Input Image',img)
cv2.imshow('Indentification Result', out)
cv2.waitKey(0)