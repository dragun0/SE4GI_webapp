# -*- coding: utf-8 -*-
"""
Created on Thu Jun  3 22:27:31 2021

@author: leoni
"""

from flask import (Flask, render_template, request, flash, redirect, abort, session, url_for)
from test_App_portfolio import get_alpha
from Mapping_tool import make_plot




app = Flask(__name__)



@app.route('/map')
def plot(): 
    
    make_plot()
    return render_template('Map_home.html')
    

   
@app.route("/Portfolio")
def portfolio():
    
    selectedID = request.args.get('id')
    alpha = get_alpha(selectedID)
      
    return render_template('Extend_portfolio.html', alphas=alpha)



if __name__ == '__main__':
   app.run(debug=True,use_reloader=False)
   
