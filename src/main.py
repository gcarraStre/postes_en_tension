from plots import Displayer
import streamlit as st
from load_and_process import loadAndProcess
import pandas as pd
from streamlit_folium import st_folium

class PosteEnTension(Displayer):

    def __init__(self, path):
        self.path = path
        self.filter_data = None
        self.m = None
        
        st.set_page_config(page_title="Poste en tension", layout="wide")

        data = loadAndProcess.parse_data_postes_en_tension()

        geojson = loadAndProcess.load_geojson_departements()

        self.title_and_description()

        st.divider()

        modify = self.widget_filter()

        self.filter_dataframe(data, modify)

        selected_data = self.filter_data if self.filter_data is not None else data

        data_map_all_data = loadAndProcess.to_geolocalised_postes_per_department(data, geojson)

        data_map_selected_data = loadAndProcess.to_geolocalised_postes_per_department(selected_data, geojson)

        col1, col2 = st.columns([1, 1.2])
        with col1:
            self.plot_map(data_map_selected_data, data_map_all_data, data)

            st_folium(self.m, width=485, height=450)

        with col2:
            cols_to_group, department_choice, department_chosen = self.widget_plots(selected_data)

            if department_choice == "Département spécifique":
                plot_data = selected_data[selected_data["Numéro de département"] == department_chosen]
            else:
                plot_data = selected_data

            
            self.plot_postes_VS_chosen_variable(plot_data, cols_to_group,  stucked=len(cols_to_group) == 2)
                
            st.plotly_chart(
                self.fig, theme="streamlit", use_container_width=True, width=1000
            )
        
       
    def title_and_description(self):
        
        st.title("Postes en tension")
        st.markdown(
            """ Une des problématiques autour de l’insertion par l’activité est d’identifier les fiches de poste en tension de chaque structure, dans les différents territoires afin de mieux orienter les candidat(e)s. 
            \\
            Cet outil permets de visualiser les postes en tension sur une carte et de filtrer les données pour mieux les analyser.
            \\
            \\
            Les graphes ci-dessous sont issues des données filtrées comme indiqué dans la section filtre à gauche.
                """
        )

if __name__ == "__main__":
    PosteEnTension("data/fiches_de_poste_en_tension.csv")