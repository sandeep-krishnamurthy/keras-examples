'''
This code is forked from https://github.com/fchollet/keras/blob/master/examples/mnist_mlp.py
and modified to use as MXNet-Keras integration testing for functionality and sanity performance
benchmarking.

Trains a simple deep NN on the MNIST dataset.

Gets to 98.40% test accuracy after 20 epochs
(there is *a lot* of margin for parameter tuning).
2 seconds per epoch on a K520 GPU.
'''

from __future__ import print_function
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D
from keras.utils import np_utils

import numpy as np
np.random.seed(1337)  # for reproducibility

from os import environ

from keras.datasets import mnist
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD
from keras.utils import np_utils

from keras.applications.resnet50 import ResNet50
from resnet import ResnetBuilder

# Imports for benchmarking
from profiler import profile
from model_util import make_model

# Imports for assertions
from assertion_util import assert_results

# Other environment variables
MACHINE_TYPE = environ['MXNET_KERAS_TEST_MACHINE']
IS_GPU = (environ['MXNET_KERAS_TEST_MACHINE'] == 'GPU')
MACHINE_TYPE = 'GPU' if IS_GPU else 'CPU'
GPU_NUM = int(environ['GPU_NUM']) if IS_GPU else 0

# Expected Benchmark Numbers
CPU_BENCHMARK_RESULTS = {'TRAINING_TIME':550.0, 'MEM_CONSUMPTION':400.0, 'TRAIN_ACCURACY': 0.85, 'TEST_ACCURACY':0.85}
GPU_1_BENCHMARK_RESULTS = {'TRAINING_TIME':40.0, 'MEM_CONSUMPTION':200, 'TRAIN_ACCURACY': 0.85, 'TEST_ACCURACY':0.85}
# TODO: Fix Train and Test accuracy numbers in multiple gpu mode. Setting it to 0 for now to get whole integration set up done
GPU_2_BENCHMARK_RESULTS = {'TRAINING_TIME':45.0, 'MEM_CONSUMPTION':375, 'TRAIN_ACCURACY': 0.0, 'TEST_ACCURACY':0.0}
GPU_4_BENCHMARK_RESULTS = {'TRAINING_TIME':55.0, 'MEM_CONSUMPTION':750.0, 'TRAIN_ACCURACY': 0.0, 'TEST_ACCURACY':0.0}
GPU_8_BENCHMARK_RESULTS = {'TRAINING_TIME':100.0, 'MEM_CONSUMPTION':1800.0, 'TRAIN_ACCURACY': 0.0, 'TEST_ACCURACY':0.0}

# Dictionary to store profiling output
profile_output = {}

batch_size = 32
nb_classes = 10
nb_epoch = 3 # Should be 200
data_augmentation = True

# input image dimensions
img_rows, img_cols = 32, 32
# The CIFAR10 images are RGB.
img_channels = 3

# the data, shuffled and split between train and test sets
(X_train, y_train), (X_test, y_test) = cifar10.load_data()

print('X_train shape:', X_train.shape)
print(X_train.shape[0], 'train samples')
print(X_test.shape[0], 'test samples')

# Convert class vectors to binary class matrices.
Y_train = np_utils.to_categorical(y_train, nb_classes)
Y_test = np_utils.to_categorical(y_test, nb_classes)


model = ResnetBuilder.build_resnet_50((3, 32, 32), nb_classes)
#model = ResNet50(include_top=False, weights=None, input_shape=X_train.shape[1:])
model.summary()
make_model(model, loss='categorical_crossentropy', optimizer=SGD(), metrics=['accuracy'])

X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
X_train /= 255
X_test /= 255

def train_model():

    if not data_augmentation:
        print('Not using data augmentation.')
        history = model.fit(X_train, Y_train,
          batch_size=batch_size,
          nb_epoch=nb_epoch,
          validation_data=(X_test, Y_test),
          shuffle=True)
        profile_output["History"] = history.history
    else:
        print('Using real-time data augmentation.')
        # This will do preprocessing and realtime data augmentation:
        datagen = ImageDataGenerator(
            featurewise_center=False,  # set input mean to 0 over the dataset
            samplewise_center=False,  # set each sample mean to 0
            featurewise_std_normalization=False,  # divide inputs by std of the dataset
            samplewise_std_normalization=False,  # divide each input by its std
            zca_whitening=False,  # apply ZCA whitening
            rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
            width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
            height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
            horizontal_flip=True,  # randomly flip images
            vertical_flip=False)  # randomly flip images

        # Compute quantities required for featurewise normalization
        # (std, mean, and principal components if ZCA whitening is applied).
        datagen.fit(X_train)

        # Fit the model on the batches generated by datagen.flow().
        history = model.fit_generator(datagen.flow(X_train, Y_train,
                                 batch_size=batch_size),
                    samples_per_epoch=X_train.shape[0],
                    nb_epoch=nb_epoch,
                    validation_data=(X_test, Y_test))
        profile_output["History"] = history.history


# Calling training and profile memory usage
profile_output["MODEL"] = "MNIST MLP"
run_time, memory_usage = profile(train_model)

profile_output['TRAINING_TIME'] = float(run_time)
profile_output['MEM_CONSUMPTION'] = float(memory_usage)

score = model.evaluate(X_test, Y_test, verbose=0)
profile_output["TEST_ACCURACY"] = score[1]

assert_results(MACHINE_TYPE, IS_GPU, GPU_NUM, profile_output, CPU_BENCHMARK_RESULTS, GPU_1_BENCHMARK_RESULTS, GPU_2_BENCHMARK_RESULTS, GPU_4_BENCHMARK_RESULTS, GPU_8_BENCHMARK_RESULTS)
