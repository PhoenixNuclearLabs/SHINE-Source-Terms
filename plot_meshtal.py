#!/usr/bin/python3

import os
import numpy as np
import mcnptools
import openmc

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib import colors as mcolors
from matplotlib import ticker as mticker
from matplotlib import image  as mpimg

def load_mcnp():

    # Load meshtal file
    fname   = os.path.join('NDAS-MCNP', 'meshtal')
    print('Reading %s' % (fname))
    meshtal = mcnptools.Meshtal(fname)
    tally   = meshtal.GetTally(24)

    # Get mesh tally data
    r_grid = np.array(tally.GetXRBounds())
    z_grid = np.array(tally.GetYZBounds()) - 100
    extent = [-r_grid[-1], r_grid[-1], z_grid[0], z_grid[-1]]
    res    = np.zeros((len(z_grid) - 1, len(r_grid) - 1))
    for i in range(len(z_grid) - 1):
        for j in range(len(r_grid) - 1):
            res[i, j] = tally.GetValue(j, i, 0, 0, 0)

    # Mirror across the x-axis
    res = np.concatenate((np.flip(res, 1), res), 1)

    return extent, res

def load_openmc():

    # Load statepoint
    fname = os.path.join('NDAS-OpenMC', 'statepoint.10.h5')
    print('Reading %s' % (fname))
    sp    = openmc.StatePoint(fname)
    tally = sp.get_tally(name='Mesh tally')
    sp.close()

    # Get mesh tally data
    slice  = tally.get_slice(scores=['flux'])
    mesh   = tally.find_filter(openmc.MeshFilter).mesh
    extent = [-mesh.r_grid[-1], mesh.r_grid[-1], mesh.z_grid[ 0], mesh.z_grid[-1]]
    slice.mean   .shape = (mesh.dimension[2], mesh.dimension[0])
    slice.std_dev.shape = (mesh.dimension[2], mesh.dimension[0])

    # Normalize by mesh cell volumes
    res = slice.mean / mesh.volumes[:, 0, :].T

    # Mirror across the x-axis
    res = np.concatenate((np.flip(res, 1), res), 1)

    return extent, res

def main():

    extent_m, res_m = load_mcnp()
    extent_o, res_o = load_openmc()

    # Get geometry outline
    fname   = os.path.join('NDAS-OpenMC', 'geometry_xz.png')
    img     = mpimg.imread(fname)
    RGB     = np.array(img * 255, dtype=int)
    outline = RGB[:, :, 0] * 65536 + RGB[:, :, 1] * 256 + RGB[:, :, 2]

    # Plot mesh tally
    for k in range(2):
        if   k == 0: res = res_m; extent = extent_m; label = 'MCNP'
        elif k == 1: res = res_o; extent = extent_o; label = 'OpenMC'
        fig, ax = plt.subplots(1, 1)
        fig.set_size_inches(9, 7.25)
        im = ax.imshow(res, origin='lower', extent=extent, cmap='Spectral_r',
                       norm=mcolors.LogNorm(vmin=1e8, vmax=1e11))
        ax.contour(outline, origin='upper', levels=np.unique(outline),
                   extent=extent, colors='k', linestyles='solid', linewidths=1)
        ax.xaxis.set_major_locator(mticker.MultipleLocator(base=20))
        ax.yaxis.set_major_locator(mticker.MultipleLocator(base=20))
        ax.set_xlabel('x position [cm]')
        ax.set_ylabel('z position [cm]')
        ax.set_title('Neutron flux map for bare SHINE NDAS - %s' % (label))
        cbar = plt.colorbar(im, orientation='vertical')
        cbar.set_label('Neutron flux [n/$cm^2$-s]')
        plt.tight_layout()
        fname = 'flux_map_%s.png' % (label.lower())
        print('Writing %s' % (fname))
        plt.savefig(fname)
        plt.close()

if __name__ == '__main__': main()
