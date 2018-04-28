# facerec.py for opencv3.1.0
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 11:42:11 2018
@author: 
    Version by:
    Oscar_Javier Avella-Gonzalez

Copyright [2018] [Oscar_Javier Avella-Gonzalez]

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" 
BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing 
permissions and limitations under the License.


"""


import cv2, sys, numpy, os,time

t_0 =time.time()

haar_face = 'haarcascade_frontalface_default.xml'
haar_eyes = 'haarcascade_eye.xml'

datasets = 'clientsDir'
# Part 1: Create fisherRecognizer
print('Training on clients Faces ...')
# Create a list of images and a list of corresponding names

#++++++++++++++++++++++++++++++
#Load training set
#++++++++++++++++++++++++++++++

#output images dimensions
dim=(130,100)
(images, labels, names, id) = ([], [], {}, 0)
for (subdirs, dirs, files) in os.walk(datasets):
    for subdir in dirs:
        names[id] = subdir
        subjectpath = os.path.join(datasets, subdir)
        for filename in os.listdir(subjectpath):
            path = subjectpath + '/' + filename
            label = id
            raw_im = cv2.imread(path, 0)
            if (raw_im.shape[0]!=dim[0] or raw_im.shape[1]!=dim[1]):
                out_im = cv2.resize(raw_im, dim, interpolation = cv2.INTER_AREA)
            else:
                out_im=raw_im
            images.append(out_im)
            labels.append(int(label))
            #print(out_im.shape)
        id += 1
        
#++++++++++++++++++++++++++++++
        
(width, height) = dim

# Create a Numpy array from the two lists above
(images, labels) = [numpy.array(lis) for lis in [images, labels]]

#Here we create the two models to use fisher/binaryPatternHist
#model = cv2.face.createFisherFaceRecognizer(5,600)
model = cv2.face.createLBPHFaceRecognizer(2,5,6,6,11)#3,6,8,8,15)
model.train(images, labels)

# Using cascade files to detect faces and eyes* (*OJAG)
face_cascade = cv2.CascadeClassifier(haar_face)
eyes_cascade = cv2.CascadeClassifier(haar_eyes)

# Camera capture
webcam = cv2.VideoCapture(0)

fps = webcam.get(cv2.CAP_PROP_FPS)

rslt_array=[]

# Using fisher/bph Recognizers on live camera feed* (*OJAG) 
while True:
    (ret, im) = webcam.read()
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:        
        cv2.rectangle(im,(x,y),(x+w,y+h),(150,150,0),4)
        faceG = gray[y:y + h, x:x + w]
        faceC = im[y:y+h, x:x+w]
        face_resize = cv2.resize(faceG, (width, height))
        eyes = eyes_cascade.detectMultiScale(faceG)
        for (eyeX,eyeY,eyeW,eyeH) in eyes:
            cv2.rectangle(faceC,(eyeX,eyeY),(eyeX+eyeW,eyeY+eyeH),(0,255,0),2)
            result = cv2.face.MinDistancePredictCollector()        
        
        #TThis part runs the recognition step* (*OJAG) 
            prediction = model.predict(face_resize, result, 0)
            recog = result.getLabel()
            conf = result.getDist() 
    #        
#            if conf < 120: *bph best performance (*OJAG) 
            if conf < 55:#120: 
                cv2.rectangle(im, (x, y), (x + w, y + h), (0,255,width), 2)
                
                cv2.rectangle(im, (x, y + h - 20), 
                              (x + w, y + h), 
                              (0,255,0), 
                              cv2.FILLED)
                cv2.putText(im,('%s \n distance: %.2f') % (names[recog],conf), 
                            (x+6, y+h-6), cv2.FONT_HERSHEY_DUPLEX,1,(0, 0, 15),2)
                rslt_array.append(names[recog])
                
               # print('the person is %s'%names[recog])               
            else:
                cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.rectangle(im, (x, y + h - 20), 
                              (x + w, y + h), 
                              (0, 0, 255), 
                              cv2.FILLED)
                cv2.putText(im,'I cannot recognize you \n distance: %.2f'% (conf),
                            (x+6, y+h-6), cv2.FONT_HERSHEY_PLAIN,1,(255, 255, 255),1)

    cv2.imshow('Facial Recognition', im)
    cv2.waitKey(1)
    interval =time.time() - t_0
    if interval >= 15: #time in seconds
        break
    
#    # Hit 'q' on the keyboard to quit!
#    if cv2.waitKey(1) & 0xFF == ord('q'):
#        break
    
  
    
    
    
webcam.release()
cv2.destroyAllWindows()

if len(sys.argv) > 1:
    subject = sys.argv[1]
    a =rslt_array.count(subject)/len(rslt_array)*100
    #print(rslt_array)
    print(" #########  overall percentage of hits: %.2f%%   #########      "%a)
    print(' the capture speed of the camera is: %.2f'%fps)
          




