#!/usr/bin/python3

import numpy as np
import openmc

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib import colors as mcolors
from matplotlib import ticker as mticker

def main():

    # Load statepoint
    sp    = openmc.StatePoint('statepoint.10.h5')
    tally = sp.get_tally(name='Cell tally')
    sp.close()

    # Get cell tally data
    ebins = tally.find_filter(openmc.EnergyFilter).values * 1e-6
    flux  = tally.mean[:, 0, 0]

    # Normalize by volume
    volume  = np.pi * (5.08**2 - 4.826**2) * 5.0
    flux   /= volume

    # Normalize by energy bin width
    log_widths = np.log10(ebins[1:] / ebins[:-1])
    flux      /= log_widths

    # Plot energy spectrum
    xvals = np.append(ebins, ebins[-1])
    yvals = np.append(0, np.append(flux, 0))
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8, 6)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.step(xvals, yvals)
    ax.set_xlim(1e-11, 1e2)
    ax.set_ylim(1e4, 1e12)
    ax.xaxis.set_major_locator(mticker.LogLocator(base=10, numticks=20))
    ax.yaxis.set_major_locator(mticker.LogLocator(base=10, numticks=20))
    ax.set_xlabel('Neutron energy [MeV]')
    ax.set_ylabel('Neutron flux [n/$cm^2$-s-lethargy]')
    ax.set_title('Neutron energy spectrum - OpenMC')
    ax.grid()
    plt.tight_layout()
    fname = 'energy_spectrum.png'
    print('Writing %s' % (fname))
    plt.savefig(fname)
    plt.close()

if __name__ == '__main__': main()
