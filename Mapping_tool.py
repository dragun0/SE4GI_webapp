# -*- coding: utf-8 -*-
"""
Created on Thu May 27 10:47:46 2021

@author: leoni
"""

from flask import (Flask, render_template, request)
import pandas as pd
import geopandas as gpd
import numpy as np
from sqlalchemy import create_engine
from bokeh.models import *
from bokeh.plotting import * 
from bokeh.io import *
from bokeh.tile_providers import *
from bokeh.palettes import *
from bokeh.transform import *
from bokeh.layouts import *
from bokeh.models.widgets import *
from bokeh.embed import components




def Load_Lagos_gdf():
   engine = create_engine('postgresql://postgres:user@localhost:5432/SE4GI')
   data_geodf = gpd.read_postgis('Lagos ALPhA Survey', engine, geom_col='geometry')
   return data_geodf



def getPointCoords(rows, geom, coord_type):
    """Calculates coordinates ('x' or 'y') of a Point geometry"""
    if coord_type == 'x':
        return rows[geom].x
    elif coord_type == 'y':
        return rows[geom].y



app = Flask(__name__)


def make_plot(FilteredExercise):
    lagos_gdf = Load_Lagos_gdf().to_crs(epsg=3857) 
    lagos_gdf['x'] = lagos_gdf.apply(getPointCoords, geom='geometry', coord_type='x', axis=1)
    lagos_gdf['y'] = lagos_gdf.apply(getPointCoords, geom='geometry', coord_type='y', axis=1)
    lagos_df = lagos_gdf.drop('geometry', axis=1).copy()
    
    #sets the zoom scale for the map
    scale = 400
    x = lagos_gdf['x']
    y = lagos_gdf['y']
    #The range for the map extents is derived from the lat/lon fields. 
    #This way the map is automatically centered on the plot elements.
    x_min=int(x.mean() - (scale * 350))
    x_max=int(x.mean() + (scale * 350))
    y_min=int(y.mean() - (scale * 350))
    y_max=int(y.mean() + (scale * 350))

    pointSource = ColumnDataSource(lagos_df)
    

    booleans = [True if FilteredExercise in ExerciseTypes else False for ExerciseTypes in pointSource.data['7_Nature_Excercise_Perfomed_Oserved']]
    myBooleanFilter = BooleanFilter(booleans)
    
    view = CDSView(source = pointSource,
                   filters = [myBooleanFilter]
                   )
    
   
    plot = figure(
                  match_aspect=True,
                  tools='wheel_zoom,pan,reset,save',
                  x_range=(x_min, x_max),
                  y_range=(y_min, y_max),
                  x_axis_type='mercator',
                  y_axis_type='mercator',
                  width=500,
                  height=500
                  )
    
    plot.grid.visible=False
    plot.xaxis.visible = False
    plot.yaxis.visible=False
    plot.circle('x','y', source=pointSource, view=view, color = 'red', size = 10)
    point_hover = HoverTool(tooltips=[('exercise', '@7_Nature_Excercise_Perfomed_Oserved')], mode='mouse', point_policy='follow_mouse')
    plot.tools.append(point_hover)
    output_file("night_sky")
    curdoc().theme = 'night_sky'
    
    
    
    tile_provider=get_provider(OSM)
    map=plot.add_tile(tile_provider)
    map.level='underlay'
    
    
    return plot




@app.route('/map')
def plot(): 
    p = make_plot("")
    script, div = components(p)
    return render_template('maps.html', title = 'haaalo', script = script, div = div)
  
    

if __name__ == '__main__':
   app.run(debug=True)