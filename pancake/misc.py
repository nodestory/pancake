#!/usr/bin/env python
# -*- coding: utf-8 -*-


def get_enum_choices(enum):
    return tuple((e.value, e.name) for e in enum)


def get_enum_values(enum):
    return tuple(e.value for e in enum)
