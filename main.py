import folium

import folium


m = folium.Map(location=[59.911491, 10.757933])

circle = folium.Circle(
    location=[59.911491, 10.757933],
    radius=2000,
    popup="City centre",
    color="#3186cc",
    fill=True,
    fill_color="#3186cc",
).add_to(m)

m.save("index.html")
