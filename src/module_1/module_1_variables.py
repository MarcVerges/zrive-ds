# definition of Static variables (Constants) for the code


# Gestión de las ciudades pedidas
COORDINATES = {
    "Madrid": {"latitude": 40.416775, "longitude": -3.703790},
    "London": {"latitude": 51.507351, "longitude": -0.127758},
    "Rio": {"latitude": -22.906847, "longitude": -43.172896},
}


# Gestión de los datos pedidos a la API
VARIABLES = ["temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max"]
TIME_SPAN = ["2010-01-01", "2020-12-31"]


# Gestión de la connexión de la API
API_URL = "https://archive-api.open-meteo.com/v1/archive?"
COOL_DOWN = 10
MAX_TRIES = 3
