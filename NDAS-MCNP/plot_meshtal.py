#!/usr/bin/python3

import numpy as np
import mcnptools

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib import colors as mcolors
from matplotlib import ticker as mticker
from matplotlib import image  as mpimg

def main():

    # Load meshtal file
    meshtal = mcnptools.Meshtal('meshtal')

    # Get mesh tally data
    tally  = meshtal.GetTally(24)
    r_grid = np.array(tally.GetXRBounds())
    z_grid = np.array(tally.GetYZBounds()) - 100
    extent = [-r_grid[-1], r_grid[-1], z_grid[0], z_grid[-1]]
    res    = np.zeros((len(z_grid) - 1, len(r_grid) - 1))
    for i in range(len(z_grid) - 1):
        for j in range(len(r_grid) - 1):
            res[i, j] = tally.GetValue(j, i, 0, 0, 0)

    # Mirror across the x-axis
    res = np.concatenate((np.flip(res, 1), res), 1)

    # Get geometry outline
    img     = mpimg.imread('../NDAS-OpenMC/geometry_xz.png')
    RGB     = np.array(img * 255, dtype=int)
    img_val = RGB[:, :, 0] * 65536 + RGB[:, :, 1] * 256 + RGB[:, :, 2]

    # Plot mesh tally
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(9, 7.25)
    im = ax.imshow(res, origin='lower', extent=extent, norm=mcolors.LogNorm(vmin=1e8, vmax=1e11), cmap='Spectral_r')
    ax.contour(img_val, origin='upper', levels=np.unique(img_val),
               extent=extent, colors='k', linestyles='solid', linewidths=1)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(base=20))
    ax.yaxis.set_major_locator(mticker.MultipleLocator(base=20))
    ax.set_xlabel('x position [cm]')
    ax.set_ylabel('z position [cm]')
    ax.set_title('Neutron flux map - MCNP')
    cbar = plt.colorbar(im, orientation='vertical')
    cbar.set_label('Neutron flux [n/$cm^2$-s]')
    plt.tight_layout()
    fname = 'mesh_tally.png'
    print('Writing %s' % (fname))
    plt.savefig(fname)
    plt.close()

if __name__ == '__main__': main()
