from PIL import Image
import urllib, io

from urllib.parse import urlencode
from urllib.request import urlopen
from math import log, exp, tan, atan, pi, ceil

EARTH_RADIUS = 6378137
EQUATOR_CIRCUMFERENCE = 2 * pi * EARTH_RADIUS
INITIAL_RESOLUTION = EQUATOR_CIRCUMFERENCE / 256.0
ORIGIN_SHIFT = EQUATOR_CIRCUMFERENCE / 2.0

def latlontopixels(lat, lon, zoom):
    mx = (lon * ORIGIN_SHIFT) / 180.0
    my = log(tan((90 + lat) * pi/360.0))/(pi/180.0)
    my = (my * ORIGIN_SHIFT) /180.0
    res = INITIAL_RESOLUTION / (2**zoom)
    px = (mx + ORIGIN_SHIFT) / res
    py = (my + ORIGIN_SHIFT) / res
    return px, py

def pixelstolatlon(px, py, zoom):
    res = INITIAL_RESOLUTION / (2**zoom)
    mx = px * res - ORIGIN_SHIFT
    my = py * res - ORIGIN_SHIFT
    lat = (my / ORIGIN_SHIFT) * 180.0
    lat = 180 / pi * (2*atan(exp(lat*pi/180.0)) - pi/2.0)
    lon = (mx / ORIGIN_SHIFT) * 180.0
    return lat, lon

############################################

# 42.3579141,-71.0938266
upperleft =  '42.3829141,-71.1188266'  
lowerright = '42.3329141,-71.0688266'

zoom = 17   # be careful not to get too many images!

ullat, ullon = map(float, upperleft.split(','))
lrlat, lrlon = map(float, lowerright.split(','))
scale = 1
maxsize = 640
ulx, uly = latlontopixels(ullat, ullon, zoom)
lrx, lry = latlontopixels(lrlat, lrlon, zoom)
dx, dy = lrx - ulx, uly - lry
cols, rows = int(ceil(dx/maxsize)), int(ceil(dy/maxsize))
bottom = 125
largura = int(ceil(dx/cols))
altura = int(ceil(dy/rows))-20
alturaplus = altura + bottom


final = Image.new("RGB", (int(dx), int(dy)))
for x in range(cols):
    for y in range(rows):
        dxn = largura * (0.5 + x)
        dyn = altura * (0.5 + y)
        latn, lonn = pixelstolatlon(ulx + dxn, uly - dyn - bottom/2, zoom)
        position = ','.join((str(latn), str(lonn)))
        print (x, y, position)
        urlparams = urlencode({'center': position,
                                      'zoom': str(zoom),
                                      'size': '%dx%d' % (largura, alturaplus),
                                      'maptype': 'satellite',
                                      'sensor': 'false',
                                      'scale': scale,
                                      'style': 'feature:all|element:labels|visibility:off'})
        urlparams2 = urlencode({'style': 'feature:road|element:all|visibility:off'})
        urlparams3 = urlencode({'style': 'feature:transit|element:all|visibility:off'})
        url = 'http://maps.google.com/maps/api/staticmap?' + urlparams +'&' + urlparams2 +'&' + urlparams3
        print(url)
        f=urlopen(url)
        im=Image.open(io.BytesIO(f.read()))
        final.paste(im, (int(x*largura), int(y*altura)))
#final.show()
final.save('test.bmp')
