#!/usr/bin/env python
import re

from nerodia import tag_map
from nerodia.elements import html_elements, svg_elements

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

URL = 'https://raw.githubusercontent.com/watir/watir/master/lib/watir/elements/{}_elements.rb'


def generate_attributes(element_type, pkg):
    response = urlopen(URL.format(element_type))
    lines = response.read()
    classes = re.split(r'class (\w+) .*', lines)
    i = 1
    elements = []
    while i < len(classes):
        match = re.search(r'^(\w+)$', classes[i])
        if not match:
            break
        class_name = match.group(1)
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

    with open('nerodia/{}_attributes.py'.format(element_type), 'w') as f:
        with open('nerodia/elements/{}_elements.py'.format(element_type), 'a') as w:
            f.write("# Autogenerated from {} specification. "
                    "Edits may be lost.\n\n".format(element_type.upper()))
            for name, lst in elements:
                if len(lst) > 0:
                    f.write("{} = [\n".format(name.lower()))
                    for attr in lst:
                        f.write("    ({}, {!r}, {!r})".format(*attr))
                        if attr != lst[-1]:
                            f.write(',')
                        f.write('\n')
                    f.write("]\n\n")
                else:
                    f.write("{} = []\n\n".format(name))

                if not hasattr(pkg, name) and not hasattr(tag_map, name):
                    caps = element_type.upper()
                    class_str = '\n@six.add_metaclass(Meta{0}Element)\n'.format(caps)
                    if 'collection' in name.lower():
                        class_str += 'class {}({}ElementCollection):\n'.format(name, caps)
                    else:
                        class_str += 'class {}({}Element):\n'.format(name, caps)
                    class_str += '    pass\n\n'
                    w.write(class_str)


generate_attributes('html', html_elements)
generate_attributes('svg', svg_elements)
