#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Copyright (C) 2017 David Pinto <david.pinto@bioch.ox.ac.uk>
##
## Microscope is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Microscope is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Microscope.  If not, see <http://www.gnu.org/licenses/>.

"""Boston MicroMachines Corporation deformable mirrors.
"""

import ctypes
import os
import warnings

import numpy

import microscope
import microscope.abc
import microscope._wrappers.BMC as BMC


class BMCDeformableMirror(microscope.abc.DeformableMirror):
    """Boston MicroMachines (BMC) deformable mirror.

    BMC deformable mirrors only support software trigger.
    """
    def __init__(self, serial_number: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._dm = BMC.DM()

        if __debug__:
            BMC.ConfigureLog(os.devnull.encode(), BMC.LOG_ALL)
        else:
            BMC.ConfigureLog(os.devnull.encode(), BMC.LOG_OFF)

        status = BMC.Open(self._dm, serial_number.encode())
        if status:
            raise Exception(BMC.ErrorString(status))

    @property
    def n_actuators(self) -> int:
        return self._dm.ActCount


    @property
    def trigger_type(self) -> microscope.TriggerType:
        return microscope.TriggerType.SOFTWARE

    @property
    def trigger_mode(self) -> microscope.TriggerMode:
        return microscope.TriggerMode.ONCE

    def set_trigger(self, ttype: microscope.TriggerType,
                    tmode: microscope.TriggerMode) -> None:
        if ttype is not microscope.TriggerType.SOFTWARE:
            raise Exception('the only trigger type supported is software')
        if tmode is not microscope.TriggerMode.ONCE:
            raise Exception('the only trigger mode supported is \'once\'')


    def _do_apply_pattern(self, pattern: numpy.ndarray) -> None:
        data_pointer = pattern.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        status = BMC.SetArray(self._dm, data_pointer, None)
        if status:
            raise Exception(BMC.ErrorString(status))

    def __del__(self) -> None:
        status = BMC.Close(self._dm)
        if status:
            warnings.warn(BMC.ErrorString(status), RuntimeWarning)
            super().__del__()
