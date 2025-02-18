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

import griffe
import plum
import quartodoc as qd
from quartodoc.renderers.base import sanitize


class Renderer(qd.MdRenderer):
	style = 'blext'

	@plum.dispatch
	def render(self, el: str) -> str:
		"""Sanitize render annotations."""
		return sanitize(el)

	@plum.dispatch
	def signature(
		self,
		el: griffe.Class | griffe.Function,
		source: griffe.Alias | None = None,
	) -> str:
		"""Return a string representation of an object's signature."""
		name = self._fetch_object_dispname(source or el)
		pars = self.render(self._fetch_method_parameters(el))

		flat_sig = f'{name}({", ".join(pars)})'
		if len(flat_sig) > 80:
			indented = [' ' * 4 + par + ',' for par in pars]
			sig = '\n'.join([f'{name}(', *indented, ')'])
		else:
			sig = flat_sig

		return f'```python\n{sig}\n```'

	@plum.dispatch
	def render(self, el: qd.layout.DocFunction | qd.layout.DocAttribute) -> str:
		# Custom Header Render
		_str_dispname = f'`{el.name}`'
		_anchor = f'{{ #{el.obj.path} }}'
		title = f'{"#" * self.crnt_header_level} {_str_dispname} {_anchor}'

		str_sig = self.signature(el)
		sig_part = [str_sig] if self.show_signature else []

		with self._increment_header():
			body = self.render(el.obj)

		return '\n\n'.join([title, *sig_part, body])
		# return '\n\n'.join([*sig_part, body])
