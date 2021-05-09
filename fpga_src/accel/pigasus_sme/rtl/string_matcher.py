import argparse
import xml.etree.ElementTree as ET
import os
from jinja2 import Environment, FileSystemLoader
from copy import copy
from copy import deepcopy
#from ROM import ROM
from math import log2
from math import ceil

context = {}
byte_size = 32
half_byte_size = int(byte_size/2)
bucket_size = 8
byte_pos = []
bucket = []
nbits = []
andmsk = []
mem_size = []
bm_size = []
arb_size = 8
#this is 2^5 = 32
fifo_depth = 5 

nbits.append(15)
nbits.append(15)
nbits.append(12)
nbits.append(12)
nbits.append(11)
nbits.append(12)
nbits.append(10)
nbits.append(8)

andmsk.append("64'hffffffffffffffff")
andmsk.append("64'hffffffffffffffff")
andmsk.append("64'hffffffffffffff00")
andmsk.append("64'hffffffffffff0000")
andmsk.append("64'hffffffffff000000")
andmsk.append("64'hffffffff00000000")
andmsk.append("64'hffffff0000000000")
andmsk.append("64'hffff000000000000")

for i in range(0,bucket_size):
    temp = 2**nbits[i]
    mem_size.append(temp)
    bm_size.append(int(temp/8))

for i in range(0,byte_size):
    byte_pos.append(i)

for i in range(0,bucket_size):
    bucket.append(i)


context['byte_pos'] = byte_pos
context['bucket'] = bucket
context['bucket_size'] = bucket_size
context['byte_size'] = byte_size
context['half_byte_size'] = half_byte_size
context['nbits'] = nbits
context['andmsk'] = andmsk
context['mem_size'] = mem_size
context['bm_size'] = bm_size
context['arb_size'] = arb_size
context['fifo_depth'] = fifo_depth
########################################################
env = Environment(loader=FileSystemLoader('./'), trim_blocks=True, lstrip_blocks=True)
template = env.get_template('first_filter.template')

# Render the template for the output file.
rendered_file = template.render(context=context)

# Write output file
with open('first_filter.sv', 'w') as outFile:
    outFile.write(rendered_file)



########################################################
env = Environment(loader=FileSystemLoader('./'), trim_blocks=True, lstrip_blocks=True)
template = env.get_template('hashtable_top.template')

# Render the template for the output file.
rendered_file = template.render(context=context)

# Write output file
with open('hashtable_top.sv', 'w') as outFile:
    outFile.write(rendered_file)


########################################################
env = Environment(loader=FileSystemLoader('./'), trim_blocks=True, lstrip_blocks=True)
template = env.get_template('frontend.template')

# Render the template for the output file.
rendered_file = template.render(context=context)

# Write output file
with open('frontend.sv', 'w') as outFile:
    outFile.write(rendered_file)


########################################################
#env = Environment(loader=FileSystemLoader('./'), trim_blocks=True, lstrip_blocks=True)
#template = env.get_template('arbiter.template')
#
## Render the template for the output file.
#rendered_file = template.render(context=context)
#
## Write output file
#with open('arbiter.v', 'w') as outFile:
#    outFile.write(rendered_file)

########################################################
env = Environment(loader=FileSystemLoader('./'), trim_blocks=True, lstrip_blocks=True)
template = env.get_template('backend.template')

# Render the template for the output file.
rendered_file = template.render(context=context)

# Write output file
with open('backend.sv', 'w') as outFile:
    outFile.write(rendered_file)


########################################################
env = Environment(loader=FileSystemLoader('./'), trim_blocks=True, lstrip_blocks=True)
template = env.get_template('string_matcher.template')

# Render the template for the output file.
rendered_file = template.render(context=context)

# Write output file
with open('string_matcher.sv', 'w') as outFile:
    outFile.write(rendered_file)


########################################################
#env = Environment(loader=FileSystemLoader('./'), trim_blocks=True, lstrip_blocks=True)
#template = env.get_template('tb.template')
#
## Render the template for the output file.
#rendered_file = template.render(context=context)
#
## Write output file
#with open('tb.v', 'w') as outFile:
#    outFile.write(rendered_file)

