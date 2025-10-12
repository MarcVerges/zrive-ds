# import orher files
import src.module_1.module_1_functions as func
import src.module_1.module_1_variables as vars


def main():
    data_cities = []
    for city, coords in vars.COORDINATES.items():
        ret_data_raw = func.get_data_meteo_api(coords["latitude"], coords["longitude"])

        if ret_data_raw is not None:
            units = {}
            ret_data_raw_matrix, units = func.process_city_data(
                city, ret_data_raw, units
            )
            ret_data_means_matrix = func.means_city_data(ret_data_raw_matrix)
            data_cities.append(ret_data_means_matrix)
        else:
            pass

    ret_data_separated = func.unite_matrix(data_cities)
    func.plot_info(ret_data_separated, vars.VARIABLES, units)


if __name__ == "__main__":
    main()
