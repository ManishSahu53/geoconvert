try:
    import geopandas
except:
    raise Exception('Geopandas not install. pip install geopandas')

try:
    import fiona
except:
    raise Exception('fiona not install. pip install fiona')

try:
    from shapely.geometry import Point, Polygon, MultiPolygon
except:
    raise Exception('shapely not install. pip install shapely')

try:
    import gdal
    import osr
except:
    raise Exception('gdal not install. conda install gdal')

import os
import numpy as np


class vector():
    """
    Create vector class
    """

    def __init__(self):
        path_input = None
        # enable KML support which is disabled by default
        fiona.drvsupport.supported_drivers['kml'] = 'rw'
        # enable KML support which is disabled by default
        fiona.drvsupport.supported_drivers['KML'] = 'rw'

    def check_driver(self):
        """
        Check driver is supported or not
        """
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
        """
        Initilize and read data files
        """
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
        """
        Split and save into multile geopandas data frame
        """
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

    # Creating dxfs from datafram and saving it
    def creatingdxf(self, dxf, dataframe, path_dxf):
        """
        Creating dxf from dataframe
        """
        world_point, world_line, world_polygon = self.split_geometry(dataframe)

        if len(world_point) > 0:
            dxf.layers.append(sdxf.Layer(
                name="PointLayer", color=1))
            dxf.layers.append(sdxf.Layer(
                name="PointNameLayer", color=7))
            # Extracting points data
            for i in range(len(world_point)):
                location = (
                    list(world_point.geometry)[i].x, list(world_point.geometry)[i].y)
                # Saving text layer
                dxf.append(
                    sdxf.Text(str(list(world_point.Name)[i]), point=location, layer="PointNameLayer"))

                # Saving to point layer
                dxf.append(sdxf.Point(
                    points=location, layer="PointLayer"))

        if len(world_line) > 0:
            dxf.layers.append(sdxf.Layer(
                name="LineLayer", color=1))
            dxf.layers.append(sdxf.Layer(
                name="LineNameLayer", color=7))
            # Extracting points data
            for i in range(len(world_line)):
                centroid_location = (list(world_line.geometry)[i].centroid.x, list(
                    world_line.geometry)[i].centroid.y)

                line_location = list(world_line.geometry)[i].xy
                location = []
                for j in range(len(line_location[0])):
                    location.append(
                        (line_location[0][j], line_location[1][j]))

                # Creating text layer at centroid of line
                dxf.append(sdxf.Text(str(list(world_line.Name)[
                           i]), point=centroid_location, layer="LineNameLayer"))

                # Creating line layer
                dxf.append(sdxf.LwPolyLine(
                    points=location, layer="LineLayer", flag=1))

        if len(world_polygon) > 0:
            dxf.layers.append(sdxf.Layer(
                name="PolygonLayer", color=1))
            dxf.layers.append(sdxf.Layer(
                name="PolygonNameLayer", color=7))
            # Extracting points data
            for i in range(len(world_polygon)):
                centroid_location = (list(world_polygon.geometry)[i].centroid.x, list(
                    world_polygon.geometry)[i].centroid.y)
                line_location = list(world_polygon.geometry)[i].xy
                location = []
                for j in range(len(line_location[0])):
                    location.append(
                        (line_location[0][j], line_location[1][j]))

                # Creating text layer at centroid of line
                dxf.append(sdxf.Text(str(list(world_polygon.Name)[
                           i]), point=centroid_location, layer="PolygonNameLayer"))

                # Creating line layer
                dxf.append(sdxf.LwPolyLine(
                    points=location, layer="PolygonLayer", flag=1))

         # Saving to file
        dxf.saveas(path_dxf)

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
                    if len(world_point) > 0:
                        world_point.to_file(path_towgs_point, driver=driver)
                    if len(world_line) > 0:
                        world_line.to_file(path_towgs_line, driver=driver)
                    if len(world_polygon) > 0:
                        world_polygon.to_file(
                            path_towgs_polygon, driver=driver)

                else:
                    path_towgs_point = os.path.splitext(self.path_input)[
                        0] + '_wgs_point.' + self.extention
                    path_towgs_line = os.path.splitext(self.path_input)[
                        0] + '_wgs_line.' + self.extention
                    path_towgs_polygon = os.path.splitext(
                        self.path_input)[0] + '_wgs_polygon.' + self.extention

                    # Saving to point, line, polygon
                    if len(world_point) > 0:
                        world_point.to_file(path_towgs_point, driver=driver)
                    if len(world_line) > 0:
                        world_line.to_file(path_towgs_line, driver=driver)
                    if len(world_polygon) > 0:
                        world_polygon.to_file(
                            path_towgs_polygon, driver=driver)

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
                world=world, path=path_togeojson, driver=driver)
            print('Successfully converted : %s' % (path_togeojson))

    def toshp(self, epsg=4326, path_toshp=None):
        """
        Converts data to shp format
        """
        print('converting to shp')
        driver = 'ESRI Shapefile'

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
            raise Exception('Error: Converting polygon to multipolygon')

        # Saving data to disk
        if self.ismultigeometry == False:
            try:
                if path_toshp is not None:
                    world.to_file(path_toshp, driver=driver)
                else:
                    path_toshp = os.path.splitext(self.path_input)[0] + '.shp'
                    world.to_file(path_toshp, driver=driver)
            except Exception as e:
                raise Exception('Error saving data to SHP')
            print('Successfully converted : %s' % (path_toshp))
        else:
            path_toshp = os.path.splitext(self.path_input)[0] + '.shp'
            self.splitandsave(
                world=world, path=path_toshp, driver=driver)
            print('Successfully converted : %s' % (path_toshp))

    # def todxf(self, path_todxf=None):
    #     """
    #     Converts data to dxf format
    #     """
    #     print('converting to dxf')

    #     # Creating dxf dataset
    #     dxf = sdxf.Drawing()
    #     world = self.df

    #     # Converting polygon to multipolygons
    #     try:
    #         world["geometry"] = [MultiPolygon([feature]) if type(
    #             feature) == Polygon else feature for feature in world["geometry"]]
    #     except Exception as e:
    #         raise Exception('Erro transforming polygon to multipolygon')

    #     # Saving data to disk
    #     if self.ismultigeometry == False:
    #         try:
    #             if path_todxf is not None:
    #                 try:
    #                     self.creatingdxf(dxf=dxf, dataframe=world,
    #                                     path_dxf=path_todxf)
    #                 except Exception as e:
    #                     raise Exception('Error: Unable to convert dataframe to dxf')

    #             else:
    #                 path_todxf = os.path.splitext(self.path_input)[0] + '.dxf'
    #                 try:
    #                     self.creatingdxf(dxf=dxf, dataframe=world,
    #                                     path_dxf=path_todxf)
    #                 except Exception as e:
    #                     raise Exception('Error: Unable to convert dataframe to dxf')

    #         except Exception as e:
    #             raise Exception('Error saving data to DXF')
    #         print('Successfully converted : %s' % (path_todxf))

    #     else:
    #         path_todxf = os.path.splitext(self.path_input)[0] + '.dxf'
    #         try:
    #             self.creatingdxf(dxf=dxf, dataframe=world,
    #                             path_dxf=path_todxf)
    #         except Exception as e:
    #             raise Exception('Error: Unable to convert dataframe to dxf')

    #         print('Successfully converted : %s' % (path_todxf))

    def todxf(self, epsg=None, path_todxf=None):
        """
        Converts data to shp format
        """
        print('converting to dxf')
        driver = 'DXF'

        # Converting to coordinate system
        if epsg is not None:
            try:
                world = self.df.to_crs({'init': 'epsg:%s' % (epsg)})
            except Exception as e:
                raise Exception('Error converting to epsg:%s' % (epsg))
        else:
            world = self.df

        # Converting polygon to multipolygons
        print('poly to multi poly')
        try:
            world["geometry"] = [MultiPolygon([feature]) if type(
                feature) == Polygon else feature for feature in world["geometry"]]
        except Exception as e:
            raise Exception('Error: Converting polygon to multipolygon')

        # Since dxf doesn't support attributes, we are removing all columns except gemerty
        columns = list(world.columns)

        for k in range(len(columns)):
            if columns[k].upper() == 'geometry'.upper():
                continue
            else:
                del world[columns[k]]

        # Saving data to disk
        if self.ismultigeometry == False:
            try:
                if path_todxf is not None:
                    world.to_file(path_todxf, driver=driver)
                else:
                    path_todxf = os.path.splitext(self.path_input)[0] + '.dxf'
                    world.to_file(path_todxf, driver=driver)
            except Exception as e:
                raise Exception('Error saving data to DXF')
            print('Successfully converted : %s' % (path_todxf))
        else:
            path_todxf = os.path.splitext(self.path_input)[0] + '.dxf'
            self.splitandsave(
                world=world, path=path_todxf, driver=driver)
            print('Successfully converted : %s' % (path_todxf))


# Raster class
class raster():
    """
    Create raster class
    """

    def __init__(self):
        self.intermediate_format = 'VRT'
        self.path_input = None
        self.path_output = None

    def config(self):
        # Reading dataset
        self.ds = gdal.Open(self.path_input, 1)
        if self.ds is None:
            raise Exception(
                'Input file provided %s cannot be loaded' % (self.path_input))

        # Reading Nodata value
        self.no_data = self.ds.GetRasterBand(1).GetNoDataValue()
        if self.no_data is None:
            self.no_data = -9999

        # Reading compression type
        try:
            self.compression = self.ds.GetMetadata(
                'IMAGE_STRUCTURE')['COMPRESSION']
        except:
            self.compression = 'LZW'

        if self.compression.upper() == 'YCbCr JPEG'.upper():
            self.compression = 'JPEG'

        # Reading number of bands
        self.num_band = self.ds.RasterCount

        # Defining dtype
        self.dtype = self.ds.ReadAsArray(0, 0, 1, 1).dtype

        # Dimensions
        self.col = self.ds.RasterXSize
        self.row = self.ds.RasterYSize

        # Tranformation settings
        self.geotransform = self.ds.GetGeoTransform()

        # Projections
        self.geoprojection = self.ds.GetProjection()

        # Check for pyramids and overviews, 0 if no overviews
        self.overview = self.ds.GetRasterBand(1).GetOverviewCount()

    # Get dtype types supported in GDAL
    def dtype_conversion(self):
        """
        GDT_Byte 	    Eight bit unsigned integer
        GDT_UInt16 	    Sixteen bit unsigned integer
        GDT_Int16 	    Sixteen bit signed integer
        GDT_UInt32 	    Thirty two bit unsigned integer
        GDT_Int32 	    Thirty two bit signed integer
        GDT_Float32 	Thirty two bit floating point
        GDT_Float64 	Sixty four bit floating point
        """
        # Float 64
        if self.dtype == np.dtype(np.float64):
            output_dtype = gdal.GDT_Float64
            return output_dtype
        # Float 32
        elif self.dtype == np.dtype(np.float32):
            output_dtype = gdal.GDT_Float32
            return output_dtype
        # Uint 8
        elif self.dtype == np.dtype(np.uint8):
            output_dtype = gdal.GDT_Byte
            return output_dtype
        # Uint 16
        elif self.dtype == np.dtype(np.uint16):
            output_dtype = gdal.GDT_UInt16
            return output_dtype
        # Unit 32
        elif self.dtype == np.dtype(np.uint32):
            output_dtype = gdal.GDT_UInt32
            return output_dtype
        # Int 16
        elif self.dtype == np.dtype(np.int16):
            output_dtype = gdal.GDT_Int16
            return output_dtype
        # Int 32
        elif self.dtype == np.dtype(np.int32):
            output_dtype = gdal.GDT_Int32
            return output_dtype
        else:
            return gdal.GDT_Float32

    # Create pyramids
    def gdal_addo(self):
        """
        Generate pyramid of raster class
        """
        # 0 = read-only, 1 = read-write.
        if self.overview == 0:
            gdal.SetConfigOption('COMPRESS_OVERVIEW', 'LZW')
            self.ds.BuildOverviews("NEAREST", [2, 4, 8, 16, 32, 64])
            print('Completed: Generating overviews')
        else:
            print('Overviews already generated. Thus skipping!')

    # WKT to EPSG
    def wkt2epsg(self, wkt):
        """
        From https://gis.stackexchange.com/questions/20298/is-it-possible-to-get-the-epsg-value-from-an-osr-spatialreference-class-using-th
        Transform a WKT string to an EPSG code

        Arguments
        ---------

        wkt: WKT definition

        Returns: EPSG code
        """
        p_in = osr.SpatialReference()
        s = p_in.ImportFromWkt(wkt)
        if s == 5:  # invalid WKT
            return None
        if p_in.IsLocal() == 1:  # this is a local definition
            return p_in.ExportToWkt()
        if p_in.IsGeographic() == 1:  # this is a geographic srs
            cstype = 'GEOGCS'
        else:  # this is a projected srs
            cstype = 'PROJCS'
        an = p_in.GetAuthorityName(cstype)
        ac = p_in.GetAuthorityCode(cstype)
        if an is not None and ac is not None:  # return the EPSG code
            return int(p_in.GetAuthorityCode(cstype))

    # Get EPSG code from raster
    def get_EPSG(self):
        """
        Returns the EPSG code from a given input georeferenced image or virtual
        raster gdal object.
        """
        wkt = self.geoprojection
        epsg = self.wkt2epsg(wkt)

        return epsg

    # Remapping array
    def remap_array(self, arr):
        """
        Remapping [3, 256,256] to [256,256,3]
        """
        return np.moveaxis(arr, 0, 2)


    def reproj(self, epsg=4326, path_totif=None):
        """
        Reproject raster to specified epsg code
        """
        try:
            epsg_code = self.get_EPSG()
        except Exception as e:
            raise Exception('Unable to get EPSG code. Make sure data is geo-referenced')

        print('EPSG projeciton code of raster dataset: %d'%(epsg_code))
        dst_proj = 'EPSG:%s'%(str(epsg))

        intermediate_format = 'Gtiff'
        print('Reprojecting data to EPSG:%s'%(epsg))

        if path_totif is None:
            path_totif = os.path.splitext(self.path_input)[0] + '_reproj.' + os.path.splitext(self.path_input)[1]

        try:
            dst_ds = gdal.Warp(path_totif, 
                               self.path_input, 
                               dstSRS=dst_proj,
                               format=intermediate_format,
                               creationOptions=['compress=%s'%(self.compression)])
            
        except Exception as e:
            raise Exception('Error: Reprojecting dataset')

        dst_ds.FlushCache()
        dst_ds= None
        print('Successfully converted : %s' % (path_totif))

    def toimg(self, epsg=None, path_toimg=None):
        #Open output format driver, see gdal_translate --formats for list
        format = "HFA"
        driver = gdal.GetDriverByName( format )
        print('Compression is %s'%(self.compression))

        if driver is None:
            raise Exception('Error: IMG file format is not supported')
        
        if path_toimg is None:
            path_toimg = os.path.splitext(self.path_input)[0] + '.img'
        
        if epsg is not None:
            # Converting to different epsg code
            dst_proj = 'EPSG:%s'%(str(epsg))
            print('Reprojecting data to EPSG:%s'%(epsg))

            try:
                ds = gdal.Warp('', 
                                self.path_input, 
                                dstSRS=dst_proj,
                                format='VRT')
            except Exception as e:
                raise Exception('Error: Unable to reproject dataset to %s'%(dst_proj))
            
            #Output to new format
            try:
                dst_ds = driver.CreateCopy(path_toimg, ds, 0,
                                            ['NUM_THREADS=ALL_CPUS',
                                            'COMPRESS=%s' % (self.compression)] )
            except Exception as e:
                raise Exception('Error: Converting data to IMG')

        else:
            #Output to new format
            try:
                dst_ds = driver.CreateCopy(path_toimg, self.ds, 0,
                                            ['NUM_THREADS=ALL_CPUS',
                                            'COMPRESS=%s' % (self.compression)] )
            except Exception as e:
                raise Exception('Error: Converting data to IMG')
        
        print('Successfully converted : %s' % (path_toimg))


def __init__():
    # enable KML support which is disabled by default
    fiona.drvsupport.supported_drivers['kml'] = 'rw'
    # enable KML support which is disabled by default
    fiona.drvsupport.supported_drivers['KML'] = 'rw'
