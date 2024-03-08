# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
# Flask Routes
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precioitation():
# Convert the query results from your precipitation analysis
    session = Session(engine)
    recent_date = session.query(Measurement).order_by(Measurement.date.desc()).first().date
    one_year_from_last = dt.date(2017,8,23) - dt.timedelta(days= 365)
    date_prcp = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= one_year_from_last).\
    order_by(Measurement.date).all()

    return jsonify(dict(date_prcp))

@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of stations from the dataset.
    session = Session(engine)
    act_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    

    
    return jsonify(dict(act_station))


@app.route("/api/v1.0/tobs")
def tobs():
#Query the dates and temperature observations of the 
# most-active station for the previous year of data.
#Return a JSON list of temperature observations
# for the previous year.
    session = Session(engine)
    one_year_from_last = dt.date(2017,8,23) - dt.timedelta(days= 365)
    station_result = session.query(Measurement.station, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= one_year_from_last).all()
    
    tem_obser = []
    for tem in station_result:
        year_tem = {}
        year_tem["tobs"] = tem.tobs
        tem_obser.append(year_tem)
          
    return jsonify(tem_obser) 

@app.route("/api/v1.0/start")
def start():
    session = Session(engine)
    start_date = dt.date(2010,8,23)
    start_end = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    
    return jsonify(dict(start_date))

@app.route("/api/v1.0/start/end")
def start_end():
    session = Session(engine)
    start_date = dt.date(2010,8,23)
    end_date = dt.date(2015,8,23) + dt.timedelta(days= 1000)
    start_end = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()
    
    return jsonify(dict(start_end))

if __name__ == '__main__':
    app.run(debug=True)

#################################################
