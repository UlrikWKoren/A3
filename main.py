import time

import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static
import requests
import json
from query import requestDrinks
st.set_page_config(page_title="WineFinder",
                   page_icon=":)",
                   layout="wide")




def hide_anchor_link():
    st.markdown("""
        <style>
        .css-15zrgzn {display: none}
        .css-eczf16 {display: none}
        .css-jn99sy {display: none}
        </style>
        """, unsafe_allow_html=True)

def updateMap(mapI, place = st.empty()):
    global worldMap
    if place:
        with place:
            folium_static(mapI, height=500, width=800)




with open('keys.json','r',encoding='utf-8') as file:
    file = json.load(file)
    apiKey = file['geocoding']['key1']
    apiKey2 = file['geocoding']['key2']



st.title('Winemap')
name = st.text_input('Search for a wine')


if 'map' not in st.session_state:
    m = folium.Map(zoom_control=False,
               scrollWheelZoom=False,
               dragging=False)
    updateMap(m)


if name:
    drinks = requestDrinks(name=name)
    columns = []
    columns.append(st.columns(4))
    columns.append(st.columns(4))
    columns.append(st.columns(4))
    tileCount = 0
    columns = [j for i in columns for j in i]
    for drink in drinks:
        imageLink = f"http://bilder.vinmonopolet.no/cache/300x300-0/{drink['link']['value'].split('/')[-1]}-1.jpg"
        columns[tileCount].markdown(f"""
        <div style="text-align: center;">
        <img src={imageLink} widht = 300 height="300">
        </div>
        """,unsafe_allow_html=True)

        columns[tileCount].markdown("<h5 style='text-align: center; font-family:sans-serif'; color: black;'>"
                                    f"{drink['name']['value'].replace('_',' ').capitalize()}</h4>",unsafe_allow_html=True)

        originString = "<p style='text-align: center; font-family:sans-serif'; color: black;'>"
        locationString = ""
        onlyCountry = True
        if drink['country']['value']:
            originString += f" {drink['country']['value'].replace('_', ' ').capitalize()}"
            locationString += drink['country']['value'].replace('_', ' ').capitalize()
        if drink['region']['value'] and drink['region']['value'] != 'Øvrige':
            originString += f", {drink['region']['value'].replace('_', ' ').capitalize()}"
            locationString += ", " + drink['region']['value'].replace('_', ' ').capitalize()
            onlyCountry = False
        if drink['subregion']['value'] and drink['subregion']['value'] != 'Øvrige':
            originString += f", {drink['subregion']['value'].replace('_', ' ').capitalize()} </p>"
            locationString = locationString.split(',')[0]
            locationString += ", " + drink['subregion']['value'].replace('_', ' ').capitalize()
            onlyCountry = False

        columns[tileCount].markdown(originString,unsafe_allow_html=True)
        doAction = columns[tileCount].button('Map',key=drink['link']['value'].split('/')[-1])
        tileCount += 1
        if doAction:
            if onlyCountry:
                apiString = f"https://api.opencagedata.com/geocode/v1/json?key={apiKey2}&q={drink['countryid']['value']}&abbrv=1&limit=1"
                r = requests.get(apiString).json()
                data = r['results'][0]['geometry']
                latitude = data['lat']
                longitude = data['lng']
            else:
                try:
                    if drink['countryid']['value'] == 'GBS':
                        drink['countryid']['value'] = 'GB'
                    apiString = f"https://api.myptv.com/geocoding/v1/locations/by-text" \
                            f"?searchText={locationString}&countryFilter={drink['countryid']['value']}&apiKey={apiKey}"
                    r = requests.get(apiString).json()
                    data = r['locations'][0]
                    latitude = data['referencePosition']['latitude']
                    longitude = data['referencePosition']['longitude']
                except Exception as error:
                        st.error('PLACE API FAILED')
                        st.write(apiString)
                        apiString = f"https://api.opencagedata.com/geocode/v1/json?key={apiKey2}&q={drink['countryid']['value']}&abbrv=1&limit=1"
                        r = requests.get(apiString).json()
                        data = r['results'][0]['geometry']
                        latitude = data['lat']
                        longitude = data['lng']
                        onlyCountry = True

            st.write(drink['link']['value'])
            m = folium.Map(location=[latitude, longitude],zoom_start=4,zoom_control=False,
               scrollWheelZoom=False,
               dragging=False)
            if not onlyCountry:
                circle = folium.Marker(
                    location=[latitude, longitude],
                    radius=1000,
                    popup="City centre",
                    color="#3186cc",
                    fill=True,
                    fill_color="#3186cc").add_to(m)

            bigM = folium.Map(location=[latitude, longitude],zoom_start=4)
            if not onlyCountry:
                circle = folium.Marker(
                    location=[latitude, longitude],
                    radius=1000,
                    popup="City centre",
                    color="#3186cc",
                    fill=True,
                    fill_color="#3186cc").add_to(bigM)

            m.add_child(folium.GeoJson(data=(open(f"geojson-files/{drink['country']['value']}.geojson", "r", encoding="utf-8")).read()))
            bigM.add_child(folium.GeoJson(data=(open(f"geojson-files/{drink['country']['value']}.geojson", "r", encoding="utf-8")).read()))
            st.session_state['map'] = m
            st.session_state['bigM'] = bigM
            updateMap(st.session_state['map'])




hide_anchor_link()

