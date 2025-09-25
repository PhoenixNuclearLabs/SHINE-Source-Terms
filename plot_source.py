#!/usr/bin/python3

import os
import numpy as np

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib import colors as mcolors
from matplotlib import ticker as mticker

def main():

    fname = os.path.join('NDAS-MCNP', 'SHINE_NDAS_source.txt')
    with open(fname, 'r') as r: text = r.read()

    # Plot vertical (extent) profile
    si1      = text.split(' si1 ')[1].split(' sp1 ')[0].split()
    sp1      = text.split(' sp1 ')[1].split('c'    )[0].split()
    zmin     = float(si1[ 0])
    zmax     = float(si1[-1])
    dist_z_p = np.array([float(x) for x in sp1[1:]])[::-1]
    dist_z_x = np.linspace(0, zmax - zmin, len(dist_z_p) + 1)
    xvals_p  = np.append(0, dist_z_x)
    yvals_p  = np.append(0, np.append(dist_z_p, 0))
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8, 6)
    ax.step(xvals_p, yvals_p)
    ax.set_xlabel('Distance from top of target chamber [cm]')
    ax.set_ylabel('Linear neutron source [n/cm-s]')
    ax.set_title('SHINE NDAS vertical neutron source distribution')
    ax.grid()
    plt.tight_layout()
    fname = os.path.join('images', 'profile_vertical.png')
    print('Writing %s' % (fname))
    plt.savefig(fname)
    plt.close()

    # Plot angular distribution
    si2      = text.split(' si2 ')[1].split(' sp2 ')[0].split()
    sp2      = text.split(' sp2 ')[1].split('c'    )[0].split()
    dist_a_x = np.acos(np.array([float(x) for x in si2[1:]]))[::-1]
    areas    = (np.cos(dist_a_x)[:-1] - np.cos(dist_a_x)[1:]) * 2 * np.pi
    dist_a_p = np.array([float(x) for x in sp2[1:]])[::-1] / areas
    xvals_p  = np.append(dist_a_x, 2 * np.pi - np.flip(dist_a_x[:-1], 0))
    yvals_p  = np.append(dist_a_p, np.flip(dist_a_p))
    yvals_p /= np.mean(yvals_p)
    yvals_p  = np.append(yvals_p, yvals_p[-1])
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='polar')
    fig.set_size_inches(6, 6)
    ax.plot(xvals_p, yvals_p)
    ax.set_rlabel_position(270)
    ax.set_title('SHINE NDAS neutron angular distribution')
    plt.tight_layout()
    fname = os.path.join('images', 'profile_angular.png')
    print('Writing %s' % (fname))
    plt.savefig(fname)
    plt.close()

    # Plot radial distribution
    ds3      = text.split(' si101 ')[1].split('c')[0].split()
    ds3      = [x for x in ds3 if not x.startswith('si') and not x == '0']
    dist_r_x = np.array([float(x) for x in ds3])[::-1]
    xvals_p  = np.append(dist_z_x, dist_z_x[-1])
    yvals_p  = np.append(np.append(0, dist_r_x), 0)
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8, 6)
    ax.step(xvals_p,  yvals_p, label='MCNP')
    plt.gca().set_prop_cycle(None)
    ax.step(xvals_p, -yvals_p)
    ax.plot([0, 137, 137, 0, 0],
            [2.5263, 2.5263, -2.5263, -2.5263, 2.5263], label='OpenMC')
    ax.set_xlabel('Distance from top of target chamber [cm]')
    ax.set_ylabel('Maximum neutron emission radius [cm]')
    ax.set_title('SHINE NDAS radial neutron source distribution')
    ax.grid()
    ax.legend()
    plt.tight_layout()
    fname = os.path.join('images', 'profile_radial.png')
    print('Writing %s' % (fname))
    plt.savefig(fname)
    plt.close()

    # Plot angular-dependent energy distribution
    num_angle = len(dist_a_x) - 1
    spectra = np.zeros((num_angle, 1601))
    for i in range(num_angle):
        si = text.split(' si%u ' % (i + 5))[1].split(' sp%u ' % (i + 5))[0]
        sp = text.split(' sp%u ' % (i + 5))[1].split('c'               )[0]
        e_vals = [float(x) for x in si.split()[1:] if not x.endswith('i')]
        e_inds = [round(x * 100) for x in e_vals]
        e_dist = np.array([float(x) for x in sp.split()])
        spectra[i, e_inds[0]:e_inds[1] + 1] = e_dist[:e_inds[1] - e_inds[0] + 1 ]
        spectra[i, e_inds[2]:e_inds[3] + 1] = e_dist[ e_inds[1] - e_inds[0] + 1:]
        #spectra[i, :] /= areas[i]
    e_vals  = np.linspace(0, (spectra.shape[1] - 1) / 100, spectra.shape[1])
    spectra = np.flip(spectra, 0) * 100
    cvals   = np.linspace(0, 0.95, num_angle)
    colors  = [plt.cm.nipy_spectral(x) for x in cvals]
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8, 6)
    ax.set_prop_cycle('color', colors)
    total = np.zeros(spectra.shape[1])
    for i in range(num_angle):
        if i in [0, 5, 10, 15, 20, 25, 30, 34, 39, 44, 49, 54, 59]:
            label = r'%u-%u$\degree$' % (i * 3, (i + 1) * 3)
        else: label = ''
        ax.fill_between(e_vals, total, total + spectra[i, :], label=label)
        total += spectra[i, :]
    ax.set_xlim(13, 15.4)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(base=0.2))
    ax.set_xlabel('Neutron energy [MeV]')
    ax.set_ylabel('Neutron source [n/MeV-sr-s]')
    ax.set_title('SHINE NDAS angular-dependent neutron energy distribution (MCNP only)')
    ax.grid()
    ax.legend(loc='upper right')
    plt.tight_layout()
    fname = os.path.join('images', 'profile_energy_angle.png')
    print('Writing %s' % (fname))
    plt.savefig(fname)
    ax.set_yscale('log')
    ax.set_xlim(-0.05 * 16, 1.05 * 16)
    ax.set_ylim(1e9, 1e14)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(base=1))
    ax.legend(loc='upper center')
    plt.tight_layout()
    fname = os.path.join('images', 'profile_energy_angle_full.png')
    print('Writing %s' % (fname))
    plt.savefig(fname)
    plt.close()

    # Plot energy distribution
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8, 6)
    ax.plot(e_vals, np.sum(spectra, 0))
    ax.set_xlim(13, 15.4)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(base=0.2))
    ax.set_xlabel('Neutron energy [MeV]')
    ax.set_ylabel('Neutron source [n/MeV-s]')
    ax.set_title('SHINE NDAS neutron energy distribution')
    ax.grid()
    plt.tight_layout()
    fname = os.path.join('images', 'profile_energy.png')
    print('Writing %s' % (fname))
    plt.savefig(fname)
    ax.set_yscale('log')
    ax.set_xlim(-0.05 * 16, 1.05 * 16)
    ax.set_ylim(1e9, 1e14)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(base=1))
    plt.tight_layout()
    fname = os.path.join('images', 'profile_energy_full.png')
    print('Writing %s' % (fname))
    plt.savefig(fname)
    plt.close()

if __name__ == '__main__': main()
