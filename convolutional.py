# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Simple, end-to-end, LeNet-5-like convolutional MNIST model example.

This should achieve a test error of 0.7%. Please keep this model as simple and
linear as possible, it is meant as a tutorial for simple convolutional models.
Run with --self_test on the command line to execute a short self-test.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import time
import numpy as np
import tensorflow as tf

import data_reader
from six.moves import xrange
from sklearn.model_selection import train_test_split
from at_imagecompairision import tf_ssim, tf_ms_ssim

IMAGE_WIDTH = 64
IMAGE_HEIGHT = 96
NUM_CHANNELS = 1
PIXEL_DEPTH = 255

VALIDATION_SIZE = 50  # Size of the validation set.
SEED = 66478  # Set to None for random seed.
BATCH_SIZE = 64
NUM_EPOCHS = 10
EVAL_BATCH_SIZE = 64
EVAL_FREQUENCY = 1  # Number of steps between evaluations.


def error_rate(predictions, labels):
    result = 0

    print(predictions)
    print(labels)
    exit(1)
    for p, l in zip(predictions, labels):
        result += tf_ssim(p, l)

    return result / len(predictions)


# def make_kernel(a):
#     """Transform a 2D array into a convolution kernel"""
#     a = np.asarray(a)
#     a = a.reshape(list(a.shape) + [1, 1])
#     return tf.constant(a, dtype=1)
#
#
# laplace_k = make_kernel([[0.5, 1.0, 0.5],
#                          [1.0, -6., 1.0],
#                          [0.5, 1.0, 0.5]])
#
#
# def simple_conv(x, k):
#     """A simplified 2D convolution operation"""
#     # x = tf.expand_dims(tf.expand_dims(x, 0), -1)
#     y = tf.nn.depthwise_conv2d(x, k, [1, 1, 1, 1], padding='SAME')
#     # return y[0, :, :, 0]
#     return y
#
#
# def laplace(x):
#     """Compute the 2D laplacian of an array"""
#     return simple_conv(x, laplace_k)
#
#
# def gradient_importance(y_true, y_pred, dtype=tf.float32):
#     importance = tf.abs(laplace(y_true))
#     return K.mean(tf.mul(tf.abs(y_pred - y_true), tf.log(2 + importance)), axis=-1)


def at_generate_weights(inputs, outputs):
    return tf.Variable(
        tf.truncated_normal([3, 3, inputs, outputs], stddev=0.1, seed=SEED, dtype=np.float32)
    )


def at_generate_biases(channels):
    return tf.Variable(tf.zeros([channels], dtype=np.float32))


