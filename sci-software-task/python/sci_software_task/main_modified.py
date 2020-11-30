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
    start_time = dt.datetime.now()
    print("Reading temperature data...")
    hourly_max_temp_data = rasterio.open("../data/hourly_max_temp_2019.nc").read()
    print("Reading land cover data...")
    land_cover_data = rasterio.open("../data/land_cover_classification.tiff").read()[0]  # There's only a single band in this dataset - just return that
    
    end_time = dt.datetime.now()
    print(end_time-start_time)
    print("Output: ", land_cover_data.shape, hourly_max_temp_data.shape, "\n___________________________________________")
    return land_cover_data, hourly_max_temp_data


def calculate_weekly_maximum_temp(hourly_max_temp_data):
    """
    Calculates the weekly maximum temperatures, given the hourly maximum temperatures.
    """
    print("Calculating weekly maximum temperatures... ")
    start_time = dt.datetime.now()
    print(" Input: ", hourly_max_temp_data.shape)

    # Initialise empty array which we then write with the calculated maximum weekly temperatures
    weekly_maxima = np.empty((52, 41, 107))
    weekly_maxima[:] = np.NaN

    hours_in_a_week = 24 * 7

    for week in range(0, 52):
        start_hour = hours_in_a_week * week
        end_hour = hours_in_a_week * (week + 1)
        weekly_slice = hourly_max_temp_data[start_hour:end_hour,:,:]
        weekly_maxima[week] = weekly_slice.max(axis = 0, keepdims = True)

    end_time = dt.datetime.now()
    print(end_time-start_time)
    print("Output: ", weekly_maxima.shape, "\n___________________________________________")
    return weekly_maxima


def map_grid_to_temp(urban_grid_coords, temp_rows, temp_cols, grid_rows, grid_cols):

    n_points = urban_grid_coords.shape[0]

    row_coords_in = urban_grid_coords[:,0].reshape([n_points, 1])
    row_coords_out = row_coords_in * (temp_rows-1) / (grid_rows-1)

    col_coords_in = urban_grid_coords[:,1].reshape([n_points, 1])
    col_coords_out = col_coords_in * (temp_cols-1) / (grid_cols-1)

    return np.concatenate((row_coords_out, col_coords_out), axis = 1)

def calculate_interpolated_weekly_temperatures(urban_temp_coords, weekly_data):
    
    n_temp_points = urban_temp_coords.shape[0]
    result = [0] * n_temp_points

    max_x = weekly_data.shape[1]-1
    max_y = weekly_data.shape[0]-1

    x = urban_temp_coords[:,1]
    y = urban_temp_coords[:,0]
    x1 = np.floor(x).astype(int)
    x2 = np.minimum(x1 + 1, max_x).astype(int)
    y1 = np.floor(y).astype(int)
    y2 = np.minimum(y1 + 1, max_y).astype(int)

    f11 = np.empty([n_temp_points,])
    f12 = np.empty([n_temp_points,])
    f21 = np.empty([n_temp_points,])
    f22 = np.empty([n_temp_points,])

    for i in range(0, n_temp_points):
        f11[i] = weekly_data[y1[i]][x1[i]]
        f12[i] = weekly_data[y1[i]][x2[i]]
        f21[i] = weekly_data[y2[i]][x1[i]]
        f22[i] = weekly_data[y2[i]][x2[i]]

    dx2x = x2 - x
    dy2y = y2 - y
    dxx1 = x - x1
    dyy1 = y - y1

    s11 = np.multiply(np.multiply(f11, dx2x), dy2y)
    s21 = np.multiply(np.multiply(f21, dxx1), dy2y)
    s12 = np.multiply(np.multiply(f12, dx2x), dyy1)
    s22 = np.multiply(np.multiply(f22, dxx1), dyy1)

    result = s11 + s21 + s12 + s22
    return result

def interpolate_urban_weekly_maxima(weekly_max_temp_data, land_cover_data):
    """
    Interpolates from the coarse, weekly max temp grid onto the higher resolution grid for the land cover classification
    """
    print("Interpolating...")
    start_time = dt.datetime.now()
    print(" Input: ", weekly_max_temp_data.shape, land_cover_data.shape)

    urban_grid_coords = np.argwhere(land_cover_data==13)
    n_urban_grid_coords = urban_grid_coords.shape[0]
    n_weeks = weekly_max_temp_data.shape[0]
    result = [np.array(n_urban_grid_coords,)] * n_weeks

    temp_rows = weekly_max_temp_data.shape[1]
    temp_cols = weekly_max_temp_data.shape[2]
    grid_rows = land_cover_data.shape[0]
    grid_cols = land_cover_data.shape[1]

    urban_temp_coords = map_grid_to_temp(urban_grid_coords, temp_rows, temp_cols, grid_rows, grid_cols)

    result = []
    for week in range(n_weeks):
        weekly_data = weekly_max_temp_data[week]
        weekly_temps = calculate_interpolated_weekly_temperatures(urban_temp_coords, weekly_data)
        result.append(weekly_temps)

    end_time = dt.datetime.now()
    print(end_time-start_time)
    print("Output: ", len(result), result[0].shape, "\n___________________________________________")
    return result

if __name__ == "__main__":
    land_cover_data, hourly_max_temp_data = load_datasets()
    weekly_max_temp_data = calculate_weekly_maximum_temp(hourly_max_temp_data)
    weekly_maximum_urban_temps = interpolate_urban_weekly_maxima(
        weekly_max_temp_data,
        land_cover_data
    )

    print("Saving...", flush = True)
    np.save(open("weekly_maximum_urban_temps.pkl", "wb+"), weekly_maximum_urban_temps)
    print("Done!")
