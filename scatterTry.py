from matplotlib.pylab import *
import numpy as np
n = 1024
x = np.random.normal(0,1,n)
y = np.random.normal(0,1,n)
for ii in range(n):
    if ii%2==1:
        scatter(x[ii],y[ii],c='y')
    else:
        scatter(x[ii], y[ii], c='g')
show()