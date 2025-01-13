"""Blender operators that ship with `bpy_jupyter`."""

from functools import reduce

from .. import contracts as ct
from . import simple_operator

BL_REGISTER: list[ct.BLClass] = [
	*simple_operator.BL_REGISTER,
]
BL_HANDLERS: ct.BLHandlers = reduce(
	lambda a, b: a + b,
	[
		simple_operator.BL_HANDLERS,
	],
	ct.BLHandlers(),
)
BL_KEYMAP_ITEMS: list[ct.BLKeymapItem] = [
	*simple_operator.BL_KEYMAP_ITEMS,
]
