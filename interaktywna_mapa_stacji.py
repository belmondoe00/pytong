import pyodbc
import pandas as pd
import folium
from folium.plugins import MarkerCluster

# Połączenie z bazą danych i pobranie danych
def pobierz_dane():
    # Połączenie z bazą danych
    polaczenie = pyodbc.connect("""DRIVER={ODBC Driver 17 for SQL Server};
    Server=analityk.wwsi.edu.pl,50221;
    DATABASE=synop;
    uid=student;
    pwd=ciekawski""")

    # Pobranie danych o temperaturach
    query_temperatury = """
    SELECT stacja, Miesiac, SredTemp, NazwaM
    FROM SredMies2000to2018
    """
    dane_temperatury = pd.read_sql(query_temperatury, polaczenie)

    # Pobranie danych o stacjach
    query_stacje = """
    SELECT IDStacji, Nazwa, Szerokosc, Dlugosc
    FROM Stacje
    """
    dane_stacje = pd.read_sql(query_stacje, polaczenie)

    # Zamknięcie połączenia
    polaczenie.close()

    return dane_temperatury, dane_stacje


# Przetwarzanie danych
def przetworz_dane(dane_temperatury, dane_stacje):
    # Połączenie tabel na podstawie ID stacji
    dane = dane_temperatury.merge(
        dane_stacje, left_on="stacja", right_on="IDStacji", how="inner"
    )
    dane = dane.sort_values(by=["stacja", "Miesiac"])  # Sortowanie po stacji i miesiącu
    return dane


# Tworzenie mapy
def stworz_mape(dane, nazwa_pliku="mapa_srednich_temperatur.html"):
    mapa = folium.Map(location=[52.0, 19.0], zoom_start=6)
    marker_cluster = MarkerCluster().add_to(mapa)

    # Grupowanie danych według stacji
    grupy_stacje = dane.groupby("stacja")

    for stacja, grupa in grupy_stacje:
        # Pobranie współrzędnych i nazwy stacji
        szerokosc = grupa.iloc[0]["Szerokosc"]
        dlugosc = grupa.iloc[0]["Dlugosc"]
        nazwa_stacji = grupa.iloc[0]["Nazwa"]

        # Tworzenie opisu z danymi o temperaturach
        popup_html = f"<b>Stacja: {nazwa_stacji}</b><br>"
        for _, row in grupa.iterrows():
            popup_html += f"Miesiąc {row['Miesiac']}: {row['SredTemp']:.2f}°C<br>"

        # Dodanie markera do mapy
        folium.Marker(
            location=[szerokosc, dlugosc],
            popup=popup_html,
            icon=folium.Icon(color="blue"),
        ).add_to(marker_cluster)

    # Zapis mapy do pliku HTML
    mapa.save(nazwa_pliku)
    print(f"Mapa została zapisana jako {nazwa_pliku}")



# Główna funkcja
if __name__ == "__main__":
    # Pobranie danych z bazy
    dane_temperatury, dane_stacje = pobierz_dane()
    print("Dane pobrane z bazy danych.")

    # Przetworzenie danych
    dane = przetworz_dane(dane_temperatury, dane_stacje)
    print("Dane zostały przetworzone.")

    # Stworzenie mapy
    stworz_mape(dane)


