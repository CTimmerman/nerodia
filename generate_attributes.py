#!/usr/bin/env python
import re
try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

URL = 'https://raw.githubusercontent.com/watir/watir/master/lib/watir/elements/html_elements.rb'

response = urlopen(URL)
lines = response.read()
classes = re.split(r'class (\w+) .*', lines)
i = 1
elements = []
while i < len(classes):
    match = re.search(r'^(\w+)$', classes[i])
    if not match:
        break
    class_name = match.group(1).lower()
    class_attrs = []
    i += 1
    attrs = classes[i].split('\n')
    for line in attrs:
        attr = []
        if 'end\n' in line:
            break
        matches = re.search(r'attribute\(\W*(\w+)\W+(\w+)\W+(\w+)\)', line)
        if matches is None:
            continue
        typ, key, val = matches.groups()
        if typ == 'Integer':
            attr.append(int.__name__)
        elif typ == 'Float':
            attr.append(float.__name__)
        elif typ == 'Boolean':
            attr.append(bool.__name__)
        else:
            attr.append(str.__name__)
        attr.append(key)
        attr.append(val)
        class_attrs.append(attr)
    elements.append([class_name, class_attrs])
    i += 1

with open('watir_snake/generated_attributes.py', 'w') as f:
    f.write("# Autogenerated from HTML specification. Edits may be lost.\n\n")
    for name, lst in elements:
        if len(lst) > 0:
            f.write("{} = [\n".format(name))
            for attr in lst:
                f.write("    ({}, {!r}, {!r})".format(*attr))
                if attr != lst[-1]:
                    f.write(',')
                f.write('\n')
            f.write("]\n\n")
        else:
            f.write("{} = []\n\n".format(name))
