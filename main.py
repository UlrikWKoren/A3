from PIL import Image
import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static
import requests
import json
from query import requestDrinks
import base64
from image_proc import rem_back
from folium import plugins

import urllib.request

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

st.title('Winemap')

def updateMap(mapI, place = st.empty()):
    global worldMap
    if place:
        with place:
            if "markers" in st.session_state:
                for mark in st.session_state['markers']:
                    mapI.add_child(mark)
            folium_static(mapI, height=600, width=1100)


saveDrink = st.button('Save map')



with open('keys.json','r',encoding='utf-8') as file:
    file = json.load(file)
    apiKey = file['geocoding']['key1']
    apiKey2 = file['geocoding']['key2']





if "search" in st.session_state:
    defSearch = st.session_state['search']
else:
    defSearch = ''
name = st.text_input('Search for a wine',value=defSearch)
st.session_state['search'] = name




if name:
    drinks = requestDrinks(name=name)
    columns = []
    columns.append(st.columns(4))
    columns.append(st.columns(4))
    columns.append(st.columns(4))
    tileCount = 0
    columns = [j for i in columns for j in i]
    for drink in drinks:
        drink['ID'] = drink['link']['value'].split('/')[-1]
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
                st.write('trying special api')
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

            st.write(drink['link']['value'])
            m = folium.Map(location=[latitude, longitude],zoom_start=7)
            # circle = folium.Marker(
            #     location=[latitude, longitude],
            #     radius=1000,
            #     popup="City centre",
            #     color="#3186cc",
            #     fill=True,
            #     fill_color="#3186cc").add_to(m)

            bigM = folium.Map(location=[latitude, longitude],zoom_start=4)
            st.write(imageLink)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
            }
            r = requests.get(imageLink,headers = headers)
            with open(f"images/{drink['ID']}.jpg", "wb") as file:
                file.write(r.content)
            size = 200, 200
            im = Image.open(f"images/{drink['ID']}.jpg")
            im.thumbnail(size, Image.ANTIALIAS)
            with open(f"images/{drink['ID']}.jpg", 'wb') as file2:
                im.save(file2)

            encoded = base64.b64encode(open(f'images/{drink["ID"]}.jpg', 'rb').read())
            #st.write(encoded)
            #st.write(encoded)
            html = f'<img src="data:image/png;base64,{encoded.decode("UTF-8")}"> <p>' \
                   f'{drink["name"]["value"].replace("_", " ").capitalize()}</p>' \
                   f'<p>{drink["country"]["value"].replace("_", " ").capitalize()} ' \
                   f'{drink["region"]["value"].replace("_", " ").capitalize()} ' \
                   f'{drink["subregion"]["value"].replace("_", " ").capitalize()}</p>' \
                   f'<a href={drink["link"]["value"].capitalize()} target="_blank">Link</a>'

            resolution, width, height = 10, 17,35
            iframe = folium.IFrame(html,width=(width*resolution), height=(height*resolution),)
            iframe = (iframe)
            popup = folium.Popup(iframe)


            rem_back(f"images/{drink['ID']}.jpg")
            icon = folium.features.CustomIcon(f'images/{drink["ID"]}.png',icon_size=(40, 100),)
            # icon2 = folium.features.CustomIcon(f'images/{drink["ID"]}.png', icon_size=(40, 100), )
            # marker = folium.Marker([latitude, longitude], popup=popup, icon=icon)
            marker2 = folium.Marker([latitude, longitude], popup=popup, icon=icon)
            # marker.add_to(bigM)
            marker2.add_to(m)

            # circle = folium.Marker(
            #     location=[latitude, longitude],
            #     radius=1000,
            #     popup="City centre",
            #     color="#3186cc",
            #     fill=True,
            #     fill_color="#3186cc").add_to(bigM)

            polygon1 = folium.GeoJson(data=(open(f"geojson-files/{drink['country']['value']}.geojson", "r", encoding="utf-8")).read(),
                                      tooltip=drink['name']['value'])
            polygon2 = folium.GeoJson(data=(open(f"geojson-files/{drink['country']['value']}.geojson", "r", encoding="utf-8")).read())
            m.add_child(polygon1)
            #bigM.add_child(polygon2)
            updateMap(m)
            st.session_state['map'] = m
            st.session_state['tempMarkers'] = marker2



        if saveDrink:
            if "markers" not in st.session_state:
                st.session_state['markers'] = [st.session_state['tempMarkers']]
            else:
                st.session_state['markers'].append(st.session_state['tempMarkers'])
            updateMap(st.session_state['map'])

hide_anchor_link()

