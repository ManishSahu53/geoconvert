# geoconvert
## Introduction
It is used to convert vector files like Shp, KML, GeoJson to one another.

## Class
1. Vector

    ### Methods
    1. vector.towgs(path_towgs)
    
        Saves vector of any coordinate system to WGS coordinates on the given path
        
        [Default] - 'Filename_wgs.format'

    2. vector.tokml(path_tokml)

        Saves vector files to KML format. KML is always stored as WGS 84 Geographic coordinate system.
        
        [Default] 
        1. path_tokml = 'Filename.kml'

    3. vector.toshp(epsg, path_toshp)


        Saves vector files to shp format in the provided epsg code to given path.
        
        [Default] - 
        1. path_toshp = 'Filename.shp'
        2. epsg = 4326

    4. vector.togeojson(epsg, path_togeojson)

        Saves vector files to KML format. KML is always stored as WGS 84 Geographic coordinate system.
        
        [Default] - 
        1. path_togeojson = 'Filename.json'
        2. epsg = 4326