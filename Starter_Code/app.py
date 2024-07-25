from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

app = Flask(__name__)

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

print(Base.classes.keys())

Measurement = Base.classes.measurement
Station=Base.classes.station

session=Session(engine)

# Define routes
@app.route("/")
def home():
    return """
    <h1>Welcome to the Hawaii Climate Analysis API!</h1>
    <h2>Available Routes:</h2>
    <ul>
        <li><a href="/api/v1.0/precipitation" target="_blank">/api/v1.0/precipitation</a></li>
        <li><a href="/api/v1.0/stations" target="_blank">/api/v1.0/stations</a></li>
        <li><a href="/api/v1.0/tobs" target="_blank">/api/v1.0/tobs</a></li>
        <li><a href="/api/v1.0/<start>" target="_blank">/api/v1.0/&lt;start&gt;</a></li>
        <li><a href="/api/v1.0/<start>/<end>" target="_blank">/api/v1.0/&lt;start&gt;/&lt;end&gt;</a></li>
    </ul>
    """

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Design a query to retrieve the last 12 months of precipitation data and plot the results.
    # Starting from the most recent data point in the database.
    # Calculate the date one year from the last date in the dataset
    most_recent_date = dt.date(2016, 8, 23) - dt.timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation scores
    precipitation_sq = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= most_recent_date).\
        order_by(Measurement.date.asc()).\
        all()
    
    # Save the query results as a Pandas DataFrame. Explicitly set the column names
    precipitation_df = pd.DataFrame(precipitation_sq, columns=["Date", "Precipitation"])

    # Sort the dataframe by date
    precipitation_df["Date"] = pd.to_datetime(precipitation_df['Date'])
    precipitation_df = precipitation_df.sort_values(by="Date", ascending=True).reset_index(drop=True)
    
    session.close()
    
    # Wouldn't work wihtout this line of code
    precipitation_data = precipitation_df.to_dict(orient="records")
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    # Query the stations
    stations_results = session.query(Station.station).all()
    
    session.close()
    
    # Convert tuples into normal list
    stations_data = list(np.ravel(stations_results))
    
    return jsonify(stations_data)

@app.route("/api/v1.0/tobs")
def tobs():
    # Recent date
    most_recent_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Querying
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
       filter(Measurement.station == 'USC00519281').\
       filter(Measurement.date >= most_recent_date).all()
    
    session.close()
    
    # Converting
    tob = list(np.ravel(tobs_data))
    
    return jsonify(tob=tob)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start=None, end=None):     
    """Return TMIN, TAVG, TMAX."""
    
    temp_stats = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    # Kept getting a valueerror here and could not find any fix for it at all. The code might work, might not, but I'm out of options for the time being.
    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        temp_results = session.query(*start).\
            filter(Measurement.station >= start).all()

        session.close()

        temps = list(np.ravel(temp_results))
        return jsonify(temps)
    
    temp_stats_se = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    
    temp_results_se = session.query(temp_stats_se).\
       filter(Measurement.date >= start).\
       filter(Measurement.date <= end).all()
    
    session.close()
    
    temp_start_end_date = list(np.ravel(temp_results_se))
    return jsonify(temp_start_end_data)

if __name__ == '__main__':
    # Running the app
    app.run(debug=True, threaded=True)
