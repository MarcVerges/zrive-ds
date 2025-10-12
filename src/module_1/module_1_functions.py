import src.module_1.module_1_variables as vars
import requests
import time
import pandas as pd
import matplotlib.pyplot as plt
import jsonschema as jssch


# Evaluation of the different status codes
def generic_API_call(
    url: str, cooldown=10, tries=3, params: dict = None
) -> dict | None:
    for attempt in range(tries):
        try:
            # puedes usar mejor urlencode (API_url + urlencode(params,safe=",),headers)
            response = requests.get(url, params=params)

            if response.status_code == 200:
                return response.json()

            elif response.status_code == 404:
                print("Servidor no encuentra recurso solicitado (404)")

            elif response.status_code == 500:
                print("Error interno del servidor (500)")

            else:
                print(f"Error inesperado: {response.status_code}")

        except requests.RequestException as e:
            print(f"Error en la solicitud: {e}")

        # Espera antes de intentar de nuevo
        # Podrias haber hecho un incremento exponencial.
        time.sleep(cooldown)

    print(f"No se obtuvo respuesta después de {tries} intentos")

    return None


# Validate estructure of the answer of the API :
def validate_schema(answ: dict):
    daily_props = {
        var: {"type": "array", "items": {"type": "number"}} for var in vars.VARIABLES
    }
    daily_props["time"] = {"type": "array", "items": {"type": "string"}}

    # Creamos las propiedades de 'daily_units', que deben ser strings
    daily_units_props = {var: {"type": "string"} for var in vars.VARIABLES}

    schema = {
        "type": "object",
        "properties": {
            "daily": {  # debe existir la sección 'daily'
                "type": "object",
                "properties": daily_props,
                "required": ["time"]
                + vars.VARIABLES,  # todas las variables son obligatorias + tiempo
            },
            "daily_units": {  # debe existir la sección 'daily_units'
                "type": "object",
                "properties": daily_units_props,
                "required": vars.VARIABLES,  # todas las variables son obligatorias
            },
        },
        "required": ["daily", "daily_units"],  # deben existir estas secciones
    }

    try:
        jssch.validate(instance=answ, schema=schema)
        return True

    except jssch.ValidationError as e:
        print("JSON inválido", e)
        return False


# Call of the API itsefl
def get_data_meteo_api(lat: float, lon: float) -> any:
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": vars.TIME_SPAN[0],
        "end_date": vars.TIME_SPAN[1],
        "daily": ",".join(vars.VARIABLES),
        "timezone": "auto",
    }

    ret = generic_API_call(vars.API_URL, vars.COOL_DOWN, vars.MAX_TRIES, params=params)

    if ret is not None:
        schematicValid = validate_schema(ret)

        if schematicValid:
            return ret
        else:
            return None


def process_city_data(
    city: str, data: dict, units_ret: dict
) -> tuple[pd.DataFrame, dict]:
    # recive un diccionario de ciudad, datos y generamos una matriz a partir de ello

    # cojemos las unidades i las tratamos para que no haya conflicto
    # de nombres en la matrix
    units = data["daily_units"]

    for tag, key in units.items():
        if tag not in units_ret:
            units_ret[tag] = key

    # cojemos los datos
    daily = data["daily"]  # seleccionamos los datos de temp,viento,precipi

    # creamos la matriz
    matrix = pd.DataFrame(daily)  # matriz de los datos
    matrix["time"] = pd.to_datetime(
        matrix["time"]
    )  # ponemos los tiempos en formato tiempo
    matrix["city"] = city

    return matrix, units_ret


def means_city_data(matrix: pd.DataFrame) -> pd.DataFrame:
    # recive una matriz con datos diarios i devuelve una matriz solo con los meses
    # y años y su media

    monthly_mean_matrix = (
        matrix.resample("ME", on="time")
        .agg(
            {  # ME indica que lo haga por meses en la columna tiempo
                "temperature_2m_mean": "mean",  # promedio mensual
                "precipitation_sum": "sum",  # promedio mensual
                "wind_speed_10m_max": "max",
            }
        )
        .reset_index()
    )

    # volvemos a añadir la columna de ciudad i cortamos el valor de los dias
    monthly_mean_matrix["city"] = matrix["city"]
    monthly_mean_matrix["time"] = monthly_mean_matrix["time"].dt.strftime(
        "%Y-%m"
    )  # dt = datetime operaciones de pandas

    return monthly_mean_matrix


def unite_matrix(matrix_list: list[pd.DataFrame]) -> list[pd.DataFrame]:
    # creamos 3 matrizes nuevas, cada una con 3 columnas, una de las temperaturas,
    # otra del viento, etc.

    temperature = pd.DataFrame()
    precipitation = pd.DataFrame()
    wind_speed = pd.DataFrame()

    for i in range(len(matrix_list)):
        city_name = matrix_list[i]["city"].iloc[
            0
        ]  # toma el nombre de ciudad como string
        temperature["time"] = matrix_list[i]["time"].values
        temperature[city_name] = matrix_list[i]["temperature_2m_mean"].values

        precipitation["time"] = matrix_list[i]["time"].values
        precipitation[city_name] = matrix_list[i]["precipitation_sum"].values

        wind_speed["time"] = matrix_list[i]["time"].values
        wind_speed[city_name] = matrix_list[i]["wind_speed_10m_max"].values

    lista_matrizes_sep = [temperature, precipitation, wind_speed]

    return lista_matrizes_sep


def plot_info(
    data_list: list[pd.DataFrame], variable_names: list[str], units: dict
) -> None:
    colors = ["red", "green", "blue"]

    for i, df in enumerate(data_list):
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"], format="%Y-%m")  # asegurar fechas
        df = df.set_index("time")

        plt.figure(figsize=(12, 6))
        for j in range(len(df.columns)):
            colname = df.columns[j]
            color = colors[j % len(colors)]
            plt.plot(df.index, df[colname], label=colname, color=color)

        plt.title(f"Evolución de valores en el tiempo - {variable_names[i]}")
        plt.xlabel("Tiempo")
        plt.ylabel(f"Valor - {units[variable_names[i]]} ")
        plt.legend()
        plt.grid(True)
        plt.show()
