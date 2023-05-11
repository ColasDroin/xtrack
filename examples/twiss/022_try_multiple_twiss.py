import time
import multiprocessing as mp

import numpy as np

import xtrack as xt
import xpart as xp

from xobjects.context_cpu import XobjectPointer

from cpymad.madx import Madx

# Load the line
if __name__ == '__main__':
    line = xt.Line.from_json(
        '../../test_data/hllhc15_noerrors_nobb/line_w_knobs_and_particle.json')
    line.particle_ref = xp.Particles(p0c=7e12, mass=xp.PROTON_MASS_EV)
    line.build_tracker()

    tw_ref = line.twiss()

    ele_start_match = 's.ds.l1.b1'
    ele_end_match = 'e.ds.r1.b1'
    tw_init = tw_ref.get_twiss_init(ele_start_match)

    ele_index_start = line.element_names.index(ele_start_match)
    ele_index_end = line.element_names.index(ele_end_match)

    ttt = line.twiss(
        #verbose=True,
        ele_start=ele_index_start,
        ele_stop=ele_index_end,
        twiss_init=tw_init,
        _keep_initial_particles=True,
        _keep_tracking_data=True,
        )

    tw = line.twiss(
        #verbose=True,
        ele_start=ele_index_start,
        ele_stop=ele_index_end,
        twiss_init=tw_init,
        _ebe_monitor=ttt.tracking_data,
        _initial_particles=ttt._initial_particles
            )

    on_x1_values = np.linspace(50, 150, 16)
    buffers = []
    for on_x1 in on_x1_values:
        line.vars['on_x1'] = on_x1
        buffers.append(line.tracker._buffer.buffer.copy())

    init_part = ttt._initial_particles

    # tr_data_xobject = ttt.tracking_data._xobject
    # init_part_xobject = ttt._initial_particles._xobject
    # pref_xobject = line.particle_ref._xobject

    # dummy_tracker = xt.Tracker(line=xt.Line())
    # dummy_tracker._track_kernel = None
    # dummy_tracker._tracker_data.__dict__.clear()
    # dummy_tracker._tracker_data._element_ref_data = XobjectPointer(
    #     line.tracker._tracker_data._element_ref_data)
    # dummy_tracker._track_kernel = line.tracker._track_kernel
    # dummy_tracker._tracker_data.line_length = line.tracker._tracker_data.line_length

    # dummy_tracker.record_last_track = None

    # element_names = line.element_names

    input = {'buffer': None}

    def f_for_pool(input):
        buffer = input['buffer']

        # line_internal = xt.Line()
        # line_internal.particle_ref = xp.Particles(_xobject=pref_xobject)
        # line_internal.tracker = dummy_tracker
        # line_internal.element_names = element_names
        # line_internal.tracker.line = line_internal

        line.tracker._tracker_data._buffer.buffer = buffer
        tw = line.twiss(
             ele_start=ele_index_start,
             ele_stop=ele_index_end,
             twiss_init=tw_init,
             _ebe_monitor='ONE_TURN_EBE',
             _initial_particles=init_part
             # _ebe_monitor=ttt.tracking_data,
            # _initial_particles=ttt._initial_particles,
            )
        tw.particle_on_co = None
        # res = {'name': tw.name, 'px': tw.px}
        # res= {'name': 'ip1', 'px': [0.]}

        return tw._data

    inputs = []
    for buffer in buffers:
        iii = input.copy()
        iii['buffer'] = buffer
        inputs.append(iii)

    ip1_index = list(tw.name).index('ip1')

    n_repeat = 10

    t1 = time.perf_counter()
    print('Start serial')
    for i in range(n_repeat):
        twisses_serial = list(map(f_for_pool, inputs))
        # print(twisses_serial[1]['px'][ip1_index])
    print('End serial')
    t2 = time.perf_counter()
    print(f'Elapsed time serial: {t2-t1} s')


    pool = mp.Pool(processes=2)
    t1 = time.perf_counter()
    print('Start parallel')
    for i in range(n_repeat):
        twisses_parallel = pool.map(f_for_pool, inputs)
        # print(twisses_parallel[1]['px'][ip1_index])
    print('End parallel')

    t2 = time.perf_counter()
    print(f'Elapsed time parallel: {t2-t1} s')


    print('Result serial:')
    for on_x1, twdata in zip(on_x1_values, twisses_serial):
        tw._data = twdata
        print(f'on_x0 = {on_x1}, px["ip1"] = {tw["px", "ip1"]*1e6:f}e-6')

    print('Result parallel:')
    for on_x1, twdata in zip(on_x1_values, twisses_parallel):
        tw._data = twdata
        print(f'on_x0 = {on_x1}, px["ip1"] = {tw["px", "ip1"]*1e6:f}e-6')




    # td = line.tracker._tracker_data
    # td._element_ref_data = XobjectPointer(td._element_ref_data)
    # td._element_dict = None
    # td._elements = None
    # td.element_classes = None
    # td._ElementRefClass = None