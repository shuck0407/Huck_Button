# Import dependencies
import datetime as dt
import numpy as np
import pandas as pd
import os
import json

#Import Python functions from the stored_functions.py file
from .stored_functions import (bacteria_name, getsampleresults, pie_chart_data, bubble_chart_data, get_metadata)

from flask import (Flask, render_template, jsonify, redirect)
from flask_sqlalchemy import SQLAlchemy

#sqlqlchemy libs
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc

#Plotly libs
import plotly
import plotly.plotly as py
import plotly.figure_factory as ff
import plotly.graph_objs as go

#Flask setup
app = Flask(__name__)

#################################################
# Database Setup
#################################################

# Establishing connection to database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/bellybutton.sqlite"
db = SQLAlchemy(app)

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(db.engine, reflect=True)
Base.classes.keys()

# Save references to each table
Samples = Base.classes.samples
Samples_metadata = Base.classes.sample_metadata

#Define each Flask route
@app.route("/")
def welcome():
    return render_template('index.html')
    
@app.route("/samples/<sample>")
def samplepick(sample):

    pie_chart = stored_functions.pie_chart_data(sample)
    bubble_chart = stored_functions.bubble_chart_data(sample)
    meta_chart = stored_functions.get_metadata(sample)

    chart_dict = {'pie': pie_chart, 'bubble': bubble_chart, 'meta': meta_chart}

    return jsonify(chart_dict)

@app.route("/buttons")
def buttons():
    
    sql_stmt2 = Session.query(Samples_metadata).statement
    metadata_df = pd.read_sql_query(sql_stmt2, session.bind)

    #populate the bellybutton dropdown list
    buttons = metadata_df['sample'].tolist()

    return (jsonify(buttons))

if __name__ == "__main__":
    app.run(debug=True)


    

        
