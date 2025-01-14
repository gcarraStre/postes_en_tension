import streamlit as st
import pandas as pd
import geopandas as gpd
from parameters import DATA_DIR
import boto3
from dotenv import load_dotenv
import os
import io

class LoadAndProcess:

    def __init__(self):
        

        endpoint_url, access_key_id, secret_access_key, session_token = self.get_secrets()

        self.s3 = boto3.client("s3", endpoint_url = endpoint_url,
                        aws_access_key_id = access_key_id,
                        aws_secret_access_key = secret_access_key,
                        aws_session_token = session_token)

    def get_secrets(self):
        if "secrets" in st.session_state:
            endpoint_url = st.secrets["minIO"]["ENDPOINT_URL"]
            access_key_id = st.secrets["minIO"]["AWS_ACCESS_KEY_ID"]
            secret_access_key = st.secrets["minIO"]["AWS_SECRET_ACCESS_KEY"]
            session_token = st.secrets["minIO"]["AWS_SESSION_TOKEN"]
        else:
            load_dotenv()
            endpoint_url = os.getenv('ENDPOINT_URL')
            access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
            secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            session_token = os.getenv('AWS_SESSION_TOKEN')
        
        return endpoint_url, access_key_id, secret_access_key, session_token


    @st.cache_data
    def parse_data_postes_en_tension(_self):
        """ Load hard-to-fill position data from path """
        raw_data = pd.read_csv(_self.get_data('fiches_de_poste_en_tension.csv'))
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

    def get_data(self, path):

        response = self.s3.get_object(Bucket='gcarra', Key=path)

        content = response['Body'].read().decode('utf-8')

        buffer = io.StringIO(content)
        
        return buffer

    @st.cache_data
    def load_geojson_departements(_self) -> gpd.GeoDataFrame:
        """ Load geojson french departements data from path """
        raw_data = gpd.read_file(_self.get_data('geoDataDepartments.geojson'))
        
        return raw_data.rename(columns={"libgeo": "Département"})

    def to_geolocalised_postes_per_department(self, data: pd.DataFrame, geojson: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Merge data with french departements geojson data to get geolocalised data """
        
        data = data.merge(geojson, left_on="Numéro de département", right_on="dep", how="left")
        data = data.groupby(['Numéro de département', 'Département', 'geometry'])['Nombre de postes en tension'].sum().reset_index()
        data = gpd.GeoDataFrame(data, geometry= data["geometry"])
        
        return data
    
loadAndProcess= LoadAndProcess()