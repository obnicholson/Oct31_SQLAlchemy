import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import and_

from flask import Flask, jsonify


##########setting up database##########
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect existing hawaii database
Base = automap_base()
Base.prepare(engine, reflect=True)

#reference tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#create session
session = Session(engine)


##########setting up flask##########
app = Flask(__name__)

@app.route("/")
def home():
    """Available API Routes:"""
    return(
        f"Available API Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start_date><br/>"
        f"/api/v1.0/<start_date>/<end_date>"
    )

#last 12 months of precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns the last 12 months of precipitation data"""
    max_date = dt.datetime.strptime(session.query(func.max(Measurement.date)).scalar(),'%Y-%m-%d')
    year_ago = max_date - dt.timedelta(days=365)
    precipitation = session.query(Measurement.prcp, Measurement.date).filter(Measurement.date > year_ago).all()
    
    all_observations = []
    for observation in precipitation:
        precip_dict = {}
        precip_dict[observation.date] = observation.prcp
        all_observations.append(precip_dict)
    
    return jsonify(all_observations)


#all stations in dataset
@app.route("/api/v1.0/stations")
def stations():
    """Returns the names of all sations in dataset"""
    stations = session.query(Station.station).all()

    station_names = list(np.ravel(stations))

    return jsonify(station_names)

#last 12 months of temperature data
@app.route("/api/v1.0/tobs")
def tobs():
    """Returns a list of temperature observations over the last 12 months of data"""
    max_date = dt.datetime.strptime(session.query(func.max(Measurement.date)).scalar(),'%Y-%m-%d')
    year_ago = max_date - dt.timedelta(days=365)
    temperatures = session.query(Measurement.tobs).filter(Measurement.date > year_ago).all()

    all_temps = list(np.ravel(temperatures))

    return jsonify(all_temps)

@app.route("/api/v1.0/<start>")
def calc_temps_ge(start):
    """Returns a list of TMIN, TAVG, TMAX of all dates greater than supplied start date""" 
    observations = list(np.ravel(session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()))
    
    return jsonify(observations)

@app.route("/api/v1.0/<start>/<end>")
def calc_temps_ge_le(start,end):
    """Returns a list of TMIN, TAVG, TMAX of all dates between supplied start and end date""" 
    observations = list(np.ravel(session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(and_(Measurement.date >= start, Measurement.date <= end)).all()))
    
    return jsonify(observations)

if __name__ == '__main__':
    app.run(debug=True)


