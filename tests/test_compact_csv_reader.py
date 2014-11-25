from __future__ import unicode_literals

import logging

import pytest
from django.utils import six

from nicedjango.utils.compact_csv import CsvReader

log = logging.getLogger(__name__)


@pytest.fixture
def stream():
    csv = b'''"a\xc2\x96b\\"c'd\\re\\nf,g\\\\",1,NULL,""\n'''.decode('utf-8')
    return six.StringIO(csv)


def test_reader_raw(stream):
    r = CsvReader(stream, replacements=(), preserve_quotes=True, symbols=(),
                  replace_digits=False)
    assert list(r) == [['''"a\x96b\\"c'd\\re\\nf,g\\\\"''', '1', 'NULL', '""']]


def test_reader_none(stream):
    r = CsvReader(stream, replacements=(), preserve_quotes=True,
                  replace_digits=False)
    assert list(r) == [['''"a\x96b\\"c'd\\re\\nf,g\\\\"''', '1', None, '""']]


def test_reader_quotes(stream):
    r = CsvReader(stream, replacements=(), replace_digits=False)
    assert list(r) == [['''a\x96b\\"c'd\\re\\nf,g\\\\''', '1', None, '']]


def test_reader_replace(stream):
    r = CsvReader(stream, replace_digits=False)
    assert list(r) == [['''a\x96b"c'd\re\nf,g\\''', '1', None, '']]


def test_reader_replace_digit(stream):
    r = CsvReader(stream)
    assert list(r) == [['''a\x96b"c'd\re\nf,g\\''', 1, None, '']]
