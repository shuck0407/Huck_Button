# Import dependencies
import datetime as dt
import numpy as np
import pandas as pd
import os
import json

#Import Python functions from the stored_functions.py file
from app.stored_functions import bacteria_name, getsampleresults, pie_chart_data, bubble_chart_data, get_metadata

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

from flask import Flask, render_template, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.debug = True

#################################################
# Database Setup
#################################################

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "") or "sqlite:///db/bellybutton.sqlite"
db = SQLAlchemy(app)

from .models import Samples, Samples_metadata


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
    engine = create_engine("sqlite:///db/bellybutton.sqlite")

    Base = automap_base()
    
    Base.prepare(engine, reflect=True)
    Samples_metadata = Base.classes.sample_metadata

    # Create our session (link) from Python to the DB
    session = Session(engine)

    sql_stmt2 = session.query(Samples_metadata).statement
    metadata_df = pd.read_sql_query(sql_stmt2, session.bind)

    #populate the bellybutton dropdown list
    buttons = metadata_df['sample'].tolist()

    return (jsonify(buttons))

if __name__ == "__main__":
    app.run(debug=True)


    

        