import itertools
import sys

if sys.version_info[0] == 2:
    from itertools import izip_longest, imap, izip
    basestring = basestring # @ReservedAssignment
    unicode = unicode # @ReservedAssignment
    bytes = str # @ReservedAssignment
    filterfalse = itertools.ifilterfalse

elif sys.version_info[0] == 3:
    from itertools import zip_longest # @UnresolvedImport
    izip_longest = zip_longest
    imap = map
    izip = zip
    basestring = str # @ReservedAssignment
    unicode = str # @ReservedAssignment
    bytes = bytes # @ReservedAssignment
    filterfalse = itertools.filterfalse # @UndefinedVariable

exclude = filterfalse
