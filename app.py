import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start]<br/>"
        f"/api/v1.0/[start]/[end]"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitation data"""
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    # Query all precipitation data from the last year
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= str(year_ago)).\
    order_by(Measurement.date).all()
    
    session.close()

    # Convert list of tuples into dictionary
    result_dict={}
    for row in results:
        result_dict.update({row[0] : row[1]})

    return jsonify(result_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of station names"""
    # Query all Stations
    results = session.query(Station.name, Station.station).all()

    session.close()

    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature obs for a year from the last data point"""
    # Query
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= str(year_ago)).\
    order_by(Measurement.date).all()

    session.close()

    return jsonify(results)

@app.route("/api/v1.0/<start_date>")
def startdate(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    if valid_date(start_date) == False:
        return jsonify({"error": f"Given start date: {start_date} is not in YYYY-MM-DD format. Please try again."}), 404

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start_date).\
    order_by(Measurement.date).all()

    session.close()

    result_dict = {}
    for row in results:
        result_dict.update({'Minimum Temp' : row[0],
                            'Average Temp' : row[1],
                            'Maximum Temp' : row[2]})
    return jsonify(result_dict)

@app.route("/api/v1.0/<start_date>/<end_date>")
def rangedate(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    if valid_date(start_date) == False:
        return jsonify({"error": f"Given start date: {start_date} is not in YYYY-MM-DD format. Please try again."}), 404
    if valid_date(end_date) == False:
        return jsonify({"error": f"Given end date: {end_date} is not in YYYY-MM-DD format. Please try again."}), 404
    #Make sure the end date is after the start date
    endyr = int(end_date[:4])
    endmo = int(end_date[5:7])
    enddy = int(end_date[8:])
    stryr = int(start_date[:4])
    strmo = int(start_date[5:7])
    strdy = int(start_date[8:])
    if (endyr < stryr) or (endmo < strmo and endyr == stryr) or (enddy < strdy and endmo == strmo and endyr == stryr):
           return jsonify({"error": f"The given end date occurs after the given start date. Please try again."}), 404

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).\
        order_by(Measurement.date).all()

    session.close()


    result_dict = {}
    for row in results:
        result_dict.update({'Minimum Temp' : row[0],
                            'Average Temp' : row[1],
                            'Maximum Temp' : row[2]})
    return jsonify(result_dict)

"""Use the datetime library to validate date string format"""
def valid_date(datestring):
    try:
        dt.datetime.strptime(datestring, '%Y-%m-%d')
        return True
    except ValueError:
        return False

if __name__ == '__main__':
    app.run(debug=True)
