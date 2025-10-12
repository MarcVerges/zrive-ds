import src.module_1.module_1_functions as func
import tests.module_1.test_meteo_variables as var
import pytest
import pandas as pd


# Test de generic_API_call


def test_generic_API_call(monkeypatch):
    # Mock de requests.get para no hacer llamadas reales
    class MockResponse:
        status_code = 200

        def json(self):
            return {"success": True}

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        "requests.get", mock_get
    )  # informa de que se use un get falso cuando se hace request.get

    result = func.generic_API_call("http://fakeurl.com")
    assert result == {"success": True}


# Test de validate_schema


def test_validate_schema():
    # Datos válidos
    assert func.validate_schema(var.mock_data) is True
    # Datos inválidos
    assert func.validate_schema(var.mock_invalid_data) is False


# Test de get_data_meteo_api


def test_get_data_meteo_api(monkeypatch):
    # Mock de generic_API_call y validate_schema
    monkeypatch.setattr(
        func, "generic_API_call", lambda url, cooldown, tries, params: var.mock_data
    )
    # cada vez que hacemos llamada a generci api call asumimos que
    # nos devulve mock data
    monkeypatch.setattr(
        func, "validate_schema", lambda answ: True
    )  # cada vez que se valida el schema asumimos que es valido

    result = func.get_data_meteo_api(
        52.52, 13.41
    )  # le damos las cordenadas que tenemos en mock data
    assert (
        result == var.mock_data
    )  # comporvamos que no haya habido ninguna distorion de los datos


# Test de process_city_data


def test_process_city_data():
    units_ret = {}
    df, units_out = func.process_city_data("Berlin", var.mock_data, units_ret)
    assert isinstance(df, pd.DataFrame)
    assert "city" in df.columns
    assert units_out["temperature_2m_mean"] == "°C"


# Test de means_city_data


def test_means_city_data():
    df, _ = func.process_city_data("Berlin", var.mock_data, {})
    monthly_df = func.means_city_data(df)
    assert isinstance(monthly_df, pd.DataFrame)  # comprueba que sea un data frame
    assert "city" in monthly_df.columns  # comprueba que se mantenga city
    # Validar promedio mensual
    assert monthly_df["temperature_2m_mean"].iloc[0] == pytest.approx(
        df["temperature_2m_mean"].mean()
    )  # comprueba que la media coicida


# Test de unite_matrix


def test_unite_matrix():
    df, _ = func.process_city_data("Berlin", var.mock_data, {})
    monthly_df = func.means_city_data(df)
    result = func.unite_matrix([monthly_df])
    assert isinstance(result, list)  # compruva que el retorno sea una lista
    assert len(result) == 3
    assert all(
        isinstance(x, pd.DataFrame) for x in result
    )  # compreba que cada elemento de salida es un dataframe
