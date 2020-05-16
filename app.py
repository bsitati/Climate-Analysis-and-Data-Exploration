import numpy as np

import sqlalchemy
import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy import create_engine, func, inspect 
from sqlalchemy.sql import label
import datetime as dt, timedelta
from dateutil.relativedelta import relativedelta
from datetime import date
import dateutil.parser

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurements = Base.classes.measurement
Stations = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start_date<br/>" 
        f"/api/v1.0/temps/start_date/end_date<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation and dates"""
    # Query all passengers
    results = session.query(Measurements.date, Measurements.prcp).all()

    session.close()

    # Convert list of tuples into normal list
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        # precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    results = session.query(Stations.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    max_date = session.query(Measurements).order_by(desc('date')).first() 
    d = dt.datetime.strptime(max_date.date, "%Y-%m-%d")
    month_12 = d - dateutil.relativedelta.relativedelta(months=12)

    top_station_1 = session.query(Measurements.station, Measurements.id, label('station_count',func.count(Measurements.id))).\
    group_by(Measurements.station).order_by(desc(func.count(Measurements.id))).first()
    
    results = session.query(Measurements.date, Measurements.tobs).filter(Measurements.date > month_12).filter(Measurements.station==top_station_1[0]).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_date_temps = []
    for date, tobs in results:
        temps_dict = {}
        temps_dict["date"] = date
        temps_dict["temps"] = tobs
        all_date_temps.append(temps_dict)

    return jsonify(all_date_temps)

@app.route("/api/v1.0/temps/<start>/<end>")
def datedStart(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #last year
    max_date = session.query(Measurements).order_by(desc('date')).first() 
    d = dt.datetime.strptime(max_date.date, "%Y-%m-%d")
    month_12 = d - dateutil.relativedelta.relativedelta(months=12)


    """Return a list of all passenger names"""
    # Query all passengers
    #results = session.query(Measurements.name).all()
    result_temps = session.query(label('min_temp',func.min(Measurements.tobs)), \
                             label('ave_temp', func.avg(Measurements.tobs)), \
                             label('max_temp',func.max(Measurements.tobs))).\
        filter(Measurements.date > month_12).filter(Measurements.date >= start).\
                             filter(Measurements.date <= end).all()

    session.close()

    # Convert list of tuples into normal list
     # Convert list of tuples into normal list
    all_date_temps = []
    for min_temp, ave_temp,max_temp  in result_temps:
        temps_dict = {}
        temps_dict["min_temp"] = min_temp
        temps_dict["ave_temp"] = ave_temp
        temps_dict["max_temp"] = max_temp
        all_date_temps.append(temps_dict)

    return jsonify(all_date_temps)

@app.route("/api/v1.0/temp/<start>")
def datedStartEnd(start):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #last year
    max_date = session.query(Measurements).order_by(desc('date')).first() 
    d = dt.datetime.strptime(max_date.date, "%Y-%m-%d")
    month_12 = d - dateutil.relativedelta.relativedelta(months=12)

    """Return a list of temp min, average, max"""
    # Query all start date
    #results = session.query(Measurements.name).all()
    result_temps = session.query(label('min_temp',func.min(Measurements.tobs)), \
                             label('ave_temp', func.avg(Measurements.tobs)), \
                             label('max_temp',func.max(Measurements.tobs))).\
    filter(Measurements.date > month_12).filter(Measurements.date >= start).all()

    # filter(Measurements.date > month_12).filter(Measurements.date >= start).all()

    session.close()

    # Convert list of tuples into normal list
    all_date_temps = []
    for min_temp, ave_temp,max_temp  in result_temps:
        temps_dict = {}
        temps_dict["min_temp"] = min_temp
        temps_dict["ave_temp"] = ave_temp
        temps_dict["max_temp"] = max_temp
        all_date_temps.append(temps_dict)

    return jsonify(all_date_temps)


if __name__ == '__main__':
    app.run(debug=True)
