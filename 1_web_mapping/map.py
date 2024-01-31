import requests
import zipfile
import folium
import os
import io
import pandas as pd

# URL of the ZIP file
zip_url = 'https://simplemaps.com/static/data/world-cities/basic/simplemaps_worldcities_basicv1.76.zip'

# Destination folder
dest_folder = '1_web_mapping/Files'

# Ensure the destination folder exists
os.makedirs(dest_folder, exist_ok=True)

# Send a GET request to the URL
response = requests.get(zip_url)

# Check if the request was successful
if response.status_code == 200:
    # Open the ZIP file
    with zipfile.ZipFile(io.BytesIO(response.content)) as thezip:
        # Loop through the contained files
        for fileinfo in thezip.infolist():
            # Check if the file is a CSV
            if fileinfo.filename.endswith('.csv'):
                # Extract the CSV file to the destination folder
                thezip.extract(fileinfo, dest_folder)
                print(f"Extracted {fileinfo.filename} to {dest_folder}")
                break
else:
    print('Failed to download the file.')

# We define our map instance
map = folium.Map(location=[41.398357, 2.174463], zoom_start = 12)

# We get the cities info
df = pd.read_csv("1_web_mapping/Files/worldcities.csv")
df = df[df["country"]=="Spain"]

cities = list(df[["city"]].values)
lat_lng = list(df[["lat", "lng"]].values)
population = list(df[["population"]].values)


# Generate a feature group to add our markers
fg = folium.FeatureGroup(name = "My Map")

for city, lat_lon, pop in zip(cities, lat_lng, population):
    inhabitants = int(pop[0])

    if inhabitants > 1000000:
        color = "red"
        radius = 35
    elif inhabitants > 100000 and inhabitants < 1000000:
        color = "orange"
        radius = 15
    else: 
        color = "beige"
        radius = 5
    
    popup_str = "This is {0} with a population of {1}".format(city[0], pop[0])
    fg.add_child(folium.CircleMarker(location=lat_lon, radius=radius, popup = popup_str, fill_color=color, color="grey", fill_opacity = 0.5))

# Add the markers to our feature grup map
map.add_child(fg)

map.save("1_web_mapping/Output/Map1.html")