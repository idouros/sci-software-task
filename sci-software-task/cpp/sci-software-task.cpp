// sci-software-task.cpp : This file contains the 'main' function. Program execution begins and ends there.
//
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <algorithm>
#include <chrono>
#include <ctime>   

typedef std::vector<std::vector<int>> arr_int_2D;
typedef std::vector<std::vector<float>> arr_float_2D;
typedef std::vector<std::vector<std::vector<float>>> arr_float_3D;

// --- I/O helpers  ----------------------------------------------------------

arr_int_2D load_dataset_2d(const std::string& data_file_name)
{
	std::fstream data_file;

	data_file.open(data_file_name, std::ios::in);
	int dims;
	data_file >> dims;
	auto shape = std::vector<int>(dims);
	for (auto i = 0; i < dims; i++)
	{
		data_file >> shape[i];
	}

	auto rows = shape[1];
	auto cols = shape[0];

	arr_int_2D result;

	for (auto row = 0; row < rows; row++)
	{
		std::vector<int> v_row(cols);
		for (auto col = 0; col < cols; col++)
		{
			data_file >> v_row[col];
		}
		result.push_back(v_row);
	}

	data_file.close();
	return result;
}

arr_float_3D load_dataset_3d(const std::string& data_file_name)
{
	std::fstream data_file;

	data_file.open(data_file_name, std::ios::in);
	int dims;
	data_file >> dims;
	auto shape = std::vector<int>(dims);
	for (auto i = 0; i < dims; i++)
	{
		data_file >> shape[i];
	}

	auto lyrs = shape[0];
	auto rows = shape[2];
	auto cols = shape[1];

	arr_float_3D result;

	for (auto layer = 0; layer < lyrs; layer++)
	{
		std::vector<std::vector<float>> v_layer;
		for (auto row = 0; row < rows; row++)
		{
			std::vector<float> v_row(cols);
			for (auto col = 0; col < cols; col++)
			{
				data_file >> v_row[col];
			}
			v_layer.push_back(v_row);
		}
		result.push_back(v_layer);
	}

	data_file.close();
	return result;
}

// --- Data manipulation helpers ---------------------------------------------

std::vector<float> vec_max(const std::vector<float>& v1, const std::vector<float>& v2)
{
	std::vector<float> result(v1.size(), 0.0);
	for (size_t i = 0; i < v1.size(); i++)
	{
		result[i] = std::max<float>(v1[i], v2[i]);
	}
	return result;
}

arr_int_2D get_urban_grid_coords(const arr_int_2D& land_cover_data)
{
	arr_int_2D result;
	size_t n_rows = land_cover_data.size();
	size_t n_cols = land_cover_data[0].size();
	for (size_t row = 0; row < n_rows; row++)
	{
		for (size_t col = 0; col < n_cols; col++)
		{
			if (land_cover_data[row][col] == 13)
			{
				std::vector<int> coords = { (int)row, (int)col };
				result.push_back(coords);
			}
		}
	}
	return result;
}

arr_float_2D map_grid_to_temp(const arr_int_2D& urban_grid_coords, const int& temp_rows, const int& temp_cols, const int& grid_rows, const int& grid_cols)
{
	auto n_points = urban_grid_coords.size();

	auto f_rows = (float)(temp_rows - 1) / (float)(grid_rows - 1);
	auto f_cols = (float)(temp_cols - 1) / (float)(grid_cols - 1);

	arr_float_2D result;

	for (size_t i = 0; i < n_points; i++)
	{
		auto row_in = urban_grid_coords[i][0];
		auto col_in = urban_grid_coords[i][1];

		auto row_out = row_in * f_rows;
		auto col_out = col_in * f_cols;

		std::vector<float> coords_out = { row_out, col_out };
		result.push_back(coords_out);
	}

	return result;
}

std::vector<float> calculate_interpolated_weekly_temperatures(const arr_float_2D& urban_temp_coords, const arr_float_2D& weekly_data)
{

	auto n_temp_points = urban_temp_coords.size();

	size_t max_x = weekly_data[0].size() - 1;
	size_t max_y = weekly_data.size() - 1;

	std::vector<float> x(n_temp_points, 0);
	std::vector<float> y(n_temp_points, 0);

	std::vector<size_t> x1(n_temp_points, 0);
	std::vector<size_t> x2(n_temp_points, 0);
	std::vector<size_t> y1(n_temp_points, 0);
	std::vector<size_t> y2(n_temp_points, 0);

	std::vector<float> f11(n_temp_points, 0);
	std::vector<float> f12(n_temp_points, 0);
	std::vector<float> f21(n_temp_points, 0);
	std::vector<float> f22(n_temp_points, 0);

	std::vector<float> dx2x(n_temp_points, 0);
	std::vector<float> dy2y(n_temp_points, 0);
	std::vector<float> dxx1(n_temp_points, 0);
	std::vector<float> dyy1(n_temp_points, 0);

	std::vector<float> result(n_temp_points, 0);


	for (size_t i = 0; i < n_temp_points; i++)
	{
		x[i] = urban_temp_coords[i][1];
		y[i] = urban_temp_coords[i][0];

		x1[i] = (int)floor(x[i]);
		x2[i] = std::min<size_t>(x1[i] + 1, max_x);
		y1[i] = (int)floor(y[i]);
		y2[i] = std::min<size_t>(y1[i] + 1, max_y);

		f11[i] = weekly_data[y1[i]][x1[i]];
		f12[i] = weekly_data[y1[i]][x2[i]];
		f21[i] = weekly_data[y2[i]][x1[i]];
		f22[i] = weekly_data[y2[i]][x2[i]];

		dx2x[i] = (float)(x2[i] - x[i]);
		dy2y[i] = (float)(y2[i] - y[i]);
		dxx1[i] = (float)(x[i] - x1[i]);
		dyy1[i] = (float)(y[i] - y1[i]);

		result[i] =
			(f11[i] * dx2x[i] * dy2y[i]) +
			(f21[i] * dxx1[i] * dy2y[i]) +
			(f12[i] * dx2x[i] * dyy1[i]) +
			(f22[i] * dxx1[i] * dyy1[i]);
	}

	return result;
}

