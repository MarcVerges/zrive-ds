# Datos simulados válidos
mock_data = {
    "daily": {
        "time": ["2022-07-01", "2022-07-02", "2022-07-03"],
        "temperature_2m_mean": [25, 26, 24],
        "precipitation_sum": [0.0, 0.5, 0.0],
        "wind_speed_10m_max": [5, 6, 4],
    },
    "daily_units": {
        "temperature_2m_mean": "°C",
        "precipitation_sum": "mm",
        "wind_speed_10m_max": "m/s",
    },
}


# Datos simulados inválidos

mock_invalid_data = {"daily": {}, "daily_units": {}}