def main(_):
    # Model Definition
    def model(data):
        """The Model definition."""
        # TODO we need to apply all activation function from the keras solution
        x = tf.nn.conv2d(
            data,
            conv1_weights,
            strides=[1, 1, 1, 1],
            padding='SAME'
        )

        x = tf.nn.max_pool(
            tf.nn.relu(tf.nn.bias_add(x, conv1_biases)),
            ksize=[1, 2, 2, 1],
            strides=[1, 2, 2, 1],
            padding='SAME'
        )

        x = tf.nn.conv2d(
            x,
            conv2_weights,
            strides=[1, 1, 1, 1],
            padding='SAME'
        )

        x = tf.nn.max_pool(
            tf.nn.relu(tf.nn.bias_add(x, conv2_biases)),
            ksize=[1, 2, 2, 1],
            strides=[1, 2, 2, 1],
            padding='SAME'
        )

        x = tf.nn.conv2d(
            x,
            conv3_weights,
            strides=[1, 1, 1, 1],
            padding='SAME'
        )

        x = tf.nn.conv2d(
            x,
            conv4_weights,
            strides=[1, 1, 1, 1],
            padding='SAME'
        )

        x = tf.nn.conv2d_transpose(
            x,
            conv5_weights,
            output_shape=[64, 32, 48, 512],
            strides=[1, 2, 2, 1],
            padding='SAME',
            name='foo'
        )

        x = tf.nn.conv2d(
            x,
            conv6_weights,
            strides=[1, 1, 1, 1],
            padding='SAME'
        )

        x = tf.nn.conv2d_transpose(
            x,
            conv7_weights,
            output_shape=[64, 64, 96, 256],
            strides=[1, 2, 2, 1],
            padding='SAME',
            name='bar'
        )

        x = tf.nn.conv2d(
            x,
            conv8_weights,
            strides=[1, 1, 1, 1],
            padding='SAME'
        )

        return x

    # Extract data into np arrays.
    X, y = data_reader.read_images_from_directory()

    train_data, test_data, train_labels, test_labels = train_test_split(X, y, test_size=0.2)

    # train_data = np.subtract(np.divide(np.array(train_data), 255), 0.5)
    # test_data = np.subtract(np.divide(np.array(test_data), 255), 0.5)
    # train_labels = np.subtract(np.divide(np.array(train_labels), 255), 0.5)
    # test_labels = np.subtract(np.divide(np.array(test_labels), 255), 0.5)
    train_data = np.array(train_data)
    test_data = np.array(test_data)
    train_labels = np.array(train_labels)
    test_labels = np.array(test_labels)
    validation_data = train_data[:VALIDATION_SIZE, ...]
    validation_labels = train_labels[:VALIDATION_SIZE]
    train_data = train_data[VALIDATION_SIZE:, ...]
    train_labels = train_labels[VALIDATION_SIZE:]

    num_epochs = NUM_EPOCHS

    train_size = train_labels.shape[0]

    # This is where training samples and labels are fed to the graph.
    # These placeholder nodes will be fed a batch of training data at each
    # training step using the {feed_dict} argument to the Run() call below.
    train_data_node = tf.placeholder(
        np.float32,
        shape=(BATCH_SIZE, IMAGE_WIDTH, IMAGE_HEIGHT, NUM_CHANNELS)
    )

    train_labels_node = tf.placeholder(tf.float32, shape=(BATCH_SIZE, IMAGE_WIDTH, IMAGE_HEIGHT, NUM_CHANNELS))

    eval_data = tf.placeholder(np.float32, shape=(EVAL_BATCH_SIZE, IMAGE_WIDTH, IMAGE_HEIGHT, NUM_CHANNELS))

    # The variables below hold all the trainable weights. They are passed an
    # initial value which will be assigned when we call:
    # {tf.global_variables_initializer().run()}
    conv1_weights = at_generate_weights(NUM_CHANNELS, 256)
    conv1_biases = at_generate_biases(256)
    conv2_weights = at_generate_weights(256, 256)
    conv2_biases = at_generate_biases(256)
    conv3_weights = at_generate_weights(256, 512)
    conv4_weights = at_generate_weights(512, 512)
    conv5_weights = at_generate_weights(512, 512)
    conv6_weights = at_generate_weights(512, 512)
    conv7_weights = at_generate_weights(256, 512)
    conv8_weights = at_generate_weights(256, 1)

    # Training computation: logits + cross-entropy loss.
    logits = model(train_data_node)

    # loss = tf.reduce_sum(tf.square(train_labels_node - logits), [1, 2, 3])
    # loss = tf.reduce_sum(tf_ssim(train_labels_node, logits))
    loss = tf_ssim(train_labels_node, logits)

    batch = tf.Variable(0, dtype=np.float32)

    # Decay once per epoch, using an exponential schedule starting at 0.01.
    learning_rate = tf.train.exponential_decay(
        0.01,  # Base learning rate.
        batch * BATCH_SIZE,  # Current index into the dataset.
        train_size,  # Decay step.
        0.95,  # Decay rate.
        staircase=True)

    optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss,
                                                         global_step=batch)

    # Predictions for the current training minibatch.
    train_prediction = tf.nn.softmax(logits)

    # Predictions for the test and validation, which we'll compute less often.
    eval_prediction = tf.nn.softmax(model(eval_data))

    # Small utility function to evaluate a dataset by feeding batches of data to
    # {eval_data} and pulling the results from {eval_predictions}.
    # Saves memory and enables this to run on smaller GPUs.
    def eval_in_batches(data, sess):
        """Get all predictions for a dataset by running it in small batches."""
        size = data.shape[0]
        if size < EVAL_BATCH_SIZE:
            raise ValueError("batch size for evals larger than dataset: %d" % size)
        predictions = np.ndarray(shape=(size, 64, 96, 1), dtype=np.float32)
        for begin in xrange(0, size, EVAL_BATCH_SIZE):
            end = begin + EVAL_BATCH_SIZE
            if end <= size:
                predictions[begin:end, :] = sess.run(
                    eval_prediction,
                    feed_dict={eval_data: data[begin:end, ...]})
            else:
                batch_predictions = sess.run(
                    eval_prediction,
                    feed_dict={eval_data: data[-EVAL_BATCH_SIZE:, ...]})
                predictions[begin:, :] = batch_predictions[begin - size:, :]
        return predictions

    # Create a local session to run the training.
    start_time = time.time()
    with tf.Session() as sess:
        # Run all the initializers to prepare the trainable parameters.
        tf.global_variables_initializer().run()

        print('Initialized!')
        # Loop through training steps.
        # print(xrange(int(num_epochs * train_size) // BATCH_SIZE))
        # exit(1)
        for step in xrange(int(num_epochs * train_size) // BATCH_SIZE):
            # Compute the offset of the current minibatch in the data.
            # Note that we could use better randomization across epochs.
            offset = (step * BATCH_SIZE) % (train_size - BATCH_SIZE)
            batch_data = train_data[offset:(offset + BATCH_SIZE), ...]
            batch_labels = train_labels[offset:(offset + BATCH_SIZE)]
            # This dictionary maps the batch data (as a np array) to the
            # node in the graph it should be fed to.
            feed_dict = {train_data_node: batch_data,
                         train_labels_node: batch_labels}
            # Run the optimizer to update weights.
            sess.run(optimizer, feed_dict=feed_dict)

            # print some extra information once reach the evaluation frequency
            if True or step % EVAL_FREQUENCY == 0:
                # fetch some extra nodes' data
                print(loss)
                print(learning_rate)
                print(train_prediction)
                l, lr, predictions = sess.run([loss, learning_rate, train_prediction],
                                              feed_dict=feed_dict)
                print('###########')
                print(l)
                print(np.mean(l))
                print(lr)
                print(predictions)
                elapsed_time = time.time() - start_time
                start_time = time.time()
                print('Step %d (epoch %.2f), %.1f ms' %
                      (step, float(step) * BATCH_SIZE / train_size,
                       1000 * elapsed_time / EVAL_FREQUENCY))
                print('Minibatch loss: %.3f, learning rate: %.6f' % (np.mean(l), lr))
                print('Minibatch error: %.1f%%' % error_rate(predictions, batch_labels))
                print('Validation error: %.1f%%' % error_rate(
                    eval_in_batches(validation_data, sess), validation_labels))
                sys.stdout.flush()
        # Finally print the result!
        test_error = error_rate(eval_in_batches(test_data, sess), test_labels)
        print('Test error: %.1f%%' % test_error)
        # if FLAGS.self_test:
        #     print('test_error', test_error)
        #     assert test_error == 0.0, 'expected 0.0 test_error, got %.2f' % (
        #         test_error,)


if __name__ == '__main__':
    tf.app.run(main=main)
