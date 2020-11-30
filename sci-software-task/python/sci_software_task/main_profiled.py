import itertools
import math

import numpy as np
import rasterio
from scipy import interpolate

import os

# To help indentify bottleneck(s)
import datetime as dt

def load_datasets():
    """
    Loads the two target datasets from disk into memory.
    """
    print("Reading temperature data...")
    hourly_max_temp_data = rasterio.open("../data/hourly_max_temp_2019.nc").read()
    print("Reading land cover data...")
    land_cover_data = rasterio.open("../data/land_cover_classification.tiff").read()[0]  # There's only a single band in this dataset - just return that
    return land_cover_data, hourly_max_temp_data


def calculate_weekly_maximum_temp(hourly_max_temp_data):
    """
    Calculates the weekly maximum temperatures, given the hourly maximum temperatures.
    """
    print("Calculating weekly maximum temperatures... ")
    start_time = dt.datetime.now()
	
    # Initialise empty array which we then write with the calculated maximum daily temperatures
    daily_maxima = np.empty((365, 41, 107))
    daily_maxima[:] = np.NaN

    for i in range(365):
        daily_data = hourly_max_temp_data[i * 24 : (i + 1) * 24]
        daily_maxima[i::] = np.apply_over_axes(
            np.max, daily_data, [0]
        )  # Equivalent to np.max(first_day, axis=0, keepdims=True)

    # Initialise empty array which we then write with the calculated maximum weekly temperatures
    weekly_maxima = np.empty((52, 41, 107))
    weekly_maxima[:] = np.NaN

    # Take only the 7-day periods which divide into a year with no remainder
    for i in range(52):
        weekly_data = daily_maxima[i * 7 : (i + 1) * 7]
        weekly_maxima[i::] = np.apply_over_axes(
            np.max, weekly_data, [0]
        )  # Equivalent to np.max(first_day, axis=0, keepdims=True)

    end_time = dt.datetime.now()
    print(end_time-start_time)

    return weekly_maxima


def interpolate_weekly_maxima(weekly_max_temp_data, current_grid, target_grid):
    """
    Interpolates from the coarse, weekly max temp grid onto the higher resolution grid for the land cover classification
    """
    print("Interpolating...")
    start_time = dt.datetime.now()

    lat_min, lat_max = 30, 40  # Latitude extends from 30 - 40 degrees
    lon_min, lon_max = -104, -130.5  # Longitude extends from -104 to -130.5 degrees
    n_weeks = weekly_max_temp_data.shape[0]

    # Latitude and longitude values for the coarse grid
    current_lats = np.linspace(lat_min, lat_max, current_grid[1])
    current_lons = np.linspace(lon_min, lon_max, current_grid[2])

    # Latitude and longitude values for the high-resolution grid
    target_lats = np.linspace(lat_min, lat_max, target_grid[0])
    target_lons = np.linspace(lon_min, lon_max, target_grid[1])

    # Initialise empty array which we then write with the interpolated maximum weekly temperatures
    interpolated_weekly_maxima = np.empty((n_weeks, target_grid[0], target_grid[1]))
    interpolated_weekly_maxima[:] = np.NaN

    for week in range(n_weeks):
        weekly_data = weekly_max_temp_data[week]

        # When on a regular grid with x.size = m and y.size = n, if z.ndim == 2, then z must have shape (n, m) for interpolate.interp2d
        weekly_data_transpose = weekly_data.T
        interp = interpolate.interp2d(current_lats, current_lons, weekly_data_transpose)

        interpolated_weekly_maxima[week::] = interp(target_lats, target_lons).T

    end_time = dt.datetime.now()
    print(end_time-start_time)
    return interpolated_weekly_maxima


def find_maximum_weekly_urban_temperatures(land_cover_data, interpolated_temperature):
    """
    Finds the maximum temperatures for each urban area in each week of 2019
    """
    print ("Finding urban temperatures...")
    start_time = dt.datetime.now()
    result = [interpolated_temperature[week][np.where(land_cover_data == 13)] for week in range(interpolated_temperature.shape[0])]
    end_time = dt.datetime.now()
    print(end_time-start_time)
    return result


if __name__ == "__main__":
    land_cover_data, hourly_max_temp_data = load_datasets()
    weekly_max_temp_data = calculate_weekly_maximum_temp(hourly_max_temp_data)
    interpolated_temperature = interpolate_weekly_maxima(
        weekly_max_temp_data,
        current_grid=weekly_max_temp_data.shape,
        target_grid=land_cover_data.shape,
    )
    weekly_maximum_urban_temps = find_maximum_weekly_urban_temperatures(land_cover_data, interpolated_temperature)

    print("Saving...", flush = True)
    np.save(open("weekly_maximum_urban_temps.pkl", "wb+"), weekly_maximum_urban_temps)
    print("Done!")
