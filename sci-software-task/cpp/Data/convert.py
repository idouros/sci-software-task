import numpy as np
import rasterio

def load_datasets():
    """
    Loads the two target datasets from disk into memory.
    """
    print("Reading temperature data...")
    hourly_max_temp_data = rasterio.open("./hourly_max_temp_2019.nc").read()
    print("Reading land cover data...")
    land_cover_data = rasterio.open("./land_cover_classification.tiff").read()[0]  # There's only a single band in this dataset - just return that
    return land_cover_data, hourly_max_temp_data

def save_dataset_2d(dataset, filename):

    shp = dataset.shape
    dims = len(shp)
    rows = shp[0]
    cols = shp[1]

    with open(filename, 'w') as f:
        f.write(str(dims) + '\n')
        f.write(str(rows) + '\n')
        f.write(str(cols) + '\n')

        for row in range(0, rows):
            for col in range(0, cols):
                f.write(str(dataset[row][col]) + '\n')


def save_dataset_3d(dataset, filename):

    shp = dataset.shape
    dims = len(shp)
    lyrs = shp[0]
    rows = shp[1]
    cols = shp[2]

    with open(filename, 'w') as f:
        f.write(str(dims) + '\n')
        f.write(str(lyrs) + '\n')
        f.write(str(rows) + '\n')
        f.write(str(cols) + '\n')

        for lyr in range(0, lyrs): 
            for row in range(0, rows):
               for col in range(0, cols):
                    f.write(str(dataset[lyr][row][col]) + '\n')


if __name__ == "__main__":
    
    land_cover_data, hourly_max_temp_data = load_datasets()

    print(land_cover_data.shape)
    save_dataset_2d(land_cover_data, "land_cover_classification.txt")
    
    print(hourly_max_temp_data.shape)
    save_dataset_3d(hourly_max_temp_data, "hourly_max_temp_2019.txt")
    
    print("Done!")
