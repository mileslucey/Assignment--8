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

# Create our session (link) from Python to the DB
session = Session(engine)

# PART 3 -- FLASK SETUP AND ROUTE CREATION
# Flask setup
app = Flask(__name__)

# Flask routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii weather API!<br/>"
        f"Pick from the following available routes:<br/>"
        f"/api/v1.0/precipitation<br/>Converts query results to a Dictionary using date as the key and prcp as the value.<br/>"
        f"/api/v1.0/stations<br/>Returns a JSON list of stations from the dataset.<br/>"
        f"/api/v1.0/tobs<br/>Query for the dates and temperature observations from a year from the last datapoint. Returns JSON list of temperature observations from a year from the last data point.<br/>"
        # f"/api/v1.0/mostobstobs<br/>Query for the dates and temperature observations from a year from the last datapoint for the station with most observations.<br/>"
        f"/api/v1.0/temp/start/end<br/>Returns a JSON list of min, avg, and max temperatures for all dates between the start and end dates.<br/>"
    )


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

    precip_dict = {date: prcp for date, prcp in precipitation}
    return jsonify(precip_dict)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    # results = session.query(Station.station).all()
    results = session.query(Measurement.station).\
    	group_by(Measurement.station).all()
    # Unravel results into a 1D array and convert to a list
    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""
    # last date in the dataset and year from last date calculations
    last_date = session.query(Measurement.date,Measurement.prcp).order_by(Measurement.date.desc()).first()[0]
    last_year = str(dt.datetime.strptime(last_date,"%Y-%m-%d") - dt.timedelta(days=365))

    # Query the primary station for all tobs from the last year
    # results = session.query(Measurement.tobs).\
    #     filter(Measurement.station == 'USC00519281').\
    #     filter(Measurement.date >= prev_year).all()

    last_year_tobs = session.query(Measurement.date, Measurement.station,Measurement.tobs).\
		filter(Measurement.date >=last_year, Measurement.date <=last_date).\
		order_by(Measurement.date,Measurement.station).all()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(last_year_tobs))

    # Return the results
    return jsonify(temps)

@app.route("/api/v1.0/mostobstobs")
# def temp_monthly_most_obs():    
#     # last date in the dataset and year from last date calculations
#     last_date = session.query(Measurement.date,Measurement.prcp).order_by(Measurement.date.desc()).first()[0]
#     last_year = str(dt.datetime.strptime(last_date,"%Y-%m-%d")-dt.timedelta(days=365))
    
#     last_year_tobs_most_obs = session.query(Measurement.date,Measurement.tobs).\
# 		filter(Measurement.date >=last_year, Measurement.date <=last_date, Measurement.station == 'USC00519281').\
# 		order_by(Measurement.date).all()

# 	temps_most_obs = list(np.ravel(last_year_tobs_most_obs))
	
# 	return jsonify(temps_most_obs)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    # Select statement
    select_stat = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*select_stat).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*select_stat).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == '__main__':
    app.run()