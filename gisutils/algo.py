from gisutils import raster

def average_slope(df, dem, dem_aff):
    """
    Computes the average slope between the first and last coordinates of 
    a line using the elevations from a reference Digital Elevation Map.

    Output DataFrame has new column `average_slope` containing the result
    of the slope calculation (float).

    Parameters
    ----------
    df : pandas.DataFrame
    dem : array
    dem_aff : affine.Affine
    
    
    Returns
    -------
    pandas.DataFrame
    
    """
    
    df = df.copy() #this may not be necessary since the function has it's own namespace
    
    for row in df.itertuples():
        length = row.geometry.length
        first_pt = row.geometry.coords[0]
        last_pt = row.geometry.coords[-1]
        ix = row.Index

        r1, c1 = raster.xy_to_rowcol(*first_pt, affine = dem_aff)
        elev1 = dem[r1,c1][0]
        
        r2, c2 = raster.xy_to_rowcol(*last_pt, affine = dem_aff)
        elev2 = dem[r2,c2][0]

        delta_elev = elev2 - elev1
        avg_slope = delta_elev / length

        df.loc[df.index[ix],'average_slope'] = avg_slope

    return df
