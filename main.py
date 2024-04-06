import folium
import requests
import pandas as pd

# read the CSV file ...
data = pd.read_csv(filepath_or_buffer="data.csv")

# the lists in our data file ...
# ['State', 'Data', 'Population (2029 Estimated)', 'Fiscal Year 20233 Funding', 'Total Diabetes Cases (Prevalence)', 'New Diabetes Cases (Incidence)', 'Prediabetes Notification', 'URL']

# calculate the percentage of the population with diabetes
data["Percentage with Diabetes"] = (
    data["Total Diabetes Cases (Prevalence)"] / data["Population (2029 Estimated)"]
) * 100

# create a dictionary that shows the State as a key and it's percentage as the value ...
results = (
    data[["State", "Percentage with Diabetes"]]
    .set_index(keys="State")
    .to_dict()["Percentage with Diabetes"]
)

# next, generate a color palate that ill show up on the heat map...
# the keys will be associated with the percentage calculated above
color_palate = {
    1: "#fee2e2",
    2: "#fecaca",
    3: "#fca5a5",
    4: "#ef4444",
    5: "#dc2626",
    6: "#b91c1c",
    7: "#991b1b",
    8: "#7f1d1d",
    9: "#450a0a",
    10: "#450a0a",
    11: "#450a0a",
    12: "#450a0a",
    13: "#450a0a",
    14: "#450a0a",
}

# no, get the url to begin to create the FOLIUM object
# this JSON can be taken from the GEOJson website
url = "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_110m_admin_1_provinces_shp.geojson"

# we need to add a few details to the parsed JSON file to render the heat map ...
response = results.get(url)
# the response is a JSON file the same as the one from the URL
response = response.json()

# we loop over the JSON data and add the diabetes data we calculated from the data.csv file
for feature in response["features"]:
    # result is our class with state:percent
    # so we loop over the JSON and match the name with the percentage ...
    feature["properties"]["dbPercent"] = round(
        number=results[feature["properties"]["name"]], ndigits=2)
    # now we add some styling properties...
    feature["properties"]["fillcolor"] = ""
    feature["properties"]["fillOpacity"] = ""


# let's create a map object ...
heat_map = folium.Map(
    location=[37.0902, -95.7129],
    zoom_start=4,
    tiles="CartoDB Positron",
)

# we can add some styling to showcase the effects
default_style = lambda x: {
    # you can add any kind of styling inside here...
    # now, we can use our oqo dictionary to generate the heat map
    # recall that feature["properties"]["dbPercent"] is now part of the JSON data...
    "fillColor": color_palate[int(x["properties"]["dbPercent"])],
    "fillOpacity": "0.91",
}

# the darker the color, the more the population has diabetes
hover_style = lambda x: {
    "fillOpacity": "1",
}

# now we add a layer on top of the generated mep..
# this layer highlights the state borders,
geo_layer = folium.GeoJson(
    response,
    style_function=default_style,
    highlight_function=hover_style,
)

# finally, we can add some pop ups to showcase some data
geo_layer.add_child(
    folium.GeoJsonTooltip(
        # the fields are associated with the keys of the JSON file
        ["name", "region", "dbPercent"]
        # dbPercent is the key we created from the CSV file using pandas...
    )
)

# we add the geo_layer to the main map=heat_map
geo_layer.add_to(heat_map)
heat_map.save("heat_map.html")
