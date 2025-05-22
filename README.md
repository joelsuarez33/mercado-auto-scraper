---

<h2 align="center">📊 ¿Qué hace este proyecto?</h2>

<p align="center">
  ✅ Recorre automáticamente un listado predefinido de modelos de vehículos.<br>
  ✅ Realiza scraping en Chrome de las publicaciones más relevantes por modelo,<br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;según la cantidad de páginas configurada.<br>
  ✅ Guarda los datos en formato <code>.parquet</code> para optimizar espacio y velocidad.<br>
  ✅ El archivo <code>.pbix</code> incluido resume la información mediante un dashboard en Power BI:<br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• Evolución de precios promedio por modelo y año.<br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• Cantidad total de publicaciones.<br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• Comparaciones interanuales (YoY) de depreciación.<br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• Detalle de URLs para acceder a publicaciones activas.
</p>

---

<h2 align="center">📌 Motivación</h2>

<p align="center">
  Según datos de <a href="https://www.clarin.com/autos/autos-usados-10-vendidos-2023-dato-visto-complica-inicio-ano_0_87Fl0ytvtx.html">Clarín Autos (2023)</a>,<br>
  los modelos más vendidos del mercado argentino incluyen el Volkswagen Gol, Chevrolet Corsa,<br>
  Toyota Hilux y Ford EcoSport.<br>
  Este proyecto toma como base esa información para construir un pipeline automatizado de monitoreo de precios y publicaciones.
</p>

---

<h2 align="center">✅ Requisitos</h2>

<p align="center">
  • Python 3.11 (necesario para <code>undetected-chromedriver</code>)<br>
  • Google Chrome instalado<br>
  • Power BI Desktop
</p>

---

<h2 align="center">🚀 Instalación (Windows)</h2>

<div align="center">

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

