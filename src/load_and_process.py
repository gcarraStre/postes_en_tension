import streamlit as st
import pandas as pd
import geopandas as gpd
from parameters import DATA_DIR

@st.cache_data
def parse_data_postes_en_tension():
    """ Load hard-to-fill position data from path """
    raw_data = pd.read_csv(DATA_DIR / 'fiches_de_poste_en_tension.csv')
    data = raw_data.copy()
    data.rename(
        columns={
            "type_structure": "Type de structure",
            "grand_domaine": "Grand domaine",
            "domaine_professionnel": "Domaine professionnel",
            "rome": "Métier",
            "nombre_de_fiches_de_poste_en_tension": "Nombre de postes en tension",
            "département": "Numéro de département",
            },
        inplace=True)
    data = data.dropna(subset=["id", "id_asp"])
    return data

@st.cache_data
def load_geojson_departements() -> gpd.GeoDataFrame:
    """ Load geojson french departements data from path """
    raw_data = gpd.read_file(DATA_DIR / 'geoDataDepartments.geojson')
    
    return raw_data.rename(columns={"libgeo": "Département"})

def to_geolocalised_postes_per_department(data: pd.DataFrame, geojson: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Merge data with french departements geojson data to get geolocalised data """
    
    data = data.merge(geojson, left_on="Numéro de département", right_on="dep", how="left")
    data = data.groupby(['Numéro de département', 'Département', 'geometry'])['Nombre de postes en tension'].sum().reset_index()
    data = gpd.GeoDataFrame(data, geometry= data["geometry"])
    
    return data