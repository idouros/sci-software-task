## Replication steps

```bash
# How do I prepare my environment?

Please unzip the supplied attachment

There are two components to the submission:

1. The main processing code itself, written as a console app in C++ using Visual Studio (used VS Community 2019, version 16.4.5). I am providing the solution/project/source files, all you need is to build and run (see below for command line arguments)

2. In order to avoid installing/building/linking the dependencies needed for loading the data files (GDAL, rasterio, etc), I have written a small python script (convert.py, it's in the "Data" subfolder). This simply reads the files and writes them as simple text files. (Yes, I know this is a bit of a hack and no, I would not do it like that in a production environment)

# How do I run the code?

- First run convert.py, this will generate the plain text versions of the data files.

- Then build the sci-software-task VS solution.

- Finally, run sci-software-task.exe, making sure that you supply exactly two arguments. The syntax is:

sci-software-task.exe land_cover_data_file hourly_max_temp_data_file

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

4. Distribution of the computation over multiple machines, and probably better streaming/division of the input data (see also #5 below)

5. There are a number of things that I have not addressed but would probably be essential in order to scale this up for bigger data. The reasons that the C++
implementation I submit is faster than the Python one supplied are:
- The inherent absence of interpreter overhead,
- The ability of modern C++ compilers to optimise SIMD operations (such as the vector operations in the interpolation funcion, in our case).
However, going forward one should consider the following:
- Further parallelise the code using multiple threads such as parallel for loops.
- Use a 3rd party library for matrix/vector math with more efficient implementation (e.g. something that involves BLAS/LAPACK)
- Deployment to GPU (e.g. CUDA).
