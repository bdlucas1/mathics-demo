import re
import sys

class D(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

def read(f):

    fields = None

    for i, line in enumerate(f):

        line = line.expandtabs()

        if i == 0:
            pos = 0
            fields = []
            while True:
                match = re.search(r"\S", line[pos:])
                if match:
                    pos += match.start()
                    fields.append(pos)
                else:
                    break
                match = re.search(r"\s", line[pos:])
                if match:
                    pos += match.start()
                else:
                    break
            fields.append(-1)

        ranges = zip(fields[:-1],fields[1:])
        values = tuple(line[r[0]:r[1]].strip() for r in ranges)

        if i == 0:
            names = values
        else:
            yield  D({name: value for name, value in zip(names, values)})
