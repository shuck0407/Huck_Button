# Import dependencies
import datetime as dt
import numpy as np
import pandas as pd
import os
import json
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

from flask import (Flask, render_template, jsonify, redirect)
from flask_sqlalchemy import SQLAlchemy

def bacteria_name(sample_df):    
    
    #This function strips the otu_labels down to their scientific bacteria name.
    # I am using this on my charts in place of the meaningless otu_id.

    #loop through the bacteria labels split on the semi-colon
    sample_df['bacteria0'] = sample_df['otu_label'].str.split(';').str[0]
    sample_df['bacteria1'] = sample_df['otu_label'].str.split(';').str[1]
    sample_df['bacteria2'] = sample_df['otu_label'].str.split(';').str[2]
    sample_df['bacteria3'] = sample_df['otu_label'].str.split(';').str[3]
    sample_df['bacteria4'] = sample_df['otu_label'].str.split(';').str[4]
    sample_df['bacteria5'] = sample_df['otu_label'].str.split(';').str[5]

    sample_df = sample_df.fillna('')
    sample_df['bact_label'] = ''
    
    for index, row in sample_df.iterrows():
        if sample_df.loc[index, 'bacteria5'] != '':
            sample_df['bact_label'][index] = row['bacteria5']
        elif sample_df.loc[index, 'bacteria4'] != '':
            sample_df['bact_label'][index] = row['bacteria4']
        elif sample_df.loc[index, 'bacteria3'] != '':
            sample_df['bact_label'][index] = row['bacteria3']
        elif sample_df.loc[index, 'bacteria2'] != '':
            sample_df['bact_label'][index] = row['bacteria2']
        elif sample_df.loc[index, 'bacteria1'] != '':
            sample_df['bact_label'][index] = row['bacteria1']
        else:
            sample_df['bact_label'][index] = row['bacteria0']
        
    sample_df = sample_df.drop(columns=['otu_label', 'bacteria0', 'bacteria1', 'bacteria2', 'bacteria3', 'bacteria4', 'bacteria5'])
    
    return sample_df

def getsampleresults(sample):
    
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/bellybutton.sqlite"
    db = SQLAlchemy(app)

    # reflect an existing database into a new model
    Base = automap_base()
    Base.prepare(db.engine, reflect=True)
    Base.classes.keys()

    # Save reference to samples table
    Samples = Base.classes.samples
   
    #Query all of the data in the samples table and make a dataframe
    sql_stmt = db.session.query(Samples).statement
    samples_df = pd.read_sql_query(sql_stmt, db.session.bind)

    #Slice the dataframe so that only the column for the sample remains
    sel_col_list = ['otu_id', 'otu_label', sample]
    samples_df = samples_df[sel_col_list]

    #Get a dataframe of otu_ids and labels to merge later
    otus = samples_df[['otu_id', 'otu_label']]
    
    #reset the index to otu_id so they don't get included in sum amounts
    samples_df = samples_df.set_index('otu_id')

    #summarize all of the participant data by otu_id
    sum_series = samples_df.sum(axis=1)

    #turn the series back into a dataframe and reset the index
    sum_df = sum_series.to_frame()
    sum_df.reset_index(level=0, inplace=True)

    #rename the column with the summary values to something meaningful
    sum_df = sum_df.rename(columns = {0 : 'data'})

    #now merge with the otu labels for our final samples dataframe
    sum_df = pd.merge(sum_df, otus, on='otu_id')

    #only return rows where the bacteria count is greater than 1
    sum_df = sum_df[(sum_df > 1).all(1)]

    #call the function that strips the otu_label to the bacteria name
    sum_df = bacteria_name(sum_df)

    #get rid of the otu_id and group/sum by bacteria type
    sum_df = sum_df.drop(columns=['otu_id'])
    sum_df = sum_df.groupby('bact_label').sum()    
    
    return sum_df

def pie_chart_data(sample):

    pie_df = getsampleresults(sample)

    #get the top ten bacteria for our pie chart
    pie_df_10 = pie_df.nlargest(10, 'data')

    #reset the index so the bacteria labels are in a column
    pie_df_10 = pie_df_10.reset_index()

    #create lists of the dataframe to send to Plotly pie chart
    sample_values = pie_df_10[pie_df_10.columns[1]].values.tolist()
    bact_labels = pie_df_10[pie_df_10.columns[0]].values.tolist()

    #create a dictionary for the pie chart
    pie_data = {'labels': bact_labels, 'values': sample_values, 'type': 'pie'} 
                        
    return pie_data     

def bubble_chart_data(sample):

    bubble_df = getsampleresults(sample)

    bubble_df = bubble_df.reset_index()

    #Create lists of the dataframe to sent to Plotly bubble chart
    x_values = bubble_df[bubble_df.columns[0]].values.tolist()
    y_values = bubble_df[bubble_df.columns[1]].values.tolist()
    marker_size = bubble_df[bubble_df.columns[1]].values.tolist()
    marker_color = bubble_df[bubble_df.columns[1]].values.tolist()

    #Min and max values for axes
    x_axis_max = bubble_df['bact_label'].count()
    y_axis_min = bubble_df['data'].min()
    y_axis_max = bubble_df['data'].max()

    sizeref = max(marker_size)/(50.**2)

    bubble_marker = {'color': marker_color, 'sizemode': 'area', 'sizeref': sizeref,
     'size': marker_size, 'symbol': 'circle'}

    bubble_data = {'x' : x_values, 'y': y_values, 'mode':'markers', 'marker': bubble_marker,
                    'text' : [x_values]}

    data = [bubble_data]                

    layout = {'title':'Bacteria Counts by Type', 'xaxis' : {'tickangle' : 45}, 
    'yaxis' : {'title' : 'Bacteria Count'}, 'width': 1000}

    bubble_chart = {'data' : data, 'layout' : layout}

    return bubble_chart

def get_metadata(sample):
    # Create engine using the `bellybutton.sqlite` database file
    engine = create_engine("sqlite:///db/bellybutton.sqlite")
    Base = automap_base()
    Base.prepare(engine, reflect=True)

    #Assign the samples_metadata class to variable
    sample_metadata = Base.classes.sample_metadata

    session = Session(engine)

    #Query all of the data in the samples table and make a dataframe
    results = session.query(sample_metadata).filter(sample_metadata.sample == sample).first()
    
    meta_dict =  {
        'Age':results.AGE,
        'BBType':results.BBTYPE,
        'Gender':results.GENDER,
        'Ethnicity':results.ETHNICITY,
        'Location':results.LOCATION,
        'Washing Frequency':results.WFREQ
    }
    
    return meta_dict

   

   
