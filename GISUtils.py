'''
Geosyntec written tools to perform mundane, tedious tasks for ArcGIS MXDs.
Contributors:
Jeffrey Munowitch, Oakland (jmunowitch@geosyntec.com)
Paul Hobson, Portland (phobson@geosyntec.com)
R. Dylan Walker, Columbia, MD (rwalker@geosyntec.com)
'''

try: 
    import arcpy.mapping as mapping    
except ImportError:
    print "Error: Can not import ArcPy. Make sure you have ArcGIS Installed."
    temp = raw_input("Press enter to exit.")
