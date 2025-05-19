import random
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from bs4 import BeautifulSoup as bs
import re
import os
from datetime import date
import duckdb
import requests

def obtener_dolar_oficial():
    """
    Obtiene el valor promedio del dólar oficial desde la API de BlueLyctics.
    """
    url = "https://api.bluelytics.com.ar/v2/latest"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        compra = data['oficial']['value_buy']
        venta = data['oficial']['value_sell']
        return (compra + venta) / 2
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los datos del dólar: {e}")
        return None

dolar_oficial = obtener_dolar_oficial()

if dolar_oficial is None:
    print("No se pudo obtener el valor del dólar. El script finalizará.")
    exit()

# === CONFIGURACIÓN DEL USUARIO ===
# Reemplazar con la ruta local al CSV con los modelos
ruta_listado = r"TU_RUTA_LOCAL/listado_autos.csv"

# Reemplazar con la ruta local donde guardar el archivo Parquet
ruta_parquet = r"TU_RUTA_LOCAL/autos_usados_filtrados.parquet"
# ================================

# Leer modelos del archivo
df_modelos = pd.read_csv(ruta_listado, header=None)
modelos = df_modelos[0].tolist()

# Parámetros comunes
max_paginas = 1
filtros = "Capital-Federal"
fecha_hoy = date.today().isoformat()
browser = uc.Chrome()

# Crear una conexión en memoria a DuckDB
con = duckdb.connect(database=':memory:', read_only=False)

# Crear tabla vacía en DuckDB
con.execute("""
    CREATE TABLE autos_usados (
        Modelo VARCHAR,
        Título VARCHAR,
        Precio VARCHAR,
        Año VARCHAR,
        Kilometraje VARCHAR,
        "Fecha de registro" VARCHAR,
        URL VARCHAR
    )
""")

# Iterar cada modelo
for modelo_auto in modelos:
    modelo_url = modelo_auto.replace(" ", "-")

    for x in range(1, max_paginas + 1):
        offset = (x - 1) * 48
        url = (
            f"https://autos.mercadolibre.com.ar/{modelo_url}/dueno-directo/{filtros}/"
            f"_Desde_{offset}"
        )
        browser.get(url)
        time.sleep(random.randint(8, 10))

        # Scroll
        body = browser.find_element("tag name", "body")
        body.send_keys(Keys.END)
        time.sleep(random.randint(2, 4))

        soup = bs(browser.page_source, "html.parser")
        autos = soup.find_all("li", class_="ui-search-layout__item")

        datos_para_insertar = []
        for auto in autos:
            try:
                link = auto.find("a", class_="poly-component__title")["href"]
                titulo = auto.find("a", class_="poly-component__title").get_text(strip=True)
            except:
                titulo = "No disponible"
                link = "No disponible"

            try:
                precio_texto = auto.find("span", class_="andes-money-amount__fraction").get_text(strip=True).replace(".", "")
                moneda = auto.find("span", class_="andes-money-amount__currency-symbol").get_text(strip=True)
                precio = f"{moneda} {precio_texto}"
            except:
                precio = "No disponible"

            try:
                ubicacion = auto.select_one("span.poly-component__location").get_text(strip=True)
            except:
                ubicacion = "No disponible"

            try:
                atributos = auto.select("ul.poly-attributes-list li")
                if len(atributos) >= 2:
                    año = atributos[0].get_text(strip=True)
                    km = atributos[1].get_text(strip=True)
                else:
                    año = "No disponible"
                    km = "No disponible"
            except:
                año = "No disponible"
                km = "No disponible"

            datos_para_insertar.append((
                modelo_auto,
                titulo,
                precio,
                año,
                km,
                fecha_hoy,
                link
            ))

        if datos_para_insertar:
            con.executemany("""
                INSERT INTO autos_usados (Modelo, Título, Precio, Año, Kilometraje, "Fecha de registro", URL)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, datos_para_insertar)

    print(f"✅ Datos recolectados para: {modelo_auto}")

browser.quit()

# Tabla final limpia con transformaciones
con.execute(f"""
    CREATE OR REPLACE TABLE autos_usados_limpio AS
    SELECT
        Modelo,
        Título,
        Precio,
        Año,
        Kilometraje,
        "Fecha de registro",
        URL,
        CASE
            WHEN Precio LIKE 'US$ %' THEN CAST(REPLACE(Precio, 'US$ ', '') AS DOUBLE)
            ELSE CAST(REPLACE(REPLACE(Precio, '$', ''), '.', '') AS DOUBLE) / {dolar_oficial}
        END AS "Precio US$",
        CAST(REPLACE(REPLACE(REPLACE(Kilometraje, '.', ''), 'Km', ''), ' ', '') AS INTEGER) AS "Kilometraje Num"
    FROM autos_usados
    WHERE REPLACE(REPLACE(REPLACE(Kilometraje, '.', ''), 'Km', ''), ' ', '') != '0'
""")

# Exportar a Parquet incluyendo la URL
con.execute(f"""
    COPY autos_usados_limpio TO '{ruta_parquet}' (FORMAT 'parquet')
""")

con.close()

print("✅ Archivo Parquet generado con éxito.")


