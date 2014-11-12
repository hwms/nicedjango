import sys

if sys.version_info[:2] == (2, 6):
    from ordereddict import OrderedDict  # @UnresolvedImport @UnusedImport
else:
    from collections import OrderedDict  # @Reimport @UnusedImport

if sys.version_info[0] == 2:
    from itertools import izip_longest
    basestring = basestring  # @ReservedAssignment
    unicode = unicode  # @ReservedAssignment
    bytes = str  # @ReservedAssignment
elif sys.version_info[0] == 3:
    from itertools import zip_longest  # @UnresolvedImport
    izip_longest = zip_longest
    basestring = str  # @ReservedAssignment
    unicode = str  # @ReservedAssignment
    bytes = bytes  # @ReservedAssignment
