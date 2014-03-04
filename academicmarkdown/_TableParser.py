# -*- coding: utf-8 -*-

"""
This file is part of zoteromarkdown.

zoteromarkdown is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

zoteromarkdown is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with zoteromarkdown.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import yaml
from academicmarkdown import YAMLParser
import subprocess
import sys

tableTemplate = {u'html5':  u"""
<span style='color:red;'>NOT IMPLEMENTED</span>
""",
u'kramdown':  u"""
%(table)s

__Table %(nTbl)d.__ %(caption)s\n{: .tbl-caption #%(id)s}
"""}


class TableParser(YAMLParser):

	"""
	The `table` block reads a table from a `.csv` file and embed it into the
	document. The source file needs to be a utf-8 encoded file that is
	comma separated and double quoted.

	%--
	table:
	 id: MyTable
	 source: my_table.csv
	 caption: "My table caption."
	--%
	"""

	def __init__(self, style=u'inline', template=u'html5', verbose=False):

		"""
		Constructor.

		Keyword arguments:
		style		--	Can be u'inline' or u'below' to indicate whether figures
						should be placed in or below the text.
						(default=u'inline')
		template	--	Indicates the output format, which can be 'odt' or
						'html5'. (default=u'html5')
		verbose		--	Indicates whether verbose output should be generated.
						(default=False)
		"""

		self.style = style
		self.template = template
		super(TableParser, self).__init__(_object=u'table', required=['id', \
			'source'], verbose=verbose)

	def parse(self, md):

		"""See BaseParser.parse()."""

		self.nTbl = 0
		return super(TableParser, self).parse(md)

	def parseObject(self, md, _yaml, d):

		"""See YAMLParser.parseObject()."""

		self.nTbl += 1
		d['nTbl'] = self.nTbl
		self.msg(u'Found table: %s (%d)' % (d['id'], self.nTbl))
		d[u'source'] = self.getPath(d[u'source'])
		if u'caption' not in d:
			d[u'caption'] = u''
		# Read table and turn it into a kramdown-style table
		s = u''
		import csv
		with open(d[u'source'], u'rb') as csvFile:
			csvReader = csv.reader(csvFile, delimiter=',', quotechar='"')
			for row in csvReader:
				s += (u'|' + u'|'.join(row) + u'|\n').decode(u'utf-8')
		d[u'table'] = s
		tbl = tableTemplate[self.template] % d
		# Insert/ append table into document
		if self.style == u'inline':
			md = md.replace(_yaml, tbl)
		else:
			md = md.replace(_yaml, u'')
			md += tbl
		# Replace reference to table
		md = md.replace(u'%%%s' % d[u'id'], u'[Table %d](#%s)' % (self.nTbl, \
			d[u'id']))
		return md
