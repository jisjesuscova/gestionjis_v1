import streamlit as st
from streamlit_option_menu import option_menu
from rrhh import show_rrhh_page
from ingresos import show_ingresos_page
from resultado import show_eerr_page

#st.set_page_config(layout="wide")
st.set_page_config(
    page_title="Indicadores JIS",
    page_icon="😎",
    layout="wide"
)

def streamlit_menu():
    selected = option_menu(
        menu_title=None,
        options=["INICIO", "INGRESOS", "RRHH", "EERR"],
        icons=["house", "book", "envelope"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa", "width": "100%"},
            "icon": {"color": "orange", "font-size": "20px"},
            "nav-link": {"font-size": "25px", "text-align": "left", "margin": "0px", "--hover-color": "#ddd", "flex": "1"},
            "nav-link-selected": {"background-color": "red"},
            "menu": {"display": "flex", "width": "100%"},
        },)
    return selected

with st.container():
    selected = streamlit_menu()

if selected == "INICIO":
    st.title(f"You have selected {selected}")
if selected == "INGRESOS":
    show_ingresos_page()    
if selected == "RRHH":    
    show_rrhh_page()
if selected == "EERR":
    show_eerr_page()
