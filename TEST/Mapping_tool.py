# -*- coding: utf-8 -*-
"""
Created on Sun May 30 19:28:19 2021

@author: leoni
"""


import pandas as pd

from bokeh.models import *
from bokeh.plotting import * 
from bokeh.io import *
from bokeh.palettes import *
from bokeh.transform import *
from bokeh.layouts import *
from bokeh.models.widgets import *
from bokeh.embed import *
from bokeh.tile_providers import get_provider, OSM
from Synchronizer import  Load_gdf_LAGOS_DB





def getPointCoords(rows, geom, coord_type):
    """Calculates coordinates ('x' or 'y') of a Point geometry"""
    if coord_type == 'x':
        return rows[geom].x
    elif coord_type == 'y':
        return rows[geom].y


#'value's for a CheckboxButtonGroup are called 'active's. carry a value of either 0 (Increased safety) or 1 (Decreased safety)
def createSafetyCallbackCode():
    return """
                    var data = source.data;
                    var selection = cb_obj.active.toString();
                    var filter = data['SafetyFilter']
                    var safetyRiskEvaluation = data['14a_Option_Safety_Perception']
                    
                    if (selection == '0') {
                        selection = 'INCREASE'
                    } 
                    
                    if (selection == '1') {
                        selection = 'DECREASE'
                    }
                    
                    if (selection == '0,1' || selection == '1,0') {
                        selection = 'INCREASE AND DECREASE'
                    }
                   
                    for (var i = 0; i < safetyRiskEvaluation.length; i++) {
                        if (selection == ''){
                            filter[i] = '1'
                        } else {
                            if (safetyRiskEvaluation[i].includes(selection)) {
                                filter[i] = '1'
                            } else {
                                filter[i] = '0'
                            }
                        }
                      
                    }
                   
                    source.change.emit();
            """


def createExerciseTypesCallbackCode():
    return """
                       
                        var data = source.data;
                        var selections = cb_obj.value
                        var selections = selections.toString().split(',');
                        var filter = data['ExerciseFilter']
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
            """


#'value's for a CheckboxButtonGroup are called 'active's. carry a value of either 0 (Increased safety) or 1 (Decreased safety)
def createHealthCallbackCode():
    return"""
                    var data = source.data;
                    var selection = cb_obj.active.toString();
                    var filter = data['HealthFilter']
                    var healthRiskEvaluation = data['13a_Option_Risk_Injury_Disease']
                 
                    if (selection == '0') {
                        selection = 'INCREASE'
                    } 
                    
                    if (selection == '1') {
                        selection = 'DECREASE'
                    }
                    
                    if (selection == '0,1' || selection == '1,0') {
                        selection = 'INCREASE AND DECREASE'
                    }
                   
                    for (var i = 0; i < healthRiskEvaluation.length; i++) {
                        if (selection == ''){
                            filter[i] = '1'
                        } else {
                            if (healthRiskEvaluation[i].includes(selection)) {
                                filter[i] = '1'
                            } else {
                                filter[i] = '0'
                            }
                        }
                      
                    }
                   
                    source.change.emit();
            """


def createOrganisationCallbackCode() :
    return"""
                    var data = source.data;
                    var selection = cb_obj.active.toString();
                    var filter = data['OrganisationFilter']
                    var LogisticsInfo = data['9_How_Exercise_Organized']
                    
                    if (selection == '0') {
                        selection = 'Organised'
                    } 
                    
                    if (selection == '1') {
                        selection = 'Spontaneous'
                    }
                    
                    
                    for (var i = 0; i < LogisticsInfo.length; i++) {
                        if (selection == '' || selection == '0,1' || selection == '1,0'){
                            filter[i] = '1'
                        } else {
                            if (LogisticsInfo[i].includes(selection)) {
                                filter[i] = '1'
                            } else {
                                filter[i] = '0'
                            }
                        }
                      
                    }
                   
                    source.change.emit();
           
            """ 

def createCovidLockdownCallbackCode():
    return"""
                    var data = source.data;
                    var selection = cb_obj.active.toString();
                    var filter = data['CovidLockdownFilter']
                    var CovidInfo = data['11_Exercise_Ocurring_In_Lockdown']
                    
                    if (selection == '0') {
                        selection = 'Yes'
                    } 
                    
                    if (selection == '1') {
                        selection = 'No'
                    }
                    
                 
                    for (var i = 0; i < CovidInfo.length; i++) {
                        if (selection == '' || selection == '0,1' || selection == '1,0'){
                            filter[i] = '1'
                        } else {
                            if (CovidInfo[i].includes(selection)) {
                                filter[i] = '1'
                            } else {
                                filter[i] = '0'
                            }
                        }
                      
                    }
                   
                    source.change.emit();
           
            """ 




def make_plot():
    
    
    lagos_gdf = Load_gdf_LAGOS_DB().to_crs(epsg=3857)
    lagos_gdf['x'] = lagos_gdf.apply(getPointCoords, geom='geometry', coord_type='x', axis=1)
    lagos_gdf['y'] = lagos_gdf.apply(getPointCoords, geom='geometry', coord_type='y', axis=1)
    
    #sets the zoom scale for the map
    scale = 200
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
    lagos_df['ExerciseFilter'] = pd.Series(['1' for x in range(len(lagos_df.index))])
    lagos_df['SafetyFilter'] = pd.Series(['1' for x in range(len(lagos_df.index))])
    lagos_df['HealthFilter'] = pd.Series(['1' for x in range(len(lagos_df.index))])
    lagos_df['OrganisationFilter'] = pd.Series(['1' for x in range(len(lagos_df.index))])
    lagos_df['CovidLockdownFilter'] = pd.Series(['1' for x in range(len(lagos_df.index))])
    
    pointSource = ColumnDataSource(lagos_df)
    
    
    #datapoint view is determined by a group filter, that is based on the 'Filter' Column of the ColumnDataSource (which contains either '0' or '1')
    #datapoints containing the value '1' in the 'Filter' Column are viewed
    view = CDSView(source = pointSource,
                   filters = [GroupFilter(column_name='ExerciseFilter', group='1'),
                              GroupFilter(column_name='SafetyFilter', group='1'),
                              GroupFilter(column_name='HealthFilter', group='1'),
                              GroupFilter(column_name='OrganisationFilter', group='1'),
                              GroupFilter(column_name='CovidLockdownFilter', group='1')]
                   )

    plot = figure(
                  match_aspect=True,
                  tools='wheel_zoom,pan,reset,save,tap',
                  x_range=(x_min, x_max),
                  y_range=(y_min, y_max),
                  x_axis_type='mercator',
                  y_axis_type='mercator',
                  width=900,
                  height=500
                  )
    

    #create Exercise Type Filter widget
    #define 'values' and 'labes'. if only one name is defined it is used as both 'label' and 'value'
    
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
    
    #define the callback, that is executed when the user selects (a) Filter(s) 
    
    ExerciseTypecallback = CustomJS(args=dict(plot=plot, source=pointSource),code=createExerciseTypesCallbackCode())
    
    #connect the widget with the callback
    
    exerciseTypeSelectorWidget.js_on_change("value", ExerciseTypecallback)
    ExerciseExplanation1 = Div(text="""Click the box below to chose your sport!""", width=200, height=100)
    ExerciseExplanation2 = Div(text="""'Others' may include: Boxing, Weightlifting, Calisthenics, etc.""", width=200, height=100)
    ExerciseExplanation3 = Div(text="""Click an ALPhA location of your choice to find out more -->""" )
    #create Safety risk button
    #define labels for the two selection options
    #'value's for a CheckboxButtonGroup are called 'active's. carry a value of either 0 (Increased safety) or 1 (Decreased safety)
   
    SafetyLabels = ['Increased Safety', 'Decreased Safety']
    SafetyButtons = CheckboxButtonGroup(labels = SafetyLabels, active=[])
    
    SafetyCallback = CustomJS(args=dict(plot=plot, source=pointSource),code=createSafetyCallbackCode())        
    SafetyButtons.js_on_change("active", SafetyCallback)
    

   
    #create Health risk button    
    HealthLabels = ['Higher Health/Injury Risk', 'Lower Health/Injury Risk']
    HealthButtons = CheckboxButtonGroup(labels = HealthLabels, active=[])
    
    HealthCallback = CustomJS(args=dict(plot=plot, source=pointSource), code=createHealthCallbackCode())
    HealthButtons.js_on_change("active", HealthCallback)
     
    
    
    OrganisationLabels = ['Spaces that host organised group activities', 'Spaces for spontaneous individual activities']
    OrganisationButtons = CheckboxGroup(labels = OrganisationLabels, active=[])
    
    # 0 for 'organised group activities', 1 for 'spontaneous individual activity'
    OrganisationCallback = CustomJS(args=dict(plot=plot, source=pointSource), code=createOrganisationCallbackCode())
    OrganisationButtons.js_on_change("active", OrganisationCallback)
    
    
    
    CovidLockdownLabels = ['Spaces used during Covid-19 Lockdowns', 'Spaces NOT used during Covid-19 Lockdowns']
    CovidLockdownButtons = CheckboxGroup(labels=CovidLockdownLabels, active=[])

    CovidLockdownCallback = CustomJS(args=dict(plot=plot, source=pointSource), code=createCovidLockdownCallbackCode())
    CovidLockdownButtons.js_on_change("active", CovidLockdownCallback)
    
    
    
    plot.grid.visible=False
    plot.xaxis.visible = False
    plot.yaxis.visible=False
    plot.circle_cross('x','y', source=pointSource, view=view, fill_color = 'blue', size = 10)
    
    
   #location displayed in cartesian coordinates
    point_hover = HoverTool(
        tooltips="""
        <div>
            <div>
                <img
                    src="@5a2_ALPhA_Photo" height="82" alt="@5a2_ALPhA_Photo" width="82"
                    style="float: left; margin: 0px 15px 15px 0px;"
                    border="2"
                ></img>
            </div>
            <div>
                <span style="font-size: 17px; font-weight: bold;">@18b_ALPhA_Name</span>
               
            </div>
            <div>
                <span style="font-size: 15px;">Location</span>
                <span style="font-size: 10px; color: #696;">($x, $y)</span>
            </div>
        </div>
        """
    )
    
    
    plot.tools.append(point_hover)

    Taptool = plot.select(type=TapTool)
    Taptool.callback = OpenURL(url='/Portfolio?id=@ID')

 
    plot.add_tile(get_provider(OSM))
    
    
    maplayout = row(widgetbox(ExerciseExplanation1, exerciseTypeSelectorWidget, ExerciseExplanation2, SafetyButtons, HealthButtons, OrganisationButtons, CovidLockdownButtons, ExerciseExplanation3), plot)
 
    output_file("./templates/map.html")
    
    save(maplayout)
    
    return 'mapping'






