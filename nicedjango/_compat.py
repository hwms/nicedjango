import sys

if sys.version_info[:2] == (2, 6):
    from ordereddict import OrderedDict  # @UnresolvedImport @UnusedImport
else:
    from collections import OrderedDict  # @Reimport @UnusedImport

if sys.version_info[0] == 2:
    from itertools import izip_longest
    try:
        from cStringIO import StringIO as BytesIO
    except ImportError:
        from StringIO import StringIO as BytesIO  # @UnusedImport
    basestring = basestring  # @ReservedAssignment
    unicode = unicode  # @ReservedAssignment
    bytes = str  # @ReservedAssignment
elif sys.version_info[0] == 3:
    from itertools import zip_longest  # @UnresolvedImport
    izip_longest = zip_longest
    from io import BytesIO  # @UnusedImport @Reimport
    basestring = str  # @ReservedAssignment
    unicode = str  # @ReservedAssignment
    bytes = bytes  # @ReservedAssignment
