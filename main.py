import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import pandas as pd
from collections import Counter
import re
import matplotlib.pyplot as plt

# Google Sheets
import gspread
from google.oauth2.service_account import Credentials

# Configurar navegador
options = uc.ChromeOptions()
driver = uc.Chrome(options=options)

# Scraping
modelos = []
offset = 0
max_paginas = 50
base_url = "https://autos.mercadolibre.com.ar/autos-camionetas_Desde_{offset}_NoIndex_True"

def extraer_modelo(texto):
    texto = texto.lower()
    texto = re.sub(r"\s+\d{4}.*", "", texto)
    palabras = texto.split()
    if len(palabras) >= 2:
        return palabras[0] + " " + palabras[1]
    elif palabras:
        return palabras[0]
    return "desconocido"

for _ in range(max_paginas):
    url = base_url.format(offset=offset)
    driver.get(url)
    time.sleep(2)

    items = driver.find_elements(By.CLASS_NAME, "ui-search-item__title")
    if not items:
        break

    for item in items:
        modelo = extraer_modelo(item.text.strip())
        modelos.append(modelo)

    offset += 48

driver.quit()

# Conteo y gráfico
conteo = Counter(modelos)
df = pd.DataFrame(conteo.items(), columns=["modelo", "publicaciones"])
df = df.sort_values("publicaciones", ascending=False)

# Gráfico Top 15
top15 = df.head(15)
plt.figure(figsize=(12, 6))
plt.barh(top15["modelo"][::-1], top15["publicaciones"][::-1], color="skyblue")
plt.xlabel("Cantidad de publicaciones")
plt.title("Top 15 modelos más publicados en Mercado Libre")
plt.tight_layout()
plt.show()

# Subir a Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('credenciales.json', scopes=SCOPES)
gc = gspread.authorize(creds)

sheet_id = "1xugs7cLtz6bsdaaNi7DxLn03ApUpPLH_tIb7MlKMTiY"
sh = gc.open_by_key(sheet_id)
worksheet = sh.sheet1

worksheet.clear()
worksheet.update([df.columns.values.tolist()] + df.values.tolist())
