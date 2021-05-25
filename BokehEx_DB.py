# -*- coding: utf-8 -*-
"""
Created on Mon May 24 19:51:13 2021

@author: daene
"""

#Importing the required packages
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure, show, output_file
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
from DBconectionEx import Load_gdf_LAGOS_DB as Load

# Loading the geodataframe from the database, assigning the WGS84 geodetic coordinate
# system (epsg=4326) and then converting it to the pseudomercator (epsg=3857)
Lagos_gdf = Load().set_crs(epsg=4326, inplace=True).to_crs(epsg=3857)

# function to extract coordinates from the geodataframe
def getPointCoords(rows, geom, coord_type):
    """Calculates coordinates ('x' or 'y') of a Point geometry"""
    if coord_type == 'x':
        return rows[geom].x
    elif coord_type == 'y':
        return rows[geom].y

Lagos_gdf['x'] = Lagos_gdf.apply(getPointCoords, geom='geometry', coord_type='x', axis=1)
Lagos_gdf['y'] = Lagos_gdf.apply(getPointCoords, geom='geometry', coord_type='y', axis=1)
# Creating a new pandas dataframe without the geometry column
Lagos_df = Lagos_gdf.drop('geometry', axis=1).copy()
#Use the dataframe as Bokeh ColumnDataSource
psource = ColumnDataSource(Lagos_df)
#Specify feature of the Hoover tool
TOOLTIPS = [
    ("Date", "@1_Date"),
    ("Title", "@title")
]

# range bounds supplied in web mercator coordinates epsg=3857
p1 = figure(x_range=(355490, 405470), y_range=(714990, 743910),
           x_axis_type="mercator", y_axis_type="mercator", tooltips=TOOLTIPS)

#Add basemap tile
p1.add_tile(get_provider(CARTODBPOSITRON))
#Add Glyphs
p1.circle('x', 'y', source=psource, color='purple', radius=20) #size=10
#Add Labels and add to the plot layout
labels = LabelSet(x='x', y='y', text='ID', level="glyph",
              x_offset=8, y_offset=8, source=psource, render_mode='css')

p1.add_layout(labels)
output_file(r"C:\Users\daene\Dropbox\POLIMI\Semestre 1\Software Engineering for Geoinformatics\Project\Lagos_map.html")
show(p1)
