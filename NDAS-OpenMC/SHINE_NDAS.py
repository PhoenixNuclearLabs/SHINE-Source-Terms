#!/usr/bin/python3

import numpy as np
import openmc

import sys
sys.dont_write_bytecode = True
from SHINE_NDAS_source import get_source

def get_materials():

    xslib = 'endfb-viii.0-hdf5'
    openmc.Materials.cross_sections = '/home/lucas/openmc_data/%s/cross_sections.xml' % (xslib)

    mat_dict = {}

    mat_dict['Cu'] = openmc.Material(112, 'Copper')
    mat_dict['Cu'].add_element('Cu', 1.0, 'ao')
    mat_dict['Cu'].set_density('g/cm3', 8.96)

    mat_dict['SS304'] = openmc.Material(331, 'Steel, Stainless 304')
    mat_dict['SS304'].add_element('C' , 0.00080, 'wo')
    mat_dict['SS304'].add_element('Si', 0.01000, 'wo')
    mat_dict['SS304'].add_element('P' , 0.00045, 'wo')
    mat_dict['SS304'].add_element('S' , 0.00030, 'wo')
    mat_dict['SS304'].add_element('Cr', 0.19000, 'wo')
    mat_dict['SS304'].add_element('Mn', 0.02000, 'wo')
    mat_dict['SS304'].add_element('Fe', 0.68345, 'wo')
    mat_dict['SS304'].add_element('Ni', 0.09500, 'wo')
    mat_dict['SS304'].set_density('g/cm3', 8.03)

    mat_dict['H2O'] = openmc.Material(392, 'Water, Liquid')
    mat_dict['H2O'].add_element('H', 2.0, 'ao')
    mat_dict['H2O'].add_element('O', 1.0, 'ao')
    mat_dict['H2O'].set_density('g/cm3', 0.997)

    return mat_dict

def get_geometry(mats):

    r_stop   = openmc.ZCylinder(r=3.8100)
    r_vacuum = openmc.ZCylinder(r=4.1783)
    r_wall_1 = openmc.ZCylinder(r=4.4577)
    r_water  = openmc.ZCylinder(r=4.5974)
    r_wall_2 = openmc.ZCylinder(r=4.8260)

    z_stop   = openmc.ZPlane(-68.5)
    z_vacuum = openmc.ZPlane(-68.5 - 0.63500)
    z_wall_1 = openmc.ZPlane(-68.5 - 0.95250)
    z_water  = openmc.ZPlane(-68.5 - 1.18872)
    z_wall_2 = openmc.ZPlane(-68.5 - 3.52552)
    zmax     = openmc.ZPlane( 68.5)

    r_tally  = openmc.ZCylinder(r=5.08)
    z0_tally = openmc.ZPlane(-17.0)
    z1_tally = openmc.ZPlane(-12.0)

    r_bound  = openmc.Sphere(r=1000, boundary_type='vacuum')

    reg_stop   = -r_stop   & +z_vacuum & -z_stop
    reg_vacuum = -r_vacuum & +z_vacuum & -zmax & (+r_stop   | -z_vacuum | +z_stop)
    reg_wall_1 = -r_wall_1 & +z_wall_1 & -zmax & (+r_vacuum | -z_vacuum)
    reg_water  = -r_water  & +z_water  & -zmax & (+r_wall_1 | -z_wall_1)
    reg_wall_2 = -r_wall_2 & +z_wall_2 & -zmax & (+r_water  | -z_water )
    reg_tally  = -r_tally  & +z0_tally & -z1_tally & +r_wall_2
    reg_bound  = -r_bound  & (+r_wall_2 | -z_wall_2 | +zmax) & (+r_tally | -z0_tally | +z1_tally)

    cells = [
        openmc.Cell(name='Beam stop'                , region=reg_stop  , fill=mats['Cu'   ]),
        openmc.Cell(name='Vacuum in target chamber' , region=reg_vacuum, fill=None         ),
        openmc.Cell(name='Target chamber inner wall', region=reg_wall_1, fill=mats['SS304']),
        openmc.Cell(name='Cooling water jacket'     , region=reg_water , fill=mats['H2O'  ]),
        openmc.Cell(name='Target chamber outer wall', region=reg_wall_2, fill=mats['SS304']),
        openmc.Cell(name='Tally cell'               , region=reg_tally , fill=None         ),
        openmc.Cell(name='Bounding cell'            , region=reg_bound , fill=None         ),
    ]

    root_universe = openmc.Universe(cells=cells)
    geometry      = openmc.Geometry(root_universe)

    return geometry

def get_tallies(geom):

    tally_cells        = [x for x in geom.root_universe.cells.values() if x.name.startswith('Tally')]
    cell_filter        = openmc.CellFilter(tally_cells)
    energy_filter      = openmc.EnergyFilter.from_group_structure('CCFE-709')
    cell_tally         = openmc.Tally(name='Cell tally')
    cell_tally.filters = [cell_filter, energy_filter]
    cell_tally.scores  = ['flux']

    r_grid             = np.linspace(   0.0, 100.0, 101)
    z_grid             = np.linspace(-100.0, 100.0, 201)
    mesh               = openmc.CylindricalMesh(r_grid=r_grid, z_grid=z_grid, origin=(0, 0, 0))
    mesh_tally         = openmc.Tally(name='Mesh tally')
    mesh_tally.filters = [openmc.MeshFilter(mesh)]
    mesh_tally.scores  = ['flux']

    tallies = openmc.Tallies([cell_tally, mesh_tally])

    return tallies

def get_plots(geom):

    plot_xy          = openmc.Plot.from_geometry(geom)
    plot_xy.basis    = 'xy'
    plot_xy.origin   = (0, 0, 0)
    plot_xy.width    = (12, 12)
    plot_xy.pixels   = (800, 800)
    plot_xy.color_by = 'material'
    plot_xy.filename = 'geometry_xy.png'

    plot_xz          = openmc.Plot.from_geometry(geom)
    plot_xz.basis    = 'xz'
    plot_xz.origin   = (0, 0, 0)
    plot_xz.width    = (200, 200)
    plot_xz.pixels   = (800, 800)
    plot_xz.color_by = 'material'
    plot_xz.filename = 'geometry_xz.png'

    plots = openmc.Plots([plot_xy, plot_xz])

    return plots

def get_settings(source):

    settings           = openmc.Settings()
    settings.run_mode  = 'fixed source'
    settings.source    = source
    settings.batches   = 10
    settings.particles = int(1e7)

    return settings

def main():

    mat_dict  = get_materials()
    geometry  = get_geometry(mat_dict)
    tallies   = get_tallies(geometry)
    plots     = get_plots(geometry)
    source    = get_source()
    settings  = get_settings(source)

    materials = openmc.Materials(mat_dict.values())

    materials.export_to_xml()
    geometry .export_to_xml()
    tallies  .export_to_xml()
    plots    .export_to_xml()
    settings .export_to_xml()

    openmc.plot_geometry()

    openmc.run()

if __name__ == '__main__': main()
