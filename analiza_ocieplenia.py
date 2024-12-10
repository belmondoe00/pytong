import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np  # Do obliczenia regresji liniowej


# Funkcja do pobierania danych z bazy danych
def pobierz_dane_srednie_temperatury_widzialnosci_i_opadow():
    # Połączenie z bazą danych
    polaczenie = pyodbc.connect("""DRIVER={ODBC Driver 17 for SQL Server};
    Server=analityk.wwsi.edu.pl,50221;
    DATABASE=synop;
    uid=student;
    pwd=ciekawski""")

    # Zaktualizowane zapytanie SQL
    query = """
    SELECT 
        YEAR(Data) AS Rok, 
        AVG(CAST(COALESCE(TemperaturaPowietrza, 0) AS FLOAT)) AS SredniaTemperatura,
        AVG(CAST(COALESCE(Widzialnosc, 0) AS FLOAT)) AS SredniaWidzialnosc,
        SUM(CAST(COALESCE(WysokoscOpadu, 0) AS FLOAT)) AS SumaOpadow
    FROM depesze
    WHERE Data between '20000101' AND '20231231'
    AND Stacja = 12375
    AND Godzina IN('12:00')
    GROUP BY YEAR(Data)
    ORDER BY Rok
    """

    # Wczytanie danych do Pandas DataFrame
    dane = pd.read_sql(query, polaczenie)

    # Zamknięcie połączenia z bazą
    polaczenie.close()
    return dane


# Pobranie danych
dane = pobierz_dane_srednie_temperatury_widzialnosci_i_opadow()

# Wyświetlenie danych dla weryfikacji
print(dane.head())

# Wizualizacja średnich temperatur z linią regresji
plt.figure(figsize=(12, 6))
plt.plot(dane['Rok'], dane['SredniaTemperatura'], marker='o', label='Średnia Temperatura')

# Obliczenie regresji liniowej
coeffs_temp = np.polyfit(dane['Rok'], dane['SredniaTemperatura'], 1)
reg_line_temp = np.polyval(coeffs_temp, dane['Rok'])
plt.plot(dane['Rok'], reg_line_temp, color='red', label='Linia regresji')

plt.title('Średnia temperatura powietrza w latach 2000-2023')
plt.xlabel('Rok')
plt.ylabel('Średnia temperatura (°C)')
plt.grid()
plt.legend()
plt.show()

# Wizualizacja średniej widzialności z linią regresji
plt.figure(figsize=(12, 6))
plt.plot(dane['Rok'], dane['SredniaWidzialnosc'], marker='o', color='green', label='Średnia Widzialność')

# Obliczenie regresji liniowej
coeffs_vis = np.polyfit(dane['Rok'], dane['SredniaWidzialnosc'], 1)
reg_line_vis = np.polyval(coeffs_vis, dane['Rok'])
plt.plot(dane['Rok'], reg_line_vis, color='red', label='Linia regresji')

plt.title('Średnia widzialność w latach 2000-2023')
plt.xlabel('Rok')
plt.ylabel('Średnia widzialność (m)')
plt.grid()
plt.legend()
plt.show()

# Wizualizacja sumy opadów (bez linii regresji, ponieważ nie zawsze ma sens w przypadku sum)
plt.figure(figsize=(12, 6))
plt.bar(dane['Rok'], dane['SumaOpadow'], color='blue', label='Suma Opadów')
plt.title('Suma opadów w latach 2000-2023')
plt.xlabel('Rok')
plt.ylabel('Suma opadów (mm)')
plt.grid()
plt.legend()
plt.show()
