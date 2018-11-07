#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2018 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

# Support for fake joystick/gamepad during devlopment
# if no 'real' joystick/gamepad is available use keyboard emulation
# 'ctrl' + 'alt' + numberKey

from __future__ import absolute_import, division, print_function
from psychopy import event

class Joystick:
    def __init__(self, device_number):
        self.device_number = device_number
        self.numberKeys=['0','1','2','3','4','5','6','7','8','9']
        self.modifierKeys=['ctrl','alt']

    def getNumButtons(self):
        return(len(self.numberKeys))

    def getAllButtons(self):
        keys = event.getKeys(keyList=self.numberKeys, modifiers=True)
        values=[ key for key, modifiers in keys if all([modifiers[modKey] for modKey in self.modifierKeys]) ]
        self.state=[ key in values for key in self.numberKeys]
        return(self.state)
