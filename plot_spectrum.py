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

def load_mcnp():

    # Load mctal file
    fname = os.path.join('NDAS-MCNP', 'mctal')
    print('Reading %s' % (fname))
    mctal = mcnptools.Mctal(fname)

    # Get cell tally data
    tally = mctal.GetTally(14)
    ebins = np.array(tally.GetEBins())
    flux  = np.array([tally.GetValue(0, 0, 0, 0, 0, 0, i, 0, 0)
                      for i in range(1, len(ebins))])

    # Normalize by energy bin width
    log_widths = np.log10(ebins[1:] / ebins[:-1])
    flux      /= log_widths

    return ebins, flux

def load_openmc():

    # Load statepoint
    fname = os.path.join('NDAS-OpenMC', 'statepoint.10.h5')
    print('Reading %s' % (fname))
    sp    = openmc.StatePoint(fname)
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

    return ebins, flux

def main():

    ebins_m, flux_m = load_mcnp()
    ebins_o, flux_o = load_openmc()

    xvals_m = np.append(ebins_m, ebins_m[-1])
    xvals_o = np.append(ebins_o, ebins_o[-1])
    yvals_m = np.append(0, np.append(flux_m, 0))
    yvals_o = np.append(0, np.append(flux_o, 0))

    # Plot energy spectrum
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8, 6)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.step(xvals_m, yvals_m, label='MCNP'  )
    ax.step(xvals_o, yvals_o, label='OpenMC')
    ax.set_xlim(1e-11, 1e+02)
    ax.set_ylim(1e+04, 1e+12)
    ax.xaxis.set_major_locator(mticker.LogLocator(base=10, numticks=20))
    ax.yaxis.set_major_locator(mticker.LogLocator(base=10, numticks=20))
    ax.set_xlabel('Neutron energy [MeV]')
    ax.set_ylabel(r'Neutron flux [n/$\mathregular{cm^2}$-s-lethargy]')
    ax.set_title('Neutron energy spectrum from bare SHINE NDAS')
    ax.legend()
    ax.grid()
    plt.tight_layout()
    fname = 'energy_spectrum.png'
    print('Writing %s' % (fname))
    plt.savefig(fname)
    plt.close()

if __name__ == '__main__': main()
