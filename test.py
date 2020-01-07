import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.preprocessing import MinMaxScaler, StandardScaler

X = np.random.normal([0,0], 1, (1000, 2))  # 1000 2-D points, normally distributed
Y = np.random.uniform([0,0], 1, (1000, 2))
Z = np.random.uniform([0,0], 0.1, (1000, 2))
scaler = MinMaxScaler()
X = scaler.fit_transform(X)  # fit to default uniform dist range 0-1
Y = scaler.fit_transform(Y)
plt.scatter(X[:,0], X[:, 1])
plt.scatter(Y[:,0], Y[:, 1])
plt.scatter(Z[:,0], Z[:, 1])
print("normal:")
print(stats.kstest(X[:,0], 'uniform'))
print(stats.kstest(X[:, 1], 'uniform'))
print("uniform:")
print(stats.kstest(Y[:,0], 'uniform'))
print(stats.kstest(Y[:, 1], 'uniform'))
print("zoomed:")
print(stats.kstest(Z[:,0], 'uniform'))
print(stats.kstest(Z[:, 1], 'uniform'))
plt.show()


45.442127, 12.335939
45.442112, 12.335949
