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

from academicmarkdown import YAMLParser
import re

class TOCParser(YAMLParser):
	
	"""
	Interprets table of content command in YAML blocks of this type:

	%--
	toc:
	 mindepth: 1
	 maxdepth: 2
	 exclude: [Contents, Contact]
	--%
	"""
	
	def __init__(self, anchorHeaders=False, verbose=False):
		
		"""
		Constructor.
		
		Keyword arguments:
		anchorHeaders	--	Indicates whether headers should be turned into
							clickable anchors, mostly useful for HTML pages.
							(default=False)
		verbose			--	Indicates whether verbose output should be
							generated. (default=False)
		"""
		
		self.anchorHeaders = anchorHeaders
		super(TOCParser, self).__init__(_object=u'toc', verbose=verbose)
	
	def parseObject(self, md, _yaml, d):
		
		"""See YAMLParser.parseObject()."""
		
		if u'exclude' not in d:
			d[u'exclude'] = []
		if u'maxdepth' not in d:
			d[u'maxdepth'] = 3			
		if u'mindepth' not in d:
			d[u'mindepth'] = 1		
		headers = []
		for i in re.finditer(r'^#(.*)', md, re.M):
			h = i.group()
			for level in range(100, -1, -1):
				if h.startswith(u'#' * level):
					break
			if level not in range(d[u'mindepth'], d[u'maxdepth']+1):
				self.msg(u'Header level not in range: %s' % h)
				continue
			label = h[level:].strip()
			_id = self.labelId(label)

			if label not in d[u'exclude']:
				headers.append( (level, h, label, _id) )
				self.msg(u'%s {#%s} (%d)' % (h, _id, level))
		_md = u'\n'
		lRep = []
		for level, h, label, _id in headers:
			print h
			_md += u'\t' * (level-d[u'mindepth']) # Indent
			_md += u'- [%s](#%s)\n' % (label, _id)
			if self.anchorHeaders:
				md = md.replace(h, u'%s [%s](#%s) {#%s}' % (u'#'*level, label, \
					_id, _id))
		_md += u'\n'
		return md.replace(_yaml, _md)
	
	def labelId(self, label):
		
		"""
		Generates and ID for a label, simulating the IDs generated by Pandoc.
		
		IDs should match the IDs that generated by Pandoc. The basic
		algorithm appears to be that spaces are converted to dashes, dashes are
		left in and all non-alphanumeric characters are ignored. Avoid dashes
		at the beginning and end of the ID and also avoid double dashes.
		BUG: Pandoc doesn't properly parse (at least) Chinese characters,
		so links in Chinese TOCs will be broken.
		
		Arguments:
		label		--	A label.
		
		Returns:
		An ID.		
		"""
		
		_id = u''
		for ch in label:
			if ch.isalnum() or ch in (u'-', u'.', u'_'):
				_id += ch.lower()
			elif ch.isspace() and len(_id) > 0 and _id[-1] != u'-':
				_id += u'-'
		return _id.strip(u'-.')