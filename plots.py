{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 20,
   "id": "elementary-catalyst",
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import geopandas as gpd\n",
    "import numpy as np\n",
    "from sqlalchemy import create_engine\n",
    "from bokeh.models import *\n",
    "from bokeh.plotting import * \n",
    "from bokeh.io import *\n",
    "from bokeh.tile_providers import *\n",
    "from bokeh.palettes import *\n",
    "from bokeh.transform import *\n",
    "from bokeh.layouts import *"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "id": "adult-transmission",
   "metadata": {},
   "outputs": [],
   "source": [
    "def Load_Lagos_gdf():\n",
    "    # ---------------------- REQUEST DATA FROM SERVER SE4GI -----------------------\n",
    "   engine = create_engine('postgresql://postgres:user@localhost:5432/SE4GI')\n",
    "    # read the dataframe from a postgreSQL table\n",
    "   data_geodf = gpd.read_postgis('Lagos ALPhA Survey', engine, geom_col='geometry')\n",
    "   return data_geodf"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "id": "alleged-cycling",
   "metadata": {},
   "outputs": [],
   "source": [
    "lagos_gdf = Load_Lagos_gdf().to_crs(epsg=3857)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "id": "deadly-heart",
   "metadata": {},
   "outputs": [],
   "source": [
    "def getPointCoords(rows, geom, coord_type):\n",
    "    \"\"\"Calculates coordinates ('x' or 'y') of a Point geometry\"\"\"\n",
    "    if coord_type == 'x':\n",
    "        return rows[geom].x\n",
    "    elif coord_type == 'y':\n",
    "        return rows[geom].y"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 24,
   "id": "complete-pantyhose",
   "metadata": {},
   "outputs": [],
   "source": [
    "lagos_gdf['x'] = lagos_gdf.apply(getPointCoords, geom='geometry', coord_type='x', axis=1)\n",
    "lagos_gdf['y'] = lagos_gdf.apply(getPointCoords, geom='geometry', coord_type='y', axis=1)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 25,
   "id": "solid-steps",
   "metadata": {},
   "outputs": [],
   "source": [
    "lagos_df = lagos_gdf.drop('geometry', axis=1).copy()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 26,
   "id": "simple-customer",
   "metadata": {},
   "outputs": [],
   "source": [
    "pointSource = ColumnDataSource(lagos_df)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 27,
   "id": "healthy-array",
   "metadata": {},
   "outputs": [],
   "source": [
    "scale = 2000\n",
    "x = lagos_gdf['x']\n",
    "y = lagos_gdf['y']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 28,
   "id": "underlying-error",
   "metadata": {},
   "outputs": [],
   "source": [
    "x_min=int(x.mean() - (scale * 350))\n",
    "x_max=int(x.mean() + (scale * 350))\n",
    "y_min=int(y.mean() - (scale * 350))\n",
    "y_max=int(y.mean() + (scale * 350))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 29,
   "id": "african-traffic",
   "metadata": {},
   "outputs": [],
   "source": [
    "tile_provider=get_provider(OSM)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 30,
   "id": "animal-dragon",
   "metadata": {},
   "outputs": [],
   "source": [
    "plot=figure(\n",
    "    title='ALPhA test',\n",
    "    match_aspect=True,\n",
    "    tools='wheel_zoom,pan,reset,save',\n",
    "    x_range=(x_min, x_max),\n",
    "    y_range=(y_min, y_max),\n",
    "    x_axis_type='mercator',\n",
    "    y_axis_type='mercator',\n",
    "    width=500\n",
    "    )"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "id": "afraid-processing",
   "metadata": {},
   "outputs": [],
   "source": [
    "plot.grid.visible=True\n",
    "\n",
    "map=plot.add_tile(tile_provider)\n",
    "map.level='underlay'\n",
    "\n",
    "plot.xaxis.visible = False\n",
    "plot.yaxis.visible=False\n",
    "plot.title.text_font_size=\"20px\"\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 32,
   "id": "applied-hebrew",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div style=\"display: table;\"><div style=\"display: table-row;\"><div style=\"display: table-cell;\"><b title=\"bokeh.models.renderers.GlyphRenderer\">GlyphRenderer</b>(</div><div style=\"display: table-cell;\">id&nbsp;=&nbsp;'1183', <span id=\"1186\" style=\"cursor: pointer;\">&hellip;)</span></div></div><div class=\"1185\" style=\"display: none;\"><div style=\"display: table-cell;\"></div><div style=\"display: table-cell;\">data_source&nbsp;=&nbsp;ColumnDataSource(id='1140', ...),</div></div><div class=\"1185\" style=\"display: none;\"><div style=\"display: table-cell;\"></div><div style=\"display: table-cell;\">glyph&nbsp;=&nbsp;Circle(id='1181', ...),</div></div><div class=\"1185\" style=\"display: none;\"><div style=\"display: table-cell;\"></div><div style=\"display: table-cell;\">hover_glyph&nbsp;=&nbsp;None,</div></div><div class=\"1185\" style=\"display: none;\"><div style=\"display: table-cell;\"></div><div style=\"display: table-cell;\">js_event_callbacks&nbsp;=&nbsp;{},</div></div><div class=\"1185\" style=\"display: none;\"><div style=\"display: table-cell;\"></div><div style=\"display: table-cell;\">js_property_callbacks&nbsp;=&nbsp;{},</div></div><div class=\"1185\" style=\"display: none;\"><div style=\"display: table-cell;\"></div><div style=\"display: table-cell;\">level&nbsp;=&nbsp;'glyph',</div></div><div class=\"1185\" style=\"display: none;\"><div style=\"display: table-cell;\"></div><div style=\"display: table-cell;\">muted&nbsp;=&nbsp;False,</div></div><div class=\"1185\" style=\"display: none;\"><div style=\"display: table-cell;\"></div><div style=\"display: table-cell;\">muted_glyph&nbsp;=&nbsp;None,</div></div><div class=\"1185\" style=\"display: none;\"><div style=\"display: table-cell;\"></div><div style=\"display: table-cell;\">name&nbsp;=&nbsp;None,</div></div><div class=\"1185\" style=\"display: none;\"><div style=\"display: table-cell;\"></div><div style=\"display: table-cell;\">nonselection_glyph&nbsp;=&nbsp;Circle(id='1182', ...),</div></div><div class=\"1185\" style=\"display: none;\"><div style=\"display: table-cell;\"></div><div style=\"display: table-cell;\">selection_glyph&nbsp;=&nbsp;'auto',</div></div><div class=\"1185\" style=\"display: none;\"><div style=\"display: table-cell;\"></div><div style=\"display: table-cell;\">subscribed_events&nbsp;=&nbsp;[],</div></div><div class=\"1185\" style=\"display: none;\"><div style=\"display: table-cell;\"></div><div style=\"display: table-cell;\">syncable&nbsp;=&nbsp;True,</div></div><div class=\"1185\" style=\"display: none;\"><div style=\"display: table-cell;\"></div><div style=\"display: table-cell;\">tags&nbsp;=&nbsp;[],</div></div><div class=\"1185\" style=\"display: none;\"><div style=\"display: table-cell;\"></div><div style=\"display: table-cell;\">view&nbsp;=&nbsp;CDSView(id='1184', ...),</div></div><div class=\"1185\" style=\"display: none;\"><div style=\"display: table-cell;\"></div><div style=\"display: table-cell;\">visible&nbsp;=&nbsp;True,</div></div><div class=\"1185\" style=\"display: none;\"><div style=\"display: table-cell;\"></div><div style=\"display: table-cell;\">x_range_name&nbsp;=&nbsp;'default',</div></div><div class=\"1185\" style=\"display: none;\"><div style=\"display: table-cell;\"></div><div style=\"display: table-cell;\">y_range_name&nbsp;=&nbsp;'default')</div></div></div>\n",
       "<script>\n",
       "(function() {\n",
       "  var expanded = false;\n",
       "  var ellipsis = document.getElementById(\"1186\");\n",
       "  ellipsis.addEventListener(\"click\", function() {\n",
       "    var rows = document.getElementsByClassName(\"1185\");\n",
       "    for (var i = 0; i < rows.length; i++) {\n",
       "      var el = rows[i];\n",
       "      el.style.display = expanded ? \"none\" : \"table-row\";\n",
       "    }\n",
       "    ellipsis.innerHTML = expanded ? \"&hellip;)\" : \"&lsaquo;&lsaquo;&lsaquo;\";\n",
       "    expanded = !expanded;\n",
       "  });\n",
       "})();\n",
       "</script>\n"
      ],
      "text/plain": [
       "GlyphRenderer(id='1183', ...)"
      ]
     },
     "execution_count": 32,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "plot.circle('x','y', source=pointSource, color = 'blue', size = 10)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 33,
   "id": "honey-position",
   "metadata": {},
   "outputs": [],
   "source": [
    "#r,bins=plot.hexbin(x,y,size=scale*10,hover_color='pink',hover_alpha=0.8,)\n",
    "#point_hover = HoverTool(tooltips=[('nickname', '@18b_ALPhA_Name')], mode='mouse', point_policy='follow_mouse',renderers=[r])\n",
    "#point_hover.renderers.append(r)\n",
    "#plot.tools.append(point_hover)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 34,
   "id": "prescription-salad",
   "metadata": {},
   "outputs": [],
   "source": [
    "#plot.tools.append(point_hover)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 35,
   "id": "previous-florist",
   "metadata": {
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "show(plot)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "typical-croatia",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.10"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
