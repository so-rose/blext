# blext
# Copyright (C) 2025 blext Project Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Implements the `lru_method` decorator."""

import functools
import typing as typ
import weakref

ClassType = typ.TypeVar('ClassType')
ParamsType = typ.ParamSpec('ParamsType')
ReturnType = typ.TypeVar('ReturnType')


def lru_method(
	maxsize: int = 128,
	typed: bool = False,
) -> typ.Callable[
	[typ.Callable[typ.Concatenate[ClassType, ParamsType], ReturnType]],
	typ.Callable[typ.Concatenate[ClassType, ParamsType], ReturnType],
]:
	"""Memoize a method of an immutable object, such that the cache is deleted with the object."""

	def method_decorator(
		method: typ.Callable[typ.Concatenate[ClassType, ParamsType], ReturnType],
	) -> typ.Callable[typ.Concatenate[ClassType, ParamsType], ReturnType]:
		"""Factory-constructed decorator to apply to the class method."""

		@functools.wraps(method)
		def method_decorated(
			instance: ClassType, *args: ParamsType.args, **kwargs: ParamsType.kwargs
		) -> ReturnType:
			"""Modified class method that maintains an LRU cache."""
			weak_instance = weakref.ref(instance)

			@functools.wraps(method)
			@functools.lru_cache(maxsize=maxsize, typed=typed)
			def cached_method(*args: ParamsType.args, **kwargs: ParamsType.kwargs):
				realized_weak_instance = weak_instance()
				if realized_weak_instance:
					return method(realized_weak_instance, *args, **kwargs)

				msg = 'Tried to get value of an `@lru_method`-decorated instance method, but that instance no longer exists.'
				raise RuntimeError(msg)

			object.__setattr__(instance, method.__name__, cached_method)
			return cached_method(*args, **kwargs)

		return method_decorated

	return method_decorator
