## Replication steps

```bash
# How do I prepare my environment?

I have chosen to alter the existing python code rather than write in another language. Not introducing any further dependencies, so if you are set up to run main.py, then you are set up to run main_modified.py - The only (very minor) challenge is to install GDAL and rasterio by picking the correct versions of the wheels that match your version of Python - I am using 3.8.6 (64-bit)

# How do I run the code?

Just run main_modified.py
```

## Questions

1. What are the biggest bottlenecks in this operation?
2. Is the order of operations important in this scenario? What would happen if we performed the interpolation before calculating the daily maximum?
3. We currently perform a bilinear interpolation. How might you expect the performance, CPU usage and memory usage to change, if we were to use a more elaborate interpolation method e.g. spline interpolation?
4. What are the major challenges in scaling this operation to cover a larger area, such as a continent or the entire globe?
5. Are there any other remarks you'd like to make, or ideas you would purse with more time?

## Answers

1. Owing to a bug in the original version of main.py, the slowest part of the operation appeared (incorrectly) to be in calculating the maximum temperatures. So, I refactored that part tp run faster, discovered the bug, and fixed in the original. Taking the timings again, it turned out that my changes do indeed accelerate that function, but the gain is not as significant as thought at first (it's 0.05 secs down from 0.19 secs, rather than down from 18s as main.py was before the fix). 

Following that, it becomes evident that the biggest bottleneck (other than the file i/o) is the interpolation.

One observation is that the given implementations interpolates the temperatures of every single point in the 1194x3177 grid, that's 3793338. However, we actually need the interpolated values only for the points that correspond to urban areas, and it turns out there is 32227 of them. I am therefore providing a low-level implementation that does that.

2. Order of calculate_weekly_maximum_temp -> interpolate_weekly_maxima is important for performance. If we were to calculate the interpolation for each hour rather than for each week, that would mean interpolating 8760 times in a for-loop, rather than 52. We don't want that. Furthermore, passing the result of the interpolation (8760, 1194, 3177) to the weekly max calculation would mean calculating the weekly maxima on 3793338 points rather than on 4387.

3. We can expect square or even cubic complexity, depending on the exact variant of interpolation used.
4. Distribution of the computation over multiple machines, and probably better streaming/division of the input data.
5. I would probably look into developing a version of interp2d capable of operating on a mask (i.e. only on the points of interest, rather than everywhere.)
