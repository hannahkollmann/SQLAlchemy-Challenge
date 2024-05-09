# Import the dependencies.
import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///./Resources/hawaii.sqlite")


# Reflect an existing database into a new model
Base = automap_base()


# Reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement


# Create our session (link) from Python to the DB
session = Session(engine)



#################################################
# Flask Setup
#################################################

app = Flask(__name__)


# Creating a helper function for date validation
def valid_date(datestr):
    """Helper function to check if a date string is valid."""
    try:
        dt.datetime.strptime(datestr, "%Y-%m-%d")
        return True
    except ValueError:
        return False



#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return(
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"The dates and precipitation amounts from the previous year.<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"The list of observatory stations collecting the data."
        f"<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"The temperature observations from the previous year.<br/>"
        f"<br/>"
        f"/api/v1.0/YYYY-MM-DD"
        f"<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD"
        f"<br/>"
        f"The list of minimum, maximum and average temperatures between 08-22-2016 through 08-23-2017.<br/>"
        f"<br/>"
        f"Thanks for visiting the app!"
    )

# App routing for precipitation for the past 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session link
    session = Session(engine)
    # Query the last 12 months of precipitation data
    cutoff_date = '2016-08-23'
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > cutoff_date).all()
    session.close()

    # Create a dictionary from the results and append to a list of precipitation_data
    precip_data = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip_data.append(precip_dict)

    return jsonify(precip_data)




 # App routing for station list
@app.route("/api/v1.0/stations")
def stations():
    # Create session link
    session = Session(engine)
    # Query the names of all stations in the list
    results = session.query(Measurement.station).distinct().all()
    session.close()

    # Create a dictionary of the active stations and their counts
    station_data = []
    for station in results:
        station_dict = {}
        station_dict["station name"] = station[0]
        station_data.append(station_dict)

    return jsonify(station_data)




# App routing for t_observed for the past 12 months
@app.route("/api/v1.0/tobs")
def tobs():
    # Create session link
    session = Session(engine)
    # Query the last 12 months of temperature data from the most active observation station 
    cutoff_date_12month = '2017-08-23'
    results = session.query(Measurement.date, Measurement.tobs).filter((Measurement.station == 'USC00519281') & (Measurement.date > cutoff_date_12month)).all()
    session.close()

    # Create a dictionary of t_obs data for the most active station
    tobs_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Oberved Temperature"] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)




@app.route("/api/v1.0/<start>")
def start(start):
    # Create session link
    session = Session(engine)
    # Using the helper function for date validation
    if not valid_date(start):
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."})

    # Query to retrieve temperature statistics from the given start date
    temp_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    if not temp_results or temp_results[0][0] is None:
        return jsonify({"error": "No temperature data found for the given start date."})

    min_temp, max_temp, avg_temp = temp_results[0]

    # Format the results as a dictionary
    temp_data = {
        "Start Date": start,
        "Minimum Temperature": min_temp,
        "Maximum Temperature": max_temp,
        "Average Temperature": avg_temp
    }

    return jsonify(temp_data)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create session link
    session = Session(engine)
    # Using the helper function for both start and end date validation
    if not valid_date(start) or not valid_date(end):
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."})

    # Query to retrieve temperature statistics for the given date range
    temp_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).all()
    session.close()

    if not temp_results or temp_results[0][0] is None:
        return jsonify({"error": "No temperature data found for the given date range."})

    min_temp, max_temp, avg_temp = temp_results[0]

    # Format the results as a dictionary
    temp_data = {
        "Start Date": start,
        "End Date": end,
        "Minimum Temperature": min_temp,
        "Maximum Temperature": max_temp,
        "Average Temperature": avg_temp
    }

    return jsonify(temp_data)


if __name__ == '__main__':
    app.run(debug=True)



#Test Start Date URL = 127.0.0.1:5000/api/v1.0/2016-08-22
#Test Start Date/End Date  URL = 127.0.0.1:5000/api/v1.0/2016-08-22/2017-08-23




    

