# PART 1 -- DEPENDENCIES AND SETUP

import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from flask import Flask, jsonify, request

# PART 2 -- DATABASE SETUP / LINK
# link python to database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# declare base as automap base
Base = automap_base()

# reflect the database into classes
Base.prepare(engine, reflect=True)

# Save references
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session (link) to databse
session = Session(engine)

# PART 3 -- FLASK SETUP AND ROUTE CREATION

# Flask setup
app = Flask(__name__)
# Flask routes
@app.route("/")
# intro/explanation
def welcome():
    return (
        f"Welcome to the Hawaii weather API!<br/>"
        f"Pick from the following available routes:<br/>"
        f"/api/v1.0/precipitation<br/>Returns a list of JSON representation of dictionary.<br/>"
        f"/api/v1.0/stations<br/>Returns a list of stations from the dataset.<br/>"
        f"/api/v1.0/tobs<br/>Returns a list of dates and temperature observations from dataset. Stations are included to avoid confusion as instructions don't specify a particular station.<br/>"
        # instructions don't mention to pull in dates and temperatures for any specific stations, but here it is in the comments for the most popular station in case it's needed
        # f"/api/v1.0/mostobstobs<br/>Query for the dates and temperature observations from a year from the last datapoint for the station with most observations.<br/>"
        f"/api/v1.0/temp/start/end<br/>Returns a list of min, avg, and max temperatures for all dates between the start and end dates.<br/>"
    )
# precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    # Calulate the date 1 year ago from today
    last_date = session.query(Measurement.date,Measurement.prcp).order_by(Measurement.date.desc()).first()[0]
    last_year = str(dt.datetime.strptime(last_date,"%Y-%m-%d") - dt.timedelta(days=365))

    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
		filter(Measurement.date >=last_year, Measurement.date <=last_date).\
		order_by(Measurement.date).all()
	# formula for itemizing each item brought in from the query
    precip_dict = {date: prcp for date, prcp in precipitation}
    return jsonify(precip_dict)

# stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    results = session.query(Measurement.station).\
    	group_by(Measurement.station).all()
    # formula for itemizing each item brought in from the query
    stations = list(np.ravel(results))
    return jsonify(stations)

# temperature observations route
@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations for previous year."""
    # last date in the dataset and year from last date calculations
    last_date = session.query(Measurement.date,Measurement.prcp).order_by(Measurement.date.desc()).first()[0]
    last_year = str(dt.datetime.strptime(last_date,"%Y-%m-%d") - dt.timedelta(days=365))

    last_year_tobs = session.query(Measurement.date, Measurement.station,Measurement.tobs).\
		filter(Measurement.date >=last_year, Measurement.date <=last_date).\
		order_by(Measurement.date,Measurement.station).all()

    # formula for itemizing each item brought in from the query
    temps = list(np.ravel(last_year_tobs))
    return jsonify(temps)

# THIS WOULD BE THE CODE FOR THE ROUTE FOR THE MOST POPULAR STATION, BUT IT ISN'T ASKED FOR IN THE ASSIGNMENT
# @app.route("/api/v1.0/mostobstobs")
# def temp_monthly_most_obs():    
#     # last date in the dataset and year from last date calculations
#     last_date = session.query(Measurement.date,Measurement.prcp).order_by(Measurement.date.desc()).first()[0]
#     last_year = str(dt.datetime.strptime(last_date,"%Y-%m-%d")-dt.timedelta(days=365))
    
#     last_year_tobs_most_obs = session.query(Measurement.date,Measurement.tobs).\
# 		filter(Measurement.date >=last_year, Measurement.date <=last_date, Measurement.station == 'USC00519281').\
# 		order_by(Measurement.date).all()

# 	temps_most_obs = list(np.ravel(last_year_tobs_most_obs))
	
# 	return jsonify(temps_most_obs)

# min, avg, and max calculations for specific vacation dates path
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Returns min, avg, and max."""

    # Select statement
    select_stat = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*select_stat).\
            filter(Measurement.date >= start).all()
    # formula for itemizing each item brought in from the query
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*select_stat).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # formula for itemizing each item brought in from the query
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == '__main__':
    app.run()