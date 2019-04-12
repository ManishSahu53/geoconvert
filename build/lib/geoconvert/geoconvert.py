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

        # Check for multi geometry type class
        point = max(list(self.df.geom_type == 'Point'))
        line = max(list(self.df.geom_type == 'LineString'))
        polygon = max(list(self.df.geom_type == 'MultiPolygon'))

        if point + line + polygon > 1:
            self.ismultigeometry = True
        else:
            self.ismultigeometry = False

    # Spliting single dataframe into multiple dataframe according to point, line, polygon
    def split_geometry(self, dataframe):
        """
        Splits dataframe into point, line, polygon parts
        """
        df_point = dataframe[dataframe.geom_type == 'Point']
        df_line = dataframe[dataframe.geom_type == 'LineString']
        df_polygon = dataframe[dataframe.geom_type == 'MultiPolygon']
        return df_point, df_line, df_polygon

    # If multigeometry then split and save to disk
    def splitandsave(self, world, driver, path=None):
        world_point, world_line, world_polygon = self.split_geometry(world)
        print('Extracted %d points, %d lines, %d polygons' %
              (len(world_point), len(world_line), len(world_polygon)))
        try:
            if path is not None:
                path_point = os.path.splitext(
                    path)[0] + '_point' + os.path.splitext(path)[1]
                path_line = os.path.splitext(
                    path)[0] + '_line' + os.path.splitext(path)[1]
                path_polygon = os.path.splitext(
                    path)[0] + '_polygon' + os.path.splitext(path)[1]

                # Saving to point line polygon
                if len(world_point) > 0:
                    world_point.to_file(path_point, driver=driver)
                if len(world_line) > 0:
                    world_line.to_file(path_line, driver=driver)
                if len(world_polygon) > 0:
                    world_polygon.to_file(path_polygon, driver=driver)
                else:
                    raise Exception(
                        'Unable to split dataframe into multi geometry types')

            else:
                path_point = os.path.splitext(self.path_input)[
                    0] + '_point'
                path_line = os.path.splitext(self.path_input)[
                    0] + '_line'
                path_polygon = os.path.splitext(self.path_input)[
                    0] + '_polygon'

                # Saving to point line polygon
                if len(world_point) > 0:
                    world_point.to_file(path_point, driver=driver)
                elif len(world_line) > 0:
                    world_line.to_file(path_line, driver=driver)
                elif len(world_polygon) > 0:
                    world_polygon.to_file(path_polygon, driver=driver)

        except Exception as e:
            raise Exception('Error saving data to disk')

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
                'Error converting to epsg:%d coordinate system ' % ('4326'))

        # Converting polygon to multipolygons
        try:
            world["geometry"] = [MultiPolygon([feature]) if type(
                feature) == Polygon else feature for feature in world["geometry"]]
        except Exception as e:
            raise Exception('Error transforming polygon tol multipolygon')

        # Saving data to disk if single type of geometry type
        if self.ismultigeometry is False:
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

        else:
            world_point, world_line, world_polygon = self.split_geometry(world)
            print('Extracted %d points, %d lines, %d polygons' %
              (len(world_point), len(world_line), len(world_polygon)))
            try:
                if path_towgs is not None:
                    path_towgs_point = os.path.splitext(
                        path_towgs)[0] + '_point' + os.path.splitext(path_towgs)[1]
                    path_towgs_line = os.path.splitext(
                        path_towgs)[0] + '_line' + os.path.splitext(path_towgs)[1]
                    path_towgs_polygon = os.path.splitext(
                        path_towgs)[0] + '_polygon' + os.path.splitext(path_towgs)[1]

                    # Saving to point, line, polygon
                    if len(world_point)>0:
                        world_point.to_file(path_towgs_point, driver=driver)
                    if len(world_line)>0:
                        world_line.to_file(path_towgs_line, driver=driver)
                    if len(world_polygon)>0:
                        world_polygon.to_file(path_towgs_polygon, driver=driver)

                else:
                    path_towgs_point = os.path.splitext(self.path_input)[
                        0] + '_wgs_point.' + self.extention
                    path_towgs_line = os.path.splitext(self.path_input)[
                        0] + '_wgs_line.' + self.extention
                    path_towgs_polygon = os.path.splitext(
                        self.path_input)[0] + '_wgs_polygon.' + self.extention

                    # Saving to point, line, polygon
                    if len(world_point)>0:
                        world_point.to_file(path_towgs_point, driver=driver)
                    if len(world_line)>0:
                        world_line.to_file(path_towgs_line, driver=driver)
                    if len(world_polygon)>0:
                        world_polygon.to_file(path_towgs_polygon, driver=driver)

            except Exception as e:
                raise Exception('Error saving data to WGS')

    def tokml(self, path_tokml=None):
        """
        Converts data to KML format to epsg 4326
        """
        print('converting to KML')
        driver = 'KML'

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
        if self.ismultigeometry == False:
            try:
                if path_tokml is not None:
                    world.to_file(path_tokml, driver=driver)
                else:
                    path_tokml = os.path.splitext(self.path_input)[0] + '.kml'
                    world.to_file(path_tokml, driver=driver)
            except Exception as e:
                raise Exception('Error saving data to KML')
            print('Successfully converted : %s' % (path_tokml))

        else:
            path_tokml = os.path.splitext(self.path_input)[0] + '.kml'
            self.splitandsave(world=world, path=path_tokml, driver=driver)
            print('Successfully converted : %s' % (path_tokml))

    def togeojson(self, epsg=4326, path_togeojson=None):
        """
        Converts data to geojson format to specifi epsg code
        """
        print('converting to geojson')
        driver = 'GeoJSON'

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
        if self.ismultigeometry == False:
            try:
                if path_togeojson is not None:
                    world.to_file(path_togeojson, driver=driver)
                else:
                    path_togeojson = os.path.splitext(
                        self.path_input)[0] + '.geojson'
                    world.to_file(path_togeojson, driver=driver)
            except Exception as e:
                raise Exception('Error saving data to geojson')
            print('Successfully converted : %s' % (path_togeojson))
        else:
            path_togeojson = os.path.splitext(self.path_input)[0] + '.geojson'
            self.splitandsave(
                world = world, path = path_togeojson, driver = driver)
            print('Successfully converted : %s' % (path_togeojson))

    def toshp(self, epsg = 4326, path_toshp = None):
        """
        Converts data to shp format
        """
        print('converting to shp')
        driver='ESRI Shapefile'

        # Converting to coordinate system
        try:
            world=self.df.to_crs({'init': 'epsg:%s' % (epsg)})
        except Exception as e:
            raise Exception('Error converting to epsg:%s' % (epsg))

        # Converting polygon to multipolygons
        print('poly to multi poly')
        try:
            world["geometry"]=[MultiPolygon([feature]) if type(
                feature) == Polygon else feature for feature in world["geometry"]]
        except Exception as e:
            raise Exception('Error: Converting polygon to multipolygon')

        # Saving data to disk
        if self.ismultigeometry == False:
            try:
                if path_toshp is not None:
                    world.to_file(path_toshp, driver = driver)
                else:
                    path_toshp=os.path.splitext(self.path_input)[0] + '.shp'
                    world.to_file(path_toshp, driver = driver)
            except Exception as e:
                raise Exception('Error saving data to SHP')
            print('Successfully converted : %s' % (path_toshp))
        else:
            path_toshp=os.path.splitext(self.path_input)[0] + '.shp'
            self.splitandsave(
                world = world, path = path_toshp, driver = driver)
            print('Successfully converted : %s' % (path_toshp))


def __init__():
    # enable KML support which is disabled by default
    fiona.drvsupport.supported_drivers['kml']='rw'
    # enable KML support which is disabled by default
    fiona.drvsupport.supported_drivers['KML']='rw'
