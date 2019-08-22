import tensorflow as tf
import numpy as np 

def stack_many(args):
    return tuple([np.stack(arg) for arg in args])

def normalise(x, mean, std):
    return (x-mean)/std

def fold_batch(x):
    rows, cols = x.shape[0], x.shape[1]
    y = x.reshape(rows*cols,*x.shape[2:])
    return y

def unfold_batch(x, length, batch_size):
    return x.reshape(length, batch_size, *x.shape[1:])

@tf.function
def keras_fold_batch(x):
    time, batch = x.shape[0], x.shape[1]
    return tf.keras.backend.reshape(x, shape=(time*batch, *x.shape[2:]) )


def one_hot(x, num_classes):
    return np.eye(num_classes)[x]


class rolling_stats(object):
    def __init__(self,mean=0,n=1,epsilon=1e-4):
        self.mean = mean
        self.n = n
        self.M2 = 0
        self.epsilon = epsilon
    
    def update(self,x):
        self.n +=1
        prev_mean = self.mean
        new_mean = prev_mean + ((x - prev_mean)/self.n)
        self.M2 += (x - new_mean) * (x - prev_mean)
        std = np.sqrt((self.M2 + self.epsilon) / self.n)
        self.mean = new_mean
        return self.mean, std

#https://github.com/openai/baselines/blob/master/baselines/common/running_mean_std.py
class RunningMeanStd(object):
    # https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Parallel_algorithm
    def __init__(self, epsilon=1e-4, shape=()):
        self.mean = np.zeros(shape, 'float64')
        self.var = np.ones(shape, 'float64')
        self.count = epsilon

    def update(self, x):
        batch_mean = np.mean(x, axis=0)
        batch_var = np.var(x, axis=0)
        batch_count = x.shape[0]
        return self.update_from_moments(batch_mean, batch_var, batch_count)

    def update_from_moments(self, batch_mean, batch_var, batch_count):
        delta = batch_mean - self.mean
        tot_count = self.count + batch_count

        new_mean = self.mean + delta * batch_count / tot_count
        m_a = self.var * (self.count)
        m_b = batch_var * (batch_count)
        M2 = m_a + m_b + np.square(delta) * self.count * batch_count / (self.count + batch_count)
        new_var = M2 / (self.count + batch_count)

        new_count = batch_count + self.count

        self.mean = new_mean
        self.var = new_var
        self.count = new_count
        
        return self.mean, np.sqrt(self.var)