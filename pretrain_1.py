# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 11:50:26 2020

@author: Neha Dadarwala
"""


#!/usr/local/bin/python

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import pickle
# from matplotlib.backends.backend_pdf import PdfPages


################    Data Loading and Plotting    ########################
def dense_to_one_hot(labels_dense, num_classes=10):
    """Convert class labels from scalars to one-hot vectors."""
    num_labels = labels_dense.shape[0]
    index_offset = np.arange(num_labels) * num_classes
    labels_one_hot = np.zeros((num_labels, num_classes))
    labels_one_hot.flat[index_offset + labels_dense.ravel()] = 1
    return labels_one_hot

path = "trainset/"
n_classes = 56 # Number of classes in that data

print("Loading Data ... %s % (path)")
train = np.loadtxt(path + 'train_melfilter48.dat')
print("loaded")
# test = np.loadtxt(path + 'test.dat')
# plot = np.loadtxt(path + 'testing.dat')
train_X = np.copy(train[:,:-1]) # Access all but the last column
train_labels_dense = np.copy(train[:,-1:]) # Access only the last column
train_labels_dense = train_labels_dense.astype(int)

train_y = dense_to_one_hot(train_labels_dense, num_classes = n_classes)

#change
# test_X = np.copy(test[:,:-1])
# test_labels_dense = np.copy(test[:,-1:]) # Access only the last column
# test_labels_dense = test_labels_dense.astype(int)
# test_y = dense_to_one_hot(test_labels_dense, num_classes = n_classes)


# print train_labels_dense
# plot_data(train_X, train_labels_dense)
# time.sleep(10)
# plt.close('all')
print("Data Loaded and processed ...")

#%%

################## Neural Networks Training #################################

print("Selecting Neural Network Parameters ...")
# Parameters
training_epochs = 200
batch_size = 64
total_batch = int(train_X.shape[0]/batch_size)
display_step = 5
beta = 0.1

#tf.train.exponential_decay(learning_rate, global_step, 10, 0.9, staircase=False, name=None)

#decayed_learning_rate = learning_rate * decay_rate ^ (global_step / 10)

starter_learning_rate = 0.003
global_step = tf.Variable(0, trainable = False)
learning_rate = tf.train.exponential_decay(starter_learning_rate, global_step, 50 * total_batch, 0.9, staircase = True)

# Network Parameters
n_hidden_1 = 512 # 1st layer num features
n_input = 585 # input dimensionality

x = tf.placeholder("float", [None, n_input])
y = tf.placeholder("float", [None, n_classes])


# Create model
def multilayer_perceptron(_X, _weights, _biases):
    #Hidden layer with RELU activation
    layer_1 = tf.nn.dropout(tf.nn.relu(tf.add(tf.matmul(_X, _weights['h1']), _biases['b1'])), 1.0)
    return tf.matmul(layer_1, _weights['out']) + _biases['out']


#He initialiser
#initializer = tf.contrib.layers.variance_scaling_initializer()

weights = {
    'h1': tf.Variable(tf.random_normal([n_input, n_hidden_1])),
    #'h1' : tf.Variable(initializer([n_input, n_hidden_1])),
    'out': tf.Variable(tf.random_normal([n_hidden_1, n_classes]))
}

biases = {
    'b1': tf.Variable(tf.random_normal([n_hidden_1])),
    #'b1' : tf.Variable(initializer([n_hidden_1])),
    'out': tf.Variable(tf.random_normal([n_classes]))
}

# print type(biases['b1'])
# def hidden_activations(_X, _weights, _biases):
# layer_1 = tf.nn.relu(tf.add(tf.matmul(x, weights['h1']), biases['b1']))
# layer_2 = tf.nn.relu(tf.add(tf.matmul(layer_1, weights['h2']), biases['b2']))
    # return layer_1, layer_2


pred = multilayer_perceptron(x, weights, biases)
# act = hidden_activations(x, weights, biases)

# Define loss and optimizer
# Softmax loss
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits = pred, labels=y))

# Loss function with L2 Regularization with decaying learning rate beta
regularizers = tf.nn.l2_loss(weights['h1']) + tf.nn.l2_loss(weights['out']) 
cost = tf.reduce_mean(cost + beta * regularizers)

# Adam Optimizer
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost, global_step = global_step)


# Create a summary to monitor cost function
tf.contrib.deprecated.scalar_summary("loss", cost)

# Merge all summaries to a single operator
merged_summary_op = tf.summary.merge_all()

print("Training the Neural Network")
init = tf.initialize_all_variables()

with tf.Session() as sess:
    sess.run(init)

    # Set logs writer into folder /tmp/tensorflow_logs
    summary_writer = tf.summary.FileWriter('tensorflow_logs', graph_def=sess.graph_def)
    # Training cycle
    avg_cost = 100.
    epoch = 0
    epochs = []
    costs = [] 
    #while avg_cost > 0.001 and epoch < 1000:
    for epoch in range(training_epochs):
        avg_cost = 0.
        # Loop over all batches
        for i in range(total_batch):
            batch_xs, batch_ys = train_X[i*batch_size:(i+1)*batch_size,:], train_y[i*batch_size:(i+1)*batch_size,:]
            # Fit training using batch data
            sess.run(optimizer, feed_dict={x: batch_xs, y: batch_ys})
            # Compute average loss
            avg_cost += sess.run(cost, feed_dict={x: batch_xs, y: batch_ys})/total_batch
            # Write logs at every iteration
            #summary_str = sess.run(merged_summary_op, feed_dict={x: batch_xs, y: batch_ys})
            #summary_writer.add_summary(summary_str, epoch*total_batch + i)

        # Display logs per epoch step
        if epoch % display_step == 0:
            print("Epoch:", '%04d' % (epoch+1), "cost=", "{:.9f}".format(avg_cost), "learning rate= %.4f" % sess.run(learning_rate), "step= %d" % sess.run(global_step))
        epochs.append(epoch)
        costs.append(avg_cost)
        epoch += 1


    print("Optimization Finished!")
    # summary_writer.flush()
    # print "b1 = ", sess.run(biases['b1'])
    # print "b2 = ", sess.run(biases['b2'])
    # print "b3 = ", sess.run(biases['out'])
    # Test model
    #correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
    # #Calculate accuracy
    #accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
    #print("Accuracy:", accuracy.eval(feed_dict={x: test_X, y: test_y}))
    # dense = tf.argmax(pred, 1)
    # #     label = np.zeros((test_y.shape[0], 1))
    # label = np.asarray(dense.eval(feed_dict={x: test_X}))
    # # print label
    # hidden1 = np.asarray(layer_1.eval(feed_dict={x: test_X}))
    # hidden2 = np.asarray(layer_2.eval(feed_dict={x: test_X}))
    # Y = np.asarray(dense.eval({x: plot}))
    W = {
    'h1': sess.run(weights['h1']),
    # 'h2': sess.run(weights['h2']),
    # 'h3': sess.run(weights['h3']),
    'out': sess.run(weights['out'])
    }

    b = {
    'b1': sess.run(biases['b1']),
    # 'b2': sess.run(biases['b2']),
    # 'b3': sess.run(biases['b3']),
    'out': sess.run(biases['out'])
    }

    # print "b1 = ", b['b1']
    # print "b2 = ", b['b2']
    # print "b3 = ", b['out']

    file_ID = path + "parameters_mfcc_1.pkl"
    f = open(file_ID, "wb")
    pickle.dump(W, f, protocol=pickle.HIGHEST_PROTOCOL)
    pickle.dump(b, f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close()
    
#%%
    
#print(epochs)   
a = epochs  
b = costs 
plt.plot(a, b) 
plt.xlabel('Epochs') 
plt.ylabel('Cost') 
plt.title('Cost vs epochs') 
plt.show()