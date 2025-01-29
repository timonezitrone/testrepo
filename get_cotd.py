import pickle
import random
import requests
import os
from shapely.geometry import box
import subprocess


api_key = os.getenv("API_KEY") 
key_var = 'MLY|8709790265784028|dac1938b9502bd5b3697bfb7136524f2'
ACCESS_TOKEN = key_var


def get_mapillary_features(min_lat, min_lon, max_lat, max_lon):
    # Create bounding box
    bbox = box(min_lon, min_lat, max_lon, max_lat)
    
    # Convert to Mapillary bbox string format
    bbox_str = f"{bbox.bounds[0]},{bbox.bounds[1]},{bbox.bounds[2]},{bbox.bounds[3]}"
    

    # Construct API URL
    url = f'https://graph.mapillary.com/map_features?access_token={ACCESS_TOKEN}&fields=id,object_value,geometry&bbox={bbox_str}'
    
    # Make API request
    response = requests.get(url)
    features = []
    
    
    if response.status_code == 200:
        data = response.json()
        for obj in data.get('data', []):
            try:
                feature = {
                    'type': 'Feature',
                    'properties': {
                        'id': obj['id'],
                        'object_value': obj['object_value']
                    },
                    'geometry': obj['geometry']
                }
                features.append(feature)
            except Exception as e:
                continue
    
    return features




def get_google_image(api_key, latitude, longitude):
    # URLs for Street View and Metadata APIs
    street_view_url = "https://maps.googleapis.com/maps/api/streetview"
    metadata_url = "https://maps.googleapis.com/maps/api/streetview/metadata"
    
    params = {
        "size": "1000x700",  # Image size (width x height in pixels)
        "location": f"{latitude},{longitude}",  # Location
        "fov": 90,  # Field of view (0 to 120 degrees)
        "heading": 0,  # Random heading (0 to 360 degrees)
        "pitch": 5,  # Camera pitch (-90 to 90 degrees)
        "key": api_key  # Your API key
    }
    # Check metadata first
    metadata_response = requests.get(metadata_url, params=params)
    if metadata_response.status_code == 200:
        metadata = metadata_response.json()
        if metadata.get("status") == "OK" and metadata.get("copyright") == "© Google":
            response = requests.get(street_view_url, params=params)
            if response.status_code == 200:
                # Create a folder to save the image
                output_folder = "challenge_of_the_day"
                os.makedirs(output_folder, exist_ok=True)
                output_path = os.path.join(output_folder, f"lat{latitude}lng{longitude}.jpg")
                with open(output_path, "wb") as file:
                    file.write(response.content)
                    print('found image')
                return output_path
            else:
                print(f"Failed to fetch image. Status code: {response.status_code}")
        else:
            print(f"No imagery available for {latitude}, {longitude}. Skipping.")
    else:
        print(f"Failed to fetch metadata. Status code: {metadata_response.status_code}")
    return None



def commit_and_push_changes(image_path):
    try:
        subprocess.run(["git", "config", "--global", "user.name", "GitHub Actions"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True)
        subprocess.run(["git", "add", image_path], check=True)
        subprocess.run(["git", "commit", "-m", "Auto-update challenge image"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Changes committed and pushed successfully.")
    except subprocess.CalledProcessError:
        print("No changes to commit or an error occurred.")



def get_coordinates_depth_5(i, j, k, l, n, m, o, p, q, r, s, t):
    min_lat = i * 10 - 90
    min_lng = j * 10 - 180
    min_lat = min_lat + k * 2.5
    min_lng = min_lng + l * 2.5
    min_lat = min_lat + n * 0.5
    min_lng = min_lng + m * 0.5
    min_lat = min_lat + o * 0.125
    min_lng = min_lng + p * 0.125
    min_lat = min_lat + q * 0.025
    min_lng = min_lng + r * 0.025
    min_lat = min_lat + s * 0.00625
    min_lng = min_lng + t * 0.00625
    max_lat = min_lat + 0.00625
    max_lng = min_lng + 0.00625
    return min_lat, min_lng, max_lat, max_lng

def get_challenge_of_the_day(api_key, grid):
    short_list = []
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if type(grid[i][j]) == list:
                for k in range(len(grid[i][j])):
                    for l in range(len(grid[i][j][k])):
                        if type(grid[i][j][k][l]) == list:
                            for n in range(len(grid[i][j][k][l])):
                                for m in range(len(grid[i][j][k][l][n])):
                                    if type(grid[i][j][k][l][n][m]) == list:
                                        for o in range(len(grid[i][j][k][l][n][m])):
                                            for p in range(len(grid[i][j][k][l][n][m][o])):
                                                if type(grid[i][j][k][l][n][m][o][p]) == list:
                                                    for q in range(len(grid[i][j][k][l][n][m][o][p])):
                                                        for r in range(len(grid[i][j][k][l][n][m][o][p][q])):
                                                            if grid[i][j][k][l][n][m][o][p][q][r] == 2000:
                                                                cell = [i,j,k,l,n,m,o,p,q,r]
                                                                short_list.append(cell)
    found_2000 = False
    while found_2000 == False:
        cotd = random.randint(0, len(short_list) - 1)
        s = random.randint(0, 3)
        t = random.randint(0, 3)
        min_lat, min_lng, max_lat, max_lng = get_coordinates_depth_5(short_list[cotd][0], short_list[cotd][1], short_list[cotd][2], short_list[cotd][3], short_list[cotd][4], short_list[cotd][5], short_list[cotd][6], short_list[cotd][7], short_list[cotd][8], short_list[cotd][9], s, t)
        features = get_mapillary_features(min_lat, min_lng, max_lat, max_lng)
        if len(features) == 2000:
            found_2000 = True
    found_image = False
    count = 0
    image_path = None
    while found_image == False and count < 100:
        lat = random.uniform(min_lat, max_lat)
        lng = random.uniform(min_lng, max_lng)
        image_path = get_google_image(api_key, lat, lng)
        found_image = image_path is not None
        count += 1
    if image_path:
      	commit_and_push_changes(image_path) 

    
with open("world_grid_depth4_europe_final.pkl", "rb") as f:
    grid = pickle.load(f)

get_challenge_of_the_day(api_key, grid)


