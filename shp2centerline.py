# -*- encoding: utf-8 -*-
from shapely.geometry import mapping, shape
import fiona
import argparse
from centerline import Centerline


class Shp2centerline(object):

    def __init__(self, inputSHP, outputSHP, dist):
        self.inshp = inputSHP
        self.outshp = outputSHP
        self.dist = abs(dist)
        self.dct_polygons = {}
        self.dct_centerlines = {}

        print 'Importing polygons from: ' + self.inshp
        self.importSHP()
        print 'Calculating centerlines.'
        self.run()
        print 'Exporting centerlines to: ' + self.outshp
        self.export2SHP()
        print 'Calculation complete.'

    def run(self):
        """
        Starts processing the imported SHP file.
        It sedns the polygon's geometry allong with the interpolation distance
        to the Centerline class to create a Centerline object.
        The results (the polygon's ID and the geometry of the centerline) are
        added to the dictionary.
        """

        for key in self.dct_polygons.keys():
            poly_geom = self.dct_polygons[key]
            centerlineObj = Centerline(poly_geom, self.dist)

            self.dct_centerlines[key] = centerlineObj.createCenterline()

    def importSHP(self):
        """
        Imports the Shapefile into a dictionary. Shapefile needs to have an ID
        column with unique values.

        Returns:
            a dictionary where the ID is the key, and the value is a polygon
            geometry.
        """

        with fiona.open(self.inshp, 'r', encoding='UTF-8') as fileIN:
            for polygon in fileIN:
                polygonID = polygon['properties'][u'id']
                geom = shape(polygon['geometry'])

                self.dct_polygons[polygonID] = geom

    def export2SHP(self):
        """
        Creates a Shapefile and fills it with centerlines and their IDs.

        The dictionary contains the IDs of the centerlines (keys) and their
        geometries (values). The ID of a centerline is the same as the ID of
        the polygon it represents.
        """

        newschema = {'geometry': 'MultiLineString',
                     'id': 'int',
                     'properties': {'id': 'int'}}

        with fiona.open(self.outshp, 'w', encoding='UTF-8',
                        schema=newschema, driver='ESRI Shapefile') as SHPfile:

            for i, key in enumerate(self.dct_centerlines):
                geom = self.dct_centerlines[key]
                newline = {}

                newline['id'] = key
                newline['geometry'] = mapping(geom)
                newline['properties'] = {'id': key}

                SHPfile.write(newline)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate the centerline\
         of a polygon')

    parser.add_argument('SRC', type=str, help='Name of the input Shapefile')
    parser.add_argument('DEST', type=str, help='Name of the output Shapefile')
    parser.add_argument('BORDENS', type=float, nargs='?', default=0.5,
                        help='The density of the border (by default: 0.5)')
    args = parser.parse_args()

    Shp2centerline(args.SRC, args.DEST, args.BORDENS)
