__author__ = 'sstippa'
'''
Purpose: Change existing Styled Layer Descriptor (SLD) XML

Requirements: Python 2.7+ - XML Module

Author: Sawyer Stippa, USGS
email: sstippa@usgs.gov
date: 3/18/15

'''

import xml.etree.ElementTree as ET

xml = r'I:\DSwebmap\Geoserver\colormaps\temp.xml' # Existing SLD
tree = ET.parse(xml)
ET.register_namespace("","http://www.opengis.net/sld")
root= tree.getroot()
colorMap = '{http://www.opengis.net/sld}ColorMap'

print 'Removing existing entries' # Clear all entries
for elem in tree.iter(tag=colorMap):
   for entry in list(elem):
        elem.remove(entry)

print 'Creating new entries' # Create New Entries
color0 = "#000000"
label0 = "nodata"
quantity0 = '0'
entry0 = {'color':color0,'label':label0,'quantity':quantity0 }

color1 = "#99CCFF"
label1 = "Label 1"
quantity1 = '1'
entry1 = {'color':color1,'label':label1,'quantity':quantity1 }

color2 = "#000000"
label2 = "nodata"
quantity2 = '0'
entry2 = {'color':color2,'label':label2,'quantity':quantity2 }

entries = [entry0,entry1,entry2] # List of entries 

print 'Appending new entries' #Append ColorMap Entries
for entry in entries:
    for elem in tree.iter(tag=colorMap):
        b = ET.SubElement(elem, 'ColorMapEntry', entry)

ET.dump(root)

print 'Saving' # Overwrite existing xml
tree.write(xml) 

print 'Process complete'
