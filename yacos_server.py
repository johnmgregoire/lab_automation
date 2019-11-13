import actions

blockd = {'potentiostat':False,
          'motor':False,
          'io':False}


move_rel_op = {'x':-10,'axis':'x','blockd':blockd}
cv_param_op = {'Vinit':0, 'Vfinal': 0, 'Vapex1': 1, 'Vapex2': -1, 'ScanInit': 0.1,
                'ScanApex': 0.1, 'ScanFinal': 0.1, 'HoldTime0': 0, 'HoldTime1': 0,
                'HoldTime2': 0, 'Cycles': 1, 'SampleRate': 0.01,
                'control_mode': 'potentiostatic','blockd':blockd}
light_cycle_op = {'on_time':0.2, 'off_time': 0.2, 'ncycles':10,'blockd':blockd}



r = []
r.append(actions.move(**move_rel_op))
r.append(actions.light_cycles(**light_cycle_op))
r.append(actions.iblocking_cv(**cv_param_op))
