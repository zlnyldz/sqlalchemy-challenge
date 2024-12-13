import datetime as dt
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
# Create engine using the hawaii.sqlite database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using automap_base()
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)
# Assign the measurement class to a variable called Measurement and
# the station class to a variable called Station
Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' dates should be in the format YYYY-MM-DD.</p>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from the most recent date in the database
    session = Session(engine)
    try:
        latest_date_str = session.query(func.max(Measurement.date)).scalar()
        latest_date = dt.datetime.strptime(latest_date_str, "%Y-%m-%d")
        prev_year = latest_date - dt.timedelta(days=365)
        # Query for the date and precipitation for the last year
        precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
        # Dict with date as the key and prcp as the value
        precip = {date: prcp for date, prcp in precipitation}
        return jsonify(precip)
    finally:
        session.close()
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    session = Session(engine)
    try:
        results = session.query(Station.station).all()
        # Unravel results into a 1D array and convert to a list
        stations = list(np.ravel(results))
        return jsonify(stations=stations)
    finally:
        session.close()
@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations (tobs) for the last year"""
    session = Session(engine)
    try:
        # Get the most recent date in the dataset
        latest_date_str = session.query(func.max(Measurement.date)).scalar()
        latest_date = dt.datetime.strptime(latest_date_str, "%Y-%m-%d")
        # Calculate the date one year ago
        prev_year = latest_date - dt.timedelta(days=365)
        # Query temperature observations for the last year
        results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= prev_year).all()
        # Format the results into a list of dictionaries
        tobs_data = [{"date": date, "temperature": tobs} for date, tobs in results]
        return jsonify(temperature_observations=tobs_data)
    finally:
        session.close()
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return temperature statistics."""
    session = Session(engine)
    try:
        # Define the selection for min, avg, and max temperatures
        sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
        if not end:
            start_dt = dt.datetime.strptime(start, "%Y-%m-%d")
            results = session.query(*sel).filter(Measurement.date >= start_dt).all()
        else:
            start_dt = dt.datetime.strptime(start, "%Y-%m-%d")
            end_dt = dt.datetime.strptime(end, "%Y-%m-%d")
            results = session.query(*sel).filter(Measurement.date >= start_dt).filter(Measurement.date <= end_dt).all()
        # Convert the query results to a list and return as JSON
        temps = list(np.ravel(results))
        return jsonify(temperature_stats=temps)
    finally:
        session.close()
if __name__ == '__main__':
    app.run(debug=True)