from collections import Iterator

from django.utils.encoding import is_protected_type, smart_text

__all__ = ['quote_value', 'CsvReader']


def quote_value(value):
    if value is None:
        return 'NULL'
    if isinstance(value, bool):
        return str(int(value))
    if is_protected_type(value):
        return str(value)
    else:
        return '"%s"' % (smart_text(value).replace('\\', '\\\\')
                                          .replace('"', '\\"')
                                          .replace('\n', '\\n')
                                          .replace('\r', '\\r'))


class CsvReader(Iterator):

    def __init__(self, stream, delimiter=',', quotechar='"', escapechar='\\',
                 lineterminator='\n',
                 replacements=(('\\r', '\r'), ('\\n', '\n'), ('\\"', '"'),
                               ('\\\\', '\\')),
                 symbols=((('NULL'), None),),
                 preserve_quotes=False,
                 replace_digits=True):
        self.stream = stream
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.escapechar = escapechar
        self.lineterminator = lineterminator
        self.replacements = replacements or ()
        self.symbols = dict(symbols or {})
        self.preserve_quotes = preserve_quotes
        self.replace_digits = replace_digits

    def __iter__(self):
        for line in self.stream:
            yield self.get_row(line)

    def __next__(self):
        return self.get_row(next(self.stream))

    def next(self):
        return type(self).__next__(self)

    def get_row(self, line):
        line = smart_text(line)
        row = [[]]
        in_escape = False
        in_quotes = False
        for char in line:
            if char == self.escapechar:
                in_escape = not in_escape
            elif char == self.delimiter:
                if not in_escape and not in_quotes:
                    row.append([])
                    continue
            elif char == self.quotechar:
                if in_quotes:
                    if not in_escape:
                        in_quotes = False
                else:
                    in_quotes = True
            if char != self.escapechar:
                in_escape = False
            row[-1].append(char)
        row[-1] = row[-1][:-len(self.lineterminator)]
        row = list(map(''.join, row))
        for index, cell in enumerate(row):
            if cell in self.symbols:
                row[index] = self.symbols[cell]
            elif cell.isdigit() and self.replace_digits:
                row[index] = int(cell)
            elif (cell[0], cell[-1]) == (self.quotechar, self.quotechar):
                if not self.preserve_quotes:
                    cell = cell[1:-1]
                for replacement in self.replacements:
                    cell = cell.replace(*replacement)
                row[index] = cell
        return row
