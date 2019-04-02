import geopandas
import fiona
import os
from shapely.geometry import Point, Polygon, MultiPolygon


class vector():
    def __init__(self):
        path_input = None
        # enable KML support which is disabled by default
        fiona.drvsupport.supported_drivers['kml'] = 'rw'
        # enable KML support which is disabled by default
        fiona.drvsupport.supported_drivers['KML'] = 'rw'

    def check_driver(self):
        ext = self.extention
        ext = ext.upper()
        if ext == 'KML':
            driver = 'KML'

        elif ext == 'JSON':
            driver = 'GeoJSON'

        elif ext == 'SHP':
            driver = 'ESRI Shapefile'
        else:
            raise Exception('File format %s is not supported' % (ext))

        return driver

    def config(self):
        try:
            self.df = geopandas.read_file(self.path_input)
        except Exception as e:
            raise Exception('%s File could not be loaded or supported')

        try:
            self.crs = self.df.crs
        except Exception as e:
            raise Exception(
                'Coordinate system is not defined or could not be read')

        self.extention = os.path.splitext(self.path_input)[1][1:].upper()

    def towgs(self, path_towgs=None):
        """
        Converts data to WGS coordinate system
        """
        print('Converting to WGS')
        # Checking driver for support
        driver = self.check_driver()

        try:
            world = self.df.to_crs({'init': 'epsg:4326'})
        except Exception as e:
            raise Exception(
                'Error converting to epsg:%d coordinate system' % (epsg))

        # Converting polygon to multipolygons
        try:
            world["geometry"] = [MultiPolygon([feature]) if type(
                feature) == Polygon else feature for feature in world["geometry"]]
        except Exception as e:
            raise Exception('Error transforming polygon tol multipolygon')

        # Saving data to disk
        try:
            if path_towgs is not None:
                wgs = world.to_file(path_towgs, driver=driver)
            else:
                path_towgs = os.path.splitext(self.path_input)[
                    0] + '_wgs.' + self.extention
                wgs = world.to_file(path_towgs, driver=driver)
        except Exception as e:
            raise Exception('Error saving data to WGS')

        print('Successfully saved to WGS : %s' % (path_towgs))

    def tokml(self, path_tokml=None):
        """
        Converts data to KML format to epsg 4326
        """
        print('converting to KML')

        # Converting to WGS
        try:
            world = self.df.to_crs({'init': 'epsg:4326'})
        except Exception as e:
            raise Exception('Error converting CRS to epsg:4326')

        # Converting polygon to multipolygons
        try:
            world["geometry"] = [MultiPolygon([feature]) if type(
                feature) == Polygon else feature for feature in world["geometry"]]
        except Exception as e:
            raise Exception('Error transforming polygon to multipolygon')

        # Saving data to disk
        try:
            if path_tokml is not None:
                wgs = world.to_file(path_tokml, driver='KML')
            else:
                path_tokml = os.path.splitext(self.path_input)[0] + '.kml'
                wgs = world.to_file(path_tokml, driver='KML')
        except Exception as e:
            raise Exception('Error saving data to KML')
        print('Successfully converted : %s' % (path_tokml))

    def togeojson(self, epsg=4326, path_togeojson=None):
        """
        Converts data to geojson format to specifi epsg code
        """
        print('converting to geojson')
        # Converting to coordinate system
        try:
            world = self.df.to_crs({'init': 'epsg:%d' % (epsg)})
        except Exception as e:
            raise Exception('Error converting to epsg:%d' % d(epsg))

        # Converting polygon to multipolygons
        try:
            world["geometry"] = [MultiPolygon([feature]) if type(
                feature) == Polygon else feature for feature in world["geometry"]]
        except Exception as e:
            raise Exception('Erro transforming polygon to multipolygon')

        # Saving data to disk
        try:
            if path_togeojson is not None:
                wgs = world.to_file(path_togeojson, driver='GeoJSON')
            else:
                path_togeojson = os.path.splitext(
                    self.path_input)[0] + '.geojson'
                wgs = world.to_file(path_togeojson, driver='GeoJSON')
        except Exception as e:
            raise Exception('Error saving data to geojson')
        print('Successfully converted : %s' % (path_togeojson))

    def toshp(self, epsg=4326, path_toshp=None):
        """
        Converts data to shp format
        """
        print('converting to shp')
        # Converting to coordinate system
        try:
            world = self.df.to_crs({'init': 'epsg:%s' % (epsg)})
        except Exception as e:
            raise Exception('Error converting to epsg:%s' % (epsg))

        # Converting polygon to multipolygons
        print('poly to multi poly')
        try:
            world["geometry"] = [MultiPolygon([feature]) if type(
                feature) == Polygon else feature for feature in world["geometry"]]
        except Exception as e:
            raise Exception('')

        # Saving data to disk
        try:
            if path_toshp is not None:
                wgs = world.to_file(path_toshp, driver='ESRI Shapefile')
            else:
                path_toshp = os.path.splitext(self.path_input)[0] + '.shp'
                wgs = world.to_file(path_toshp, driver='ESRI Shapefile')
        except Exception as e:
            raise Exception('Error saving data to SHP')
        print('Successfully converted : %s' % (path_toshp))


def __init__():
    # enable KML support which is disabled by default
    fiona.drvsupport.supported_drivers['kml'] = 'rw'
    # enable KML support which is disabled by default
    fiona.drvsupport.supported_drivers['KML'] = 'rw'
