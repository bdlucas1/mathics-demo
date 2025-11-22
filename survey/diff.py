import sym
import core
import tabbed
import util

def read(fn):
    f = open(fn)
    return {d["option"]: d for d in tabbed.read(f)}

graphics= read("wma-graphics.tab")
graphics3d = read("wma-graphics3d.tab")
mcs = read("mcs-graphics.tab")

print("graphics3d only", graphics3d.keys() - graphics.keys())
print("graphics only", graphics.keys() - graphics3d.keys())
print("graphics/graphics3d differ")
for x in graphics.keys() & graphics3d.keys():
    if graphics[x] != graphics3d[x]:
        print(f"{x} {graphics[x]} {graphics3d[x]}")

print("graphics/mcs differ")        
for x in mcs.keys():
    if graphics[x].default != mcs[x].default:
        print(f"{x} {graphics[x].default} {mcs[x].default}")

print("=== GRAPHICS_OPTIONS")
for x in graphics.keys() - mcs.keys():
    print(f'    "{x}": "{graphics[x].default}",')

print("=== G3D")    
for x in graphics3d.keys() - graphics.keys():
    print(f'    "{x}": "{graphics3d[x].default}",')

print("=== manifest g")
for x in graphics.keys() - mcs.keys():
    print(f"System`{x}")
print("=== manfest g3")    
for x in graphics3d.keys() - mcs.keys():
    print(f"System`{x}")

print("=== builtin")    
for x in graphics.keys() - mcs.keys():
    print(f"class {x}(Builtin): pass")
print("=== manfest g3")    
for x in graphics3d.keys() - mcs.keys():
    print(f"class {x}(Builtin): pass")

print("=== symbol")    
for x in graphics.keys() - mcs.keys():
    print(f'Symbol{x} = Symbol("System`{x}")')
print("=== symbol3d g3")    
for x in graphics3d.keys() - mcs.keys():
    print(f'Symbol{x} = Symbol("System`{x}")')


import re

def camel_to_snake(camel_case_string):
    # Insert an underscore before any uppercase letter that is not at the beginning of the string
    # and is preceded by a lowercase letter or digit.
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', camel_case_string)
    # Insert an underscore before any uppercase letter that is preceded by a lowercase letter or digit.
    # This also handles cases where an uppercase letter is followed by another uppercase letter, then a lowercase letter.
    s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()

print("=== consumer")
for x in graphics.keys():
    print(f'{camel_to_snake(x)} = get_option("{x}")')
print("=== consumer3d")
for x in graphics3d.keys() - graphics.keys():
    print(f'{camel_to_snake(x)} = get_option("{x}")')
