import pandas as pd
import streamlit as st
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype
from parameters import COLUMNS_FILTERS
from branca.colormap import linear
import folium
import plotly.express as px



class Displayer : 
    """ This class allows to define methods to produce plots and filter UI """

    def __init__(self):
        self.fig = None
        self.fig1 = None
        self.fig2 = None
        self.fig3 = None
    def widget_filter(self):
        """
        This checkbox allow to select the filter option
        Parameters
        ----------
        None

        Returns
        ----------
        modify: bool
            It says if the filter option has been selected
        """
        with st.sidebar:
            st.markdown("""## FILTRES""")
            modify = st.checkbox("Appliquer des filtres sur les données")
        return modify


    def filter_dataframe(self, data, modify):
        """
        Allowing users to filter columns

        Parameters:
            pd.DataFrame : Original dataframe
            modify: bool
                It says if the filter option has been selected

        Returns:
            pd.DataFrame: Filtered dataframe
        """

        with st.sidebar:
            if modify:
                self.filter_data = data.copy()
                to_filter_columns = st.multiselect("Colonnes sur lesquels filtrer", COLUMNS_FILTERS, placeholder="Sélectionner les colonnes")
                for column in to_filter_columns:
                    left, right = st.columns((1, 20))
                    left.write("↳")
                    
                    if ((is_numeric_dtype(data[column])) and ((data[column].nunique() >= 10))):
                        _min = float(data[column].min())
                        _max = float(data[column].max())
                        step = (_max - _min) / 100
                        user_num_input = right.slider(
                            f"Values for {column}",
                            min_value=_min,
                            max_value=_max,
                            value=(_min, _max),
                            step=step,
                        )
                        self.filter_data = self.filter_data[
                            self.filter_data[column].between(*user_num_input)
                            ]
                        
                    elif is_datetime64_any_dtype(data[column]):
                        user_date_input = right.date_input(
                            f"Valeurs pour {column}",
                            value=(
                                data[column].min(),
                                data[column].max(),
                            ),
                        )
                        if len(user_date_input) == 2:
                            user_date_input = tuple(
                                map(pd.to_datetime, user_date_input)
                            )
                            start_date, end_date = user_date_input
                            self.filter_data = data.loc[
                                self.filter_data[column].between(start_date, end_date)
                            ]
                    
                    else :
                        user_cat_input = right.multiselect(
                            f"Valeurs pour {column}",
                            data[column].unique(),
                            default=list(data[column].unique()),
                        )
                        self.filter_data = self.filter_data[self.filter_data[column].isin(user_cat_input)]
    
    
    

    def plot_map(self, data_map_selected_data, data_map_all_data, data):

        colormap = linear.Blues_09.scale(
            data_map_all_data["Nombre de postes en tension"].min(),
            data_map_all_data["Nombre de postes en tension"].max()
        )
        self.m = folium.Map(location=[47, 2], zoom_start=5, tiles = None)
        folium.GeoJson(
        data_map_all_data,
        name="departments_boundaries",
        style_function=lambda x: {
            'fillOpacity': 0,    
            'weight': 1,         
            'color': 'gray',     
            'fillColor': 'none'  
        }
        ).add_to(self.m)
        if data_map_selected_data.empty == False:
            folium.Choropleth(
                    data=data_map_selected_data,
                    geo_data=data_map_selected_data,
                    columns=["Département", "Nombre de postes en tension"],
                    key_on="feature.properties.Département",
                    fill_color= None,
                    colormap=colormap,
                    legend_name="Nombre de fiches",
                    position = "right",
                ).add_to(self.m)
                
            folium.GeoJson(
                data_map_selected_data,
                tooltip=folium.GeoJsonTooltip(fields=["Département", "Numéro de département", "Nombre de postes en tension"], aliases=["Département:", "Numéro de département:", "Nombre de postes en tension:"]),
                style_function=lambda x: {'fillOpacity': 0, 'weight': 0} 
            ).add_to(self.m)
           
    def widget_plots(self, data):
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            type_analyse = st.selectbox(
            "Quelle analyse effectuer sur le nombre de postes en tension ?",
            ["Par type de structure et grand domaine","Par type de structure", "Par grand domaine", "Par domaine professionnel", "Par métier"],
            index=0,
            placeholder="choisir le type d'analyse",
            key="type_analyse",
        )      
            if type_analyse == "Par domaine professionnel":
                cols_to_group = ["Domaine professionnel"]
            elif type_analyse == "Par grand domaine":
                cols_to_group = ["Grand domaine"]
            elif type_analyse == "Par type de structure":
                cols_to_group = ["Type de structure"]
            elif type_analyse == "Par métier":
                cols_to_group = ["Métier"]
            else: 
                cols_to_group = ["Type de structure", "Grand domaine"]
        with col2_2:        
            department_modality = st.radio(
                "Choisir une modalité",
                ["Tous les départements", "Département spécifique"],
                key = "department_modality",
            )
            if department_modality == "Département spécifique":
                department_chosen = st.selectbox(
                    "Choisir un département",
                    data["Numéro de département"].unique(),
                    key="department_chosen",
                )
            else:
                department_chosen = None
        return cols_to_group, department_modality, department_chosen

    def plot_postes_VS_chosen_variable(self, data, cols_to_group, limit = 10, stucked = False):

        data = data.groupby(cols_to_group)['Nombre de postes en tension'].sum().reset_index()
        data = data.sort_values(by='Nombre de postes en tension', ascending=False)
        if stucked:
            custom_colors = [
                "#E41A1C", "#377EB8", "#4DAF4A", "#FF7F00", "#FFFF33", "#A65628", "#F781BF",  
                "#999999", "#66CC99", "#FFCC00", "#FF66CC", "#CC3399", "#003366", "#66CCFF"   
            ]
            self.fig = px.bar(data, x=cols_to_group[0], y='Nombre de postes en tension', color = cols_to_group[1], color_discrete_sequence=custom_colors, barmode="stack")
            self.fig.for_each_trace(lambda t: t.update(name=t.name[:30] + '...' if len(t.name) > 30 else t.name)) 
        else :
            if cols_to_group[0] == "Type de structure":
                title = None
            else :
                title = f"Nombre de postes pour {limit} {cols_to_group[0]} les plus en tension"
            self.fig = px.bar(data[:limit], x=cols_to_group[0], y='Nombre de postes en tension', title = title )
       

        

        


   


    
