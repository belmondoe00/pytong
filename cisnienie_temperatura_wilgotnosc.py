import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pyodbc
from scipy.interpolate import griddata

# Połączenie z bazą danych
polaczenie = pyodbc.connect("""DRIVER={ODBC Driver 17 for SQL Server};
Server=analityk.wwsi.edu.pl,50221;
DATABASE=synop;
uid=student;
pwd=ciekawski""")

# Pobieranie danych konturów Polski
zapytanie_kontury = """
SELECT [dl], [szer], [nr]
FROM [synop].[dbo].[PolskaPunkty]
ORDER BY nr;
"""
kontury = pd.read_sql(zapytanie_kontury, polaczenie)

# Pobieranie danych meteorologicznych
zapytanie_dane = """
WITH ct AS (
    SELECT TOP 1 godzina
    FROM Depesze
    WHERE Data = CAST(GETDATE() AS DATE)
    GROUP BY godzina
    HAVING COUNT(*) > 40
    ORDER BY godzina DESC
)
SELECT 
    CAST(data AS VARCHAR(20)) AS Dzien,
    CAST(godzina AS VARCHAR(5)) AS Godzina,
    CisnienieNaPoziomieMorza AS Cisn,
    TemperaturaPowietrza AS Temp,
    TemperaturaPowietrza - TemperaturaPunktuRosy AS Wilg,
    Szerokosc AS Szer,
    Dlugosc AS Dlug
FROM Depesze AS D
JOIN Stacje AS S 
    ON D.stacja = S.idstacji
WHERE 
    Data = CAST(GETDATE() AS DATE) AND
    Godzina = (SELECT godzina FROM ct) AND
    CisnienieNaPoziomieMorza > 0;
"""
dane = pd.read_sql(zapytanie_dane, polaczenie)

# Zamknięcie połączenia
polaczenie.close()

# Przygotowanie danych
dl = np.asarray(dane['Dlug'])
szer = np.asarray(dane['Szer'])
cisn = np.asarray(dane['Cisn'])
temp = np.asarray(dane['Temp'])
wilg = np.asarray(dane['Wilg'])

# Tworzenie siatki regularnej
dlgr = np.linspace(min(kontury['dl']), max(kontury['dl']), 1000)
szergr = np.linspace(min(kontury['szer']), max(kontury['szer']), 1000)
X, Y = np.meshgrid(dlgr, szergr)

# Interpolacja do węzłów siatki
CISN = griddata((dl, szer), cisn, (X, Y), method='cubic')
TEMP = griddata((dl, szer), temp, (X, Y), method='cubic')
WILG = griddata((dl, szer), wilg, (X, Y), method='cubic')

# Obliczanie wartości izolinii
izoC = range(int(min(cisn)) - 1, int(max(cisn)) + 1, 1)
izoT = range(int(min(temp)) - 1, int(max(temp)) + 1, 1)
izoR = range(int(min(wilg)) - 1, int(max(wilg)) + 1, 1)

# Rysowanie wykresów
fig, axes = plt.subplots(1, 3, figsize=(20, 6), dpi=100)

# Rozkład ciśnienia
cs = axes[0].contourf(X, Y, CISN, levels=izoC, cmap='coolwarm')
fig.colorbar(cs, ax=axes[0], label='Ciśnienie (hPa)')
axes[0].set_title('Rozkład ciśnienia')
axes[0].set_xlabel('Długość geograficzna')
axes[0].set_ylabel('Szerokość geograficzna')

# Rozkład temperatury
ct = axes[1].contourf(X, Y, TEMP, levels=izoT, cmap='coolwarm')
fig.colorbar(ct, ax=axes[1], label='Temperatura (°C)')
axes[1].set_title('Rozkład temperatury')
axes[1].set_xlabel('Długość geograficzna')
axes[1].set_ylabel('Szerokość geograficzna')

# Rozkład wilgotności
cr = axes[2].contourf(X, Y, WILG, levels=izoR, cmap='coolwarm')
fig.colorbar(cr, ax=axes[2], label='Wilgotność względna')
axes[2].set_title('Rozkład wilgotności')
axes[2].set_xlabel('Długość geograficzna')
axes[2].set_ylabel('Szerokość geograficzna')

# Wyświetlanie wykresów
plt.tight_layout()
plt.show()
