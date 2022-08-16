from mpl_toolkits.mplot3d import Axes3D
from matplotlib import pyplot as plt
import matplotlib
import numpy as np
import matplotlib.cm as cmx





def scatter4d( x, y, z, cs, title,colorsMap='rainbow'): #jet tab20c for discrete range
    cm = plt.get_cmap(colorsMap)
#    cNorm = matplotlib.colors.Normalize(vmin=-1.4, vmax=0.4)
    cNorm = matplotlib.colors.Normalize(vmin=min(cs), vmax=max(cs))
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.scatter(x, y, z, c=scalarMap.to_rgba(cs))
    scalarMap.set_array(cs)
    fig.colorbar(scalarMap,label='Cp') ##DeltaP (daN/m2)
    ax.set_xlabel('x',fontsize=14, fontweight='bold')
    ax.set_ylabel('y',fontsize=14, fontweight='bold')
    ax.set_zlabel('z',fontsize=14, fontweight='bold')
    ax.set_title(title,fontsize=10,fontweight='bold')


    max_range = np.array([max(x)-min(x), max(y)-min(y), max(z)-min(z)]).max() / 2.0
    mid_x = (max(x)+min(x)) * 0.5
    mid_y = (max(y)+min(y)) * 0.5
    mid_z = (max(z)+min(z)) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)