import streamlit as st
from streamlit_folium import folium_static


folium_static(st.session_state['bigM'])
