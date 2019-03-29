import numpy.matlib
import numpy as np
"""
# sigmoid function


def nonlin(x, deriv=False):
    if(deriv == True):
        return x * (1 - x)
    return 1 / (1 + np.exp(-x))

# input dataset
X = np.array([[0, 0, 1],
              [0, 1, 1],
              [1, 0, 1],
              [1, 1, 1]])

# output dataset
y = np.array([[0, 0, 1, 1]]).T

# seed random numbers to make calculation
# deterministic (just a good practice)
np.random.seed(1)

# initialize weights randomly with mean 0
syn0 = 2 * np.random.random((3, 1)) - 1

for iter in range(10000):
    # forward propagation
    l0 = X
    l1 = nonlin(np.dot(l0, syn0))

    # how much did we miss?
    l1_error = y - l1

    # multiply how much we missed by the
    # slope of the sigmoid at the values in l1
    l1_delta = l1_error * nonlin(l1, True)

    # update weights
    syn0 += np.dot(l0.T, l1_delta)
print("Output After Training:")
print(l1)

# 章节输入矩阵
Input = np.array([[1, 1, 1, 1]])

# 目标考点分布矩阵
Target = np.array([[0.1, 0.2, 0.5, 0.9]])

np.random.seed(1)

# 当前考点分布矩阵
syn0 = 2 * np.random.random((1, 4)) - 1

for iter in range(1000):
    # 前向传播
    l0 = Input

    l1 = nonlin(l0 * syn0)

    # 计算输入迭代后与目标矩阵的差值
    l1_error = Target - l1

    # nolin计算下降梯度，结果用于计算偏差修正值
    l1_delta = l1_error * nonlin(l1, True)

    # 修正分布矩阵以“强迫”其接近输出
    syn0 += l1_delta

print("Output After Training:")
print(l1)
"""

a = [1, 2, 3, 4, 5]
b = ['1', '2', '3', '4']
print(set(a) & set(b))
