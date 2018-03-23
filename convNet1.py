### primera red convolucional de prueba basada en el sitio web edureka ###
import cv2
import numpy as np
import os
from random import shuffle
from tqdm import tqdm
import tensorflow as tf
import matplotlib.pyplot as plt
import tflearn
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression

TRAIN_DIR = 'ConvNetImages/train/'
TEST_DIR =  'ConvNetImages/test/'
LR = 1e-3
MODEL_NAME = 'classif_PerrosYgatos'
IMG_SIZE = 50

#
def create_label(image_name):
    "One-hot encoded vector de los nombres de cada imagen"
    word_label = image_name.split('.')[-3]
    if word_label ==  'cat':
        return np.array([1,0])
    elif word_label =='dog':
        return np.array([0,1])
    
    
    
    
def create_training_set():
    training_data = []
    for img in tqdm(os.listdir(TRAIN_DIR)):
        path2file = os.path.join(TRAIN_DIR,img)
        img_data = cv2.imread(path2file,cv2.IMREAD_GRAYSCALE)
        img_data = cv2.resize(img_data,(IMG_SIZE, IMG_SIZE))
        training_data.append([np.array(img_data), create_label(img)])
    shuffle(training_data)
    np.save('train_data.npy',training_data)
    return training_data
    

def create_test_set():
    test_data = []
    for img in tqdm(os.listdir(TEST_DIR)):
        path2file = os.path.join(TEST_DIR,img)
        img_num = img.split('.')[0]
        img_data = cv2.imread(path2file,cv2.IMREAD_GRAYSCALE)
        img_data = cv2.resize(img_data,(IMG_SIZE,IMG_SIZE))
        test_data.append([np.array(img_data),img_num])
    shuffle(test_data)
    np.save('test_data.npy', test_data)
    return test_data


###  To create the training and testing datasets
    
#training_set = create_training_set()
#testing_set = create_test_set()

# Para cargar los datos de entremanmiento y de prueba
training_set = np.load('train_data.npy')
testing_set = np.load('test_data.npy')
train = training_set[:-500]
test = training_set[-500:]

x_train = np.array([i[0] for i in train]).reshape(-1, IMG_SIZE, IMG_SIZE, 1)
y_train = [i[1] for i in train]
x_test = np.array([i[0] for i in test]).reshape(-1, IMG_SIZE, IMG_SIZE, 1)
y_test = [i[1] for i in test]

#The Model
tf.reset_default_graph()
convnet = input_data(shape=[None,IMG_SIZE, IMG_SIZE,1], name='input')
convnet = conv_2d(convnet,32,5,activation='relu')
convnet = max_pool_2d(convnet,5)

convnet = conv_2d(convnet,64,5,activation='relu')
convnet = max_pool_2d(convnet,5)

convnet = conv_2d(convnet,128,5,activation='relu')
convnet = max_pool_2d(convnet,5)

convnet = conv_2d(convnet,64,5,activation='relu')
convnet = max_pool_2d(convnet,5)

convnet = conv_2d(convnet,32,5,activation='relu')
convnet = max_pool_2d(convnet,5)

convnet = fully_connected(convnet,1024,activation='relu')
convnet = dropout(convnet,0.8)

convnet = fully_connected(convnet,2,activation='softmax')
convnet = regression(convnet, optimizer='adam', learning_rate=LR, 
                     loss= 'categorical_crossentropy', name='targets')

model = tflearn.DNN(convnet,tensorboard_dir='log',tensorboard_verbose=0)
model.fit({'input':x_train},{'targets':y_train}, n_epoch=10,
          validation_set=({'input':x_test},{'targets': y_test}),
                          snapshot_step=500, show_metric=True, run_id=MODEL_NAME)

fig = plt.figure(figsize=(16,12))

for num, data in enumerate(testing_set[:16]):
    img_num = data[1]
    img_data = data[0]
    
    y=fig.add_subplot(4, 4, num + 1)
    orig = img_data
    data = img_data.reshape(IMG_SIZE,IMG_SIZE,1)
    model_out  =  model.predict([data])[0]
    
    
    if np.argmax(model_out) == 1:
        str_label = 'Dog'
    else:
        str_label = 'Cat'
                               
    y.imshow(orig,cmap='gray')
    plt.title(str_label)
    y.axes.get_xaxis().set_visible(False)
    y.axes.get_yaxis().set_visible(False)
plt.show()

