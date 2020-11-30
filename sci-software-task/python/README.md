# Senior Scientific Software Engineer - Technical Task

Welcome to the technical task for the Senior Scientific Software Engineer!

The task is to help out a scientist with code that they have written in Python. The code calculates, for each week in 2019, the maximum temperature for each urban area in California.

Your task is as follows:

> Can you help the scientist to improve their code's performance?

To help with the task, we've provided 2 data files (which we outline in the [Data Specification](#data-specification) section) and the scientists' Python implementation which answers this question. You may use this code as a starting point, or re-implement the problem in a different language.

We'd like to see some evidence of low-level programming skills, but are agnostic about how you do that - if you wish to call out to some C code that you've written from within Python, write it completely in Fortran or can show that another choice would be fastest, that's fine by us.

We will want to run your code for benchmarking purposes, so please make sure that it is replicable!

## Data Specification

We provide two datasets for you to complete this task:

1. land_cover_classification.tiff
2. max_temp_2019.nc

Both datasets cover the same region of California. The maximum latitudes and longitudes are as follows:

```python
lat_min, lat_max = 30, 40  # Latitude extends from 30 to 40 degrees
lon_min, lon_max = -104, -130.5  # Longitude extends from -104 to -130.5 degrees
```

The land cover classification data is a grid of integer values which correspond to a catgeory of land classification. The only value you actually need is the urban environment, which has an integer value of 13. For completeness, the complete mapping from integer to category is defined in the [Land cover classification table](#land-cover-classification-table). The data is defined on a 1194 x 3177 grid. The land cover is assumed to be constant for the year of 2019. This is provided in a TIFF file, denoted bt the .tiff extension.

The maximum temperature data provides the maximum temperature at each point on a 41 x 107 grid for each hour in 2019. This is provided in a NetCDF file, denoted by the .nc extension. 

Both TIFFs and NetCDF files are common data format in geospatial domains, for which there are libraries available to read the input data. GDAL, for instance, is implemented in C and the gdal binary (`sudo apt-get install -y gdal-bin`) provided by apt-get can parse both formats. GDAL also has bindings in Rust and other languages. 

## Tips

* There are a few components to focus on in this problem - it is possible that a full re-implementation will take longer than 3 hours in a low-level language. You might instead choose to only cover a part of the problem. You could choose just one which:
  *  you think is most interesting,
  *  currently represents the biggest bottleneck, or
  *  can be used to demonstrate passing data between different runtimes easily

*  The 4 principal components to this code are:
  1. Loading the data into memory
  2. Aggregating the temperature data
  3. Interpolating the aggregated temperature data
  4. Subsetting/filtering the land cover data for the urban areas only and looking up the corresponding maximum temperature

* Don't worry too much about the shape of the output data for the purposes of this task. You'll see that the Python implementation simply dumps the data to disk in binary Python format (pickle). If your wish to format it in some other (more sensible) way, that's a nice-to-have.

## Submitting the task

You can see a sample submission file in SAMPLE_SUBMISSION.md

This contains space for replication steps and a few questions to think about. This need only be a few lines per question.

We don't expect you to spend more than 3 hours or so on the task. If you have ideas for further optimizations that would push you beyond this timeframe, please outline those in your submission.

Please send submissions to tom@cervest.earth, including as an attachment any code you write. We look forward to reading your submissions!

## Questions

If you've any questions regarding completing or submitting the task, please reach out to me at tom@cervest.earth

## Appendix

### Land cover classification table

| Name                                | Value | Description                                                                                          |
|-------------------------------------|-------|------------------------------------------------------------------------------------------------------|
| Evergreen Needleleaf Forests        | 1     | Dominated by evergreen conifer trees (canopy > 2m). Tree cover >60%.                                 |
| Evergreen Broadleaf Forests         | 2     | Dominated by evergreen broadleaf and palmate trees (canopy >2m). Tree cover >60%.                    |
| Deciduous Needleleaf Forests        | 3     | Dominated by deciduous needleleaf (larch) trees(canopy >2m). Tree cover >60%.                        |
| Deciduous Broadleaf Forests         | 4     | Dominated by deciduous broadleaf trees (canopy>2m). Tree cover >60%.                                 |
| Mixed Forests                       | 5     | Dominated by neither deciduous nor evergreen(40-60% of each) tree type (canopy >2m). Treecover > 60%.|
| Closed Shrublands                   | 6     | Dominated by woody perennials (1-2m height). > 60% cover.                                            |
| Open Shrublands                     | 7     | Dominated by woody perennials (1-2m height). 10-60% cover.                                           |
| Woody Savannas                      | 8     | Tree cover 30-60% (canopy >2m).                                                                      |
| Savannas                            | 9     | Tree cover 10-30% (canopy >2m).                                                                      |
| Grasslands                          | 10    | Dominated by herbaceous annuals (<2m).                                                               |
| Permanent Wetlands                  | 11    | Permanently inundated lands with 30-60% water cover and >10% vegetated cover.                        |
| Croplands                           | 12    | At least 60% of area is cultivated cropland.                                                         |
| Urban and Built-up Lands            | 13    | At least 30% impervious surface area including building materials, asphalt, and vehicles.            |
| Cropland/Natural Vegetation Mosaics | 14    | Mosaics of small-scale cultivation 40-60% with natural tree, shrub, or herbaceous vegetation.        |
| Permanent Snow and Ice              | 15    | At least 60% of area is covered by snow and ice for at least 10 months of the year.                  |
| Barren                              | 16    | At least 60% of area is non-vegetated barren (sand, rock, soil) areas with less than 10% vegetation. |
| Water Bodies                        | 17    | At least 60% of area is covered by permanent water bodies.                                           |
| Unclassified                        | 255   | Has not received a map label because of missing inputs.                                              |

### Land cover data image

![land-cover-image](static/land_cover.png)