// ---------------------------------------------------------------------------

arr_float_3D calculate_weekly_maximum_temp(const arr_float_3D hourly_max_temp_data)
{
	auto start = std::chrono::system_clock::now();

	arr_float_3D weekly_maxima;
	auto hours_in_a_week = 24 * 7;
	size_t n_layers = hourly_max_temp_data.size();
	size_t n_rows = hourly_max_temp_data[0].size();
	size_t n_cols = hourly_max_temp_data[0][0].size();

	std::cout << "Calculating weekly maximum temperatures... " << std::endl;


	for (auto week = 0; week < 52; week++)
	{
		arr_float_2D weekly_slice;

		auto start_hour = hours_in_a_week * week;
		auto end_hour = hours_in_a_week * (week + 1);

		for (size_t row = 0; row < n_rows; row++)
		{
			std::vector<float> row_of_maxima(n_cols, std::numeric_limits<float>::min());
			for (auto hour = start_hour; hour < end_hour; hour++)
			{
				auto current_row = hourly_max_temp_data[hour][row];
				row_of_maxima = vec_max(row_of_maxima, current_row);
			}
			weekly_slice.push_back(row_of_maxima);
		}
		weekly_maxima.push_back(weekly_slice);
	}

	auto end = std::chrono::system_clock::now();
	std::chrono::duration<double> elapsed_seconds = end - start;
	std::time_t end_time = std::chrono::system_clock::to_time_t(end);
	std::cout << "elapsed time: " << elapsed_seconds.count() << "s\n";

	return weekly_maxima;
}

arr_float_2D interpolate_urban_weekly_maxima(const arr_float_3D & weekly_max_temp_data, const arr_int_2D& land_cover_data)
{
	auto start = std::chrono::system_clock::now();
	arr_float_2D result;
	std::cout << "Interpolating..." << std::endl;
	auto urban_grid_coords = get_urban_grid_coords(land_cover_data);
	auto n_urban_grid_coords = urban_grid_coords.size();
	auto n_weeks = weekly_max_temp_data.size();

	auto temp_rows = weekly_max_temp_data[0].size();
	auto temp_cols = weekly_max_temp_data[0][0].size();
	auto grid_rows = land_cover_data.size();
	auto grid_cols = land_cover_data[0].size();

	auto urban_temp_coords = map_grid_to_temp(urban_grid_coords, temp_rows, temp_cols, grid_rows, grid_cols);

	for (size_t week = 0; week < n_weeks; week++)
	{
		auto weekly_data = weekly_max_temp_data[week];
		auto weekly_temps = calculate_interpolated_weekly_temperatures(urban_temp_coords, weekly_data);
		result.push_back(weekly_temps);
 	}

	auto end = std::chrono::system_clock::now();
	std::chrono::duration<double> elapsed_seconds = end - start;
	std::time_t end_time = std::chrono::system_clock::to_time_t(end);
	std::cout << "elapsed time: " << elapsed_seconds.count() << "s\n";

	return result;
}


// ---------------------------------------------------------------------------

int main(int argc, char** argv)
{
	if (argc != 3)
	{
		std::cout << "Syntax: sci-software-task.exe land_cover_data_file hourly_max_temp_data_file" << std::endl;
		return -1;
	}

	auto lcc_filename = argv[1];
	auto hmt_filename = argv[2];

	std::cout << "Reading land cover data..." << std::endl;
	auto land_cover_data = load_dataset_2d(lcc_filename);

	std::cout << "Reading temperature data..." << std::endl;
	auto hourly_max_temp_data = load_dataset_3d(hmt_filename);

	auto weekly_max_temp_data = calculate_weekly_maximum_temp(hourly_max_temp_data);
	auto weekly_maximum_urban_temps = interpolate_urban_weekly_maxima(weekly_max_temp_data, land_cover_data);

	std::cout << "Done!" << std::endl;

	// yes, normally around here we would save the end result (weekly_maximum_urban_temps) in an appropriate format.
	return 0;
}

