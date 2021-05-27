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
from bokeh.resources import CDN
from bokeh.embed import file_html




def Load_Lagos_gdf():
    # ---------------------- REQUEST DATA FROM SERVER SE4GI -----------------------
   engine = create_engine('postgresql://postgres:user@localhost:5432/SE4GI')
    # read the dataframe from a postgreSQL table
   data_geodf = gpd.read_postgis('Lagos ALPhA Survey', engine, geom_col='geometry')
   return data_geodf




def getPointCoords(rows, geom, coord_type):
    """Calculates coordinates ('x' or 'y') of a Point geometry"""
    if coord_type == 'x':
        return rows[geom].x
    elif coord_type == 'y':
        return rows[geom].y


lagos_gdf = Load_Lagos_gdf().to_crs(epsg=3857) 
lagos_gdf['x'] = lagos_gdf.apply(getPointCoords, geom='geometry', coord_type='x', axis=1)
lagos_gdf['y'] = lagos_gdf.apply(getPointCoords, geom='geometry', coord_type='y', axis=1)



lagos_df = lagos_gdf.drop('geometry', axis=1).copy()



pointSource = ColumnDataSource(lagos_df)


scale = 2000
x = lagos_gdf['x']
y = lagos_gdf['y']



x_min=int(x.mean() - (scale * 350))
x_max=int(x.mean() + (scale * 350))
y_min=int(y.mean() - (scale * 350))
y_max=int(y.mean() + (scale * 350))


app = Flask(__name__)


def make_plot():
    plot = figure(title='ALPhA test',
                  match_aspect=True,
                  tools='wheel_zoom,pan,reset,save',
                  x_range=(x_min, x_max),
                  y_range=(y_min, y_max),
                  x_axis_type='mercator',
                  y_axis_type='mercator',
                  width=500
                  )
    plot.grid.visible=True
    plot.xaxis.visible = False
    plot.yaxis.visible=False
    plot.title.text_font_size="20px"
    plot.circle('x','y', source=pointSource, color = 'blue', size = 10)
    point_hover = HoverTool(tooltips=[('nickname', '@18b_ALPhA_Name')], mode='mouse', point_policy='follow_mouse')
    plot.tools.append(point_hover)
    
    tile_provider=get_provider(OSM)
    map=plot.add_tile(tile_provider)
    map.level='underlay'
    return plot





@app.route('/map')
def plot(): 
    p = make_plot()
   # return file_html(p, CDN, "blabal")
    return file_html(p, CDN, "zzz", "plots.html")
  
    

    

if __name__ == '__main__':
   app.run(debug=True)