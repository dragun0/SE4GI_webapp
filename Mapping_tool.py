# -*- coding: utf-8 -*-
"""
Created on Sun May 30 19:28:19 2021

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
from bokeh.embed import *
from bokeh.resources import CDN




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

def make_plot():
    lagos_gdf = Load_Lagos_gdf().to_crs(epsg=3857) 
    lagos_gdf['x'] = lagos_gdf.apply(getPointCoords, geom='geometry', coord_type='x', axis=1)
    lagos_gdf['y'] = lagos_gdf.apply(getPointCoords, geom='geometry', coord_type='y', axis=1)
    
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

    #Add two more columns to the dataframe; 'Filter' and 'URL'
    #one is altered by the filter widget callbacks
    #one to display URLs on the bokeh glyphs
    lagos_df = lagos_gdf.drop('geometry', axis=1).copy()
    lagos_df['Filter'] = pd.Series(['1' for x in range(len(lagos_df.index))])
    
    pointSource = ColumnDataSource(lagos_df)
    
    
    #datapoint view is determined by a group filter, that is based on the 'Filter' Column of the ColumnDataSource (which contains either '0' or '1')
    #datapoints containing the value '1' in the 'Filter' Column are viewed
    view = CDSView(source = pointSource,
                   filters = [GroupFilter(column_name='Filter', group='1')]
                   )

    

    #create Filter widget
    OPTIONS = ['Walking',
               ('Running or jogging','Running or Jogging'),
               ('football','Football'),
               ('basketball','Basketball'),
               'Cycling',
               'Swimming',
               'Aerobics',
               ('Other activities not listed','Others')
               ]
    exerciseTypeSelectorWidget = MultiChoice(value=[], options=OPTIONS)
    
   
    
    plot = figure(
                  match_aspect=True,
                  tools='wheel_zoom,pan,reset,save',
                  x_range=(x_min, x_max),
                  y_range=(y_min, y_max),
                  x_axis_type='mercator',
                  y_axis_type='mercator',
                  width=800,
                  height=500
                  )
    
    callback = CustomJS(args=dict(plot=plot, source=pointSource),code="""
                        var data = source.data;
                        var selections = cb_obj.value
                        var selections = selections.toString().split(',');
                        var filter = data['Filter']
                        var exerciseTypes = data['7_Nature_Excercise_Perfomed_Oserved']
                        
                       
                        for (var i = 0; i < exerciseTypes.length; i++) {
                            filter[i] = '1'
                            for (var j = 0; j < selections.length; j++) {
                                if (!exerciseTypes[i].includes(selections[j])){
                                    filter[i] = '0'
                                } 
                            }
                        }
                        source.change.emit();
            """)
                        
       
    exerciseTypeSelectorWidget.js_on_change("value", callback)

    
    plot.grid.visible=False
    plot.xaxis.visible = False
    plot.yaxis.visible=False
    plot.circle_cross('x','y', source=pointSource, view=view, fill_color = 'blue', size = 10) 
    point_hover = HoverTool(tooltips=[('exercise', '@7_Nature_Excercise_Perfomed_Oserved')], mode='mouse', point_policy='follow_mouse')
    plot.tools.append(point_hover)
    
    output_file("night_sky")
    curdoc().theme = 'night_sky'
    
    tile_provider=get_provider(OSM)
    map=plot.add_tile(tile_provider)
    map.level='underlay'
    
    maplayout = row(exerciseTypeSelectorWidget, plot)
    #mapWithFilteringTool = column(widgetbox(exerciseTypeSelectorWidget), plot)
    #curdoc().add_root(row(maplayout, plot, width=800))
  
    
    
    return maplayout



@app.route('/map')
def plot(): 
    p = make_plot()
    return file_html(p, CDN)
   # script, div = components(widget)
 #   return render_template('maps.html', title = 'haaalo', script = script, div = div)
  
    

if __name__ == '__main__':
   app.run(debug=True)