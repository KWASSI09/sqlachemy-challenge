import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt



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
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation and date"""
    # Query all precipitation and date
    results = session.query(Measurement.date,Measurement.prcp).all()

    session.close()

    # Convert list of tuples into dictionary
    all_precepitations=[]
    for date,prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        all_precepitations.append(precipitation_dict)

    return jsonify(all_precepitations)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.id,Station.station,Station.name).all()
    session.close()
    all_station=[]
    for id,station,name in results:
        station_dict={}
        station_dict['Id']=id
        station_dict['station']=station
        station_dict['name']=name
        all_station.append(station_dict)
    return jsonify(all_station)

@app.route("/api/v1.0/tobs")
def tempartureobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all temparture observation"""

    # retrieving  the period previous the last data point in the database

    results_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_arr=list(np.ravel(results_date))[0]
    latest_date=dt.datetime.strptime(date_arr,"%Y-%m-%d")
    prev_year=latest_date-dt.timedelta(days=366)

# querying  the date and precipitation scores
    results=session.query(Measurement.date, Measurement.tobs).\
                    order_by(Measurement.date.desc()).\
                    filter(Measurement.date>=prev_year).all()
    session.close()
    all_temperature=[]
    for date,tobs in results:
        tobs_dict={}
        tobs_dict['date']=date
        tobs_dict['tobs']=tobs
        all_temperature.append(tobs_dict)
    return jsonify(all_temperature)

 
# and return the minimum, average, and maximum temperatures for that range of dates
@app.route("/api/v1.0/<start>")
def Start_Date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    results=session.query (func.min(Measurement.tobs),
                           func.avg(Measurement.tobs),\
                           func.max(Measurement.tobs)).\
                           filter(Measurement.date >= start).all()
    session.close()
    temp_obs={}
    temp_obs["Min_Temp"]=results[0][0]
    temp_obs["avg_Temp"]=results[0][1]
    temp_obs["max_Temp"]=results[0][2]
    return jsonify(temp_obs)



@app.route("/api/v1.0/<start>/<end>")
def Start_end_date(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    results=session.query(func.min(Measurement.tobs),
                           func.avg(Measurement.tobs),
                           func.max(Measurement.tobs)).\
                           filter(Measurement.date >= start).\
                           filter(Measurement.date <= end).all()
    session.close()
    temp_obs={}
    temp_obs["Min_Temp"]=results[0][0]
    temp_obs["avg_Temp"]=results[0][1]
    temp_obs["max_Temp"]=results[0][2]
    return jsonify(temp_obs)


if __name__ == '__main__':
    app.run(debug=True)