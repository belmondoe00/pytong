import pyodbc
import pandas as pd
from bokeh.io import show
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool
from bokeh.plotting import figure
from bokeh.palettes import Viridis256
import json
#
# Połączenie z bazą danych
def pobierz_dane():
    polaczenie = pyodbc.connect("""DRIVER={ODBC Driver 17 for SQL Server};
    Server=analityk.wwsi.edu.pl,50221;
    DATABASE=synop;
    uid=student;
    pwd=ciekawski""")

    query = """
    SELECT 
        wojewodztwo,
        COUNT(DISTINCT dp.Stacja) AS LiczbaStacji,
        SUM(CAST(COALESCE(dp.WysokoscOpadu, 0) AS FLOAT)) AS SumaOpadow
    FROM depesze dp
    JOIN Stacje st ON dp.Stacja = st.IDStacji
    WHERE dp.Data BETWEEN '20000101' AND '20231231'
    GROUP BY wojewodztwo
    """

    dane = pd.read_sql(query, polaczenie)
    polaczenie.close()

    # Obliczenie średnich opadów
    dane['SredniaOpadow'] = dane['SumaOpadow'] / dane['LiczbaStacji']
    return dane

# Pobranie danych
dane = pobierz_dane()

# Wczytanie granic województw z pliku GeoJSON
with open('poland_provinces.geojson', 'r', encoding='utf-8') as file:
    granice = json.load(file)

# Wyświetlenie przykładowych danych z GeoJSON
print("Przykładowe dane z GeoJSON:")
for feature in granice['features'][:3]:  # Wyświetl pierwsze 3 obiekty
    print(json.dumps(feature['properties'], indent=2))

# Mapowanie średnich opadów na granice województw
def mapuj_dane_na_granice(granice, dane):
    for feature in granice['features']:
        wojewodztwo = feature['properties'].get('nazwa', 'Nieznane')
        srednia_opadow = dane.loc[dane['wojewodztwo'] == wojewodztwo, 'SredniaOpadow']
        feature['properties']['SredniaOpadow'] = float(srednia_opadow) if not srednia_opadow.empty else 0
    return granice

granice = mapuj_dane_na_granice(granice, dane)

# Konwersja danych GeoJSON na GeoJSONDataSource
geo_source = GeoJSONDataSource(geojson=json.dumps(granice))

# Tworzenie mapy w Bokeh
palette = Viridis256
color_mapper = LinearColorMapper(palette=palette, low=dane['SredniaOpadow'].min(), high=dane['SredniaOpadow'].max())

p = figure(title="Mapa średnich opadów w województwach Polski (2000-2023)",
           width=900, height=700, tools="pan,wheel_zoom,reset,save")

p.patches('xs', 'ys', source=geo_source,
          fill_color={'field': 'SredniaOpadow', 'transform': color_mapper},
          line_color='black', line_width=0.5, fill_alpha=0.8)

# Dodanie narzędzia Hover
hover = HoverTool()
hover.tooltips = [
    ("Województwo", "@nazwa"),
    ("Średnia Opadów (mm)", "@SredniaOpadow{0.0}")
]
p.add_tools(hover)

# Dodanie legendy
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=12, location=(0, 0), title="Średnia Opadów (mm)")
p.add_layout(color_bar, 'right')

# Wyświetlenie mapy
show(p)
