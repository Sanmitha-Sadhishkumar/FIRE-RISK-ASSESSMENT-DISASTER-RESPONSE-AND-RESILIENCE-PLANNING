from OSMPythonTools.api import Api
from OSMPythonTools.overpass import Overpass
overpass = Overpass()
result = overpass.query('way["name"="Stephansdom"]; out body;') 
stephansdom = result.elements()[0]
print(stephansdom)
stephansdom.tag('name:en')
# "Saint Stephen's Cathedral"
print('%s %s, %s %s' %(stephansdom.tag('addr:street'), stephansdom.tag('addr:housenumber'), stephansdom.tag('addr:postcode'), stephansdom.tag('addr:city')))
# 'Stephansplatz 3, 1010 Wien'
stephansdom.tag('building')
# 'cathedral'
stephansdom.tag('denomination')