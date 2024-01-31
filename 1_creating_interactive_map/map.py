import requests
import zipfile
import folium
import os
import io
import pandas as pd


# We define our map instance
map = folium.Map(location=[41.398357, 2.174463], zoom_start = 12)

#______________________________________________________________________________________________________
#                                   DISPLAYING SPANISH CITIES IN OUR MAP
#______________________________________________________________________________________________________

# Function to rescale the population data
def rescale_vector(vector):
    min_val = min(vector)
    max_val = max(vector)

    # Normalization to a 0-1 range
    normalized_vector = [(x - min_val) / (max_val - min_val) for x in vector]

    # Rescaling to the 5-35 range
    min_target = 5
    max_target = 50
    rescaled_vector = [min_target + x * (max_target - min_target) for x in normalized_vector]

    return rescaled_vector

#____________________________________________________________ Get cities data directly from the source
# URL of the ZIP file
zip_url = 'https://simplemaps.com/static/data/world-cities/basic/simplemaps_worldcities_basicv1.76.zip'

# Destination folder
dest_folder = '1_web_mapping/Files/'

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


# We get the cities info
df = pd.read_csv("1_web_mapping/Files/worldcities.csv")
df = df[df["country"]=="Spain"]

# We get the lists we are going to use in the loop
cities = list(df["city"].values)
lat_lng = list(df[["lat", "lng"]].values)
population = list(df["population"])
radius_pop = rescale_vector(population)

# Generate a feature group to add our markers
fgc = folium.FeatureGroup(name = "cities")

for city, lat_lon, pop, rad in zip(cities, lat_lng, population, radius_pop):
    if pop > 1000000:
        color = "red"
    elif pop > 100000 and pop < 1000000:
        color = "orange"
    else: 
        color = "beige"
    
    popup_str = "This is {0} with a population of {1}".format(city, pop)
    fgc.add_child(folium.CircleMarker(location=lat_lon, radius=rad, popup = popup_str, fill_color=color, color="grey", fill_opacity = 0.5))

#______________________________________________________________________________________________________
#                                   DISPLAYING SPANISH REGIONS IN OUR MAP
#______________________________________________________________________________________________________

#____________________________________________________________ Get Spain geojson data
# URL of the raw GeoJSON file
url = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-communities.geojson"

# Sending a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    #spain_geojson = response.content
    # Write the content to a file
    with open(dest_folder+'spain-communities.geojson', 'wb') as file:
       file.write(response.content)
    print("File downloaded successfully")
else:
    print("Failed to download file")

with open("1_web_mapping/Files/spain-communities.geojson", "r") as file:
    data = file.read()

fgr = folium.FeatureGroup(name = "regions")

fgr.add_child(
    folium.GeoJson(
        data=data, 
        fillOpacity= 0,
        color = "grey",
        opacity = 0.5
        ))

#______________________________________________________________________________________________________
#                                   GENERATING OUR FINAL MAP
#______________________________________________________________________________________________________
# Add the markers to our feature grup map
map.add_child(fgc)
map.add_child(fgr)

# We add the layer control
map.add_child(folium.LayerControl())

map.save("Spain_cities_regions_population_map.html")