from gisutils import raster

def average_slope(gdf, dem, dem_affine):
    """
    Computes the average slope between the first and last coordinates of 
    a line using the elevations from a reference Digital Elevation Map.

    Output DataFrame has new column `average_slope` containing the result
    of the slope calculation (float).

    Parameters
    ----------
    gdf : GeoDataFrame
    dem : array
    dem_affine : affine.Affine
    
    
    Returns
    -------
    pandas.DataFrame
    
    """
    
    length = gdf['geometry'].length
    x1 = gdf['geometry'].apply(lambda g: g.coords[0][0])
    y1 = gdf['geometry'].apply(lambda g: g.coords[0][1])

    x2 = gdf['geometry'].apply(lambda g: g.coords[-1][0])
    y2 = gdf['geometry'].apply(lambda g: g.coords[-1][1])
    
    r1, c1 = raster.xy_to_rowcol(x1, y1, dem_affine)
    z1 = dem[r1,c1]
    
    r2, c2 = raster.xy_to_rowcol(x2, y2, dem_affine)
    z2 = dem[r2,c2]
    

    slope = (z2 - z1)/ length
    return gdf.assign(avg_slope=slope)