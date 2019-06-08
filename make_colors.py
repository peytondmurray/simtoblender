import numpy as np
import matplotlib.cm as cm
import cmocean

#cmap = cmocean.cm.ice_r
cmap = cm.get_cmap('RdBu_r')
values = np.linspace(0.2, 0.8, 512)
np.savetxt('colors.csv', cmap(values))