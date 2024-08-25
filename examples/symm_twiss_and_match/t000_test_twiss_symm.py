import xtrack as xt
import xobjects as xo
import numpy as np

# Build line with half a cell
half_cell = xt.Line(
    elements={
        'start_cell': xt.Marker(),
        'drift0': xt.Drift(length=1.),
        'qf1': xt.Quadrupole(k1=0.027/2, length=1.),
        'drift1_1': xt.Drift(length=1),
        'bend1': xt.Bend(k0=3e-4, h=3e-4, length=45.),
        'drift1_2': xt.Drift(length=1.),
        'qd1': xt.Quadrupole(k1=-0.0271/2, length=1.),
        'drift2': xt.Drift(length=1),
        'mid_cell': xt.Marker(),
    }
)
half_cell.particle_ref = xt.Particles(p0c=2e9)

tw_half_cell = half_cell.twiss4d(init='periodic_symmetric', # <--- periodic-symmetric boundary
                                 strengths=True # to get the strengths in table
                                )

cell = xt.Line(
    elements={
        'start_cell': xt.Marker(),
        'drift0': xt.Drift(length=1.),
        'qf1':    xt.Quadrupole(k1=0.027/2, length=1.),
        'drift1': xt.Drift(length=1),
        'bend1':  xt.Bend(k0=3e-4, h=3e-4, length=45.),
        'drift2': xt.Drift(length=1.),
        'qd1':    xt.Quadrupole(k1=-0.0271/2, length=1.),
        'drift3': xt.Drift(length=1),
        'mid_cell': xt.Marker(),
        'drift4': xt.Replica('drift3'),
        'qd2':    xt.Replica('qd1'),
        'drift5': xt.Replica('drift2'),
        'bend2':  xt.Replica('bend1'),
        'drift6': xt.Replica('drift1'),
        'qf2':    xt.Replica('qf1'),
        'drift7': xt.Replica('drift0'),
        'end_cell': xt.Marker(),
    }
)
cell.particle_ref = xt.Particles(p0c=2e9)
tw_cell = cell.twiss4d(strengths=True)

xo.assert_allclose(tw_half_cell.betx[:-1], # remove '_end_point'
                   tw_cell.rows[:'mid_cell'].betx, atol=0, rtol=1e-8)
xo.assert_allclose(tw_half_cell.bety[:-1], # remove '_end_point'
                   tw_cell.rows[:'mid_cell'].bety, atol=0, rtol=1e-8)
xo.assert_allclose(tw_half_cell.alfx[:-1], # remove '_end_point'
                   tw_cell.rows[:'mid_cell'].alfx, atol=1e-8, rtol=0)
xo.assert_allclose(tw_half_cell.alfy[:-1], # remove '_end_point'
                   tw_cell.rows[:'mid_cell'].alfy, atol=1e-8, rtol=0)
