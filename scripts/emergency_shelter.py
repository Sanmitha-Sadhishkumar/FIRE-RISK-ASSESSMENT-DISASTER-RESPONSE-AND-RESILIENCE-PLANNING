# Import Libraries
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from geopy.geocoders import Nominatim
import time

def emergency_shelter_func():
    # Load Data
    school_data = pd.read_csv('/content/drive/MyDrive/Module 5/Delhi/school_data.csv')
    facilities_data = pd.read_csv('/content/drive/MyDrive/Module 5/Delhi/school_detail.csv')
    fault_data = gpd.read_file('/content/drive/MyDrive/Module 5/Delhi/Fault.shp')
    earthquake_data = gpd.read_file('/content/drive/MyDrive/Module 5/Delhi/Earthquake.shp')
    metro_data = pd.read_csv('/content/drive/MyDrive/Module 5/Delhi/Delhi metro.csv')
    landuse_data = gpd.read_file('/content/drive/MyDrive/Module 5/Delhi/Landuse.shp')
    waterbody_data = gpd.read_file('/content/drive/MyDrive/Module 5/Delhi/Waterbody.shp')
    population_data = pd.read_csv('/content/drive/MyDrive/Module 5/Delhi/Population_den.csv')

    # Initialize Geocoder
    geolocator = Nominatim(user_agent="fyp.orange.2024@gmail.com")

    def geocode_school(row):
        try:
            #Village Name
            query = f"{row['VILLAGE_NAME']}, Delhi, India" if pd.notna(row['VILLAGE_NAME']) else None
            if query:
                location = geolocator.geocode(query)
                if location:
                    time.sleep(3)
                    return pd.Series([location.latitude, location.longitude])

            # Pincode
            if pd.notna(row['PINCODE']):
                query = f"{row['PINCODE']}, Delhi, India"
                location = geolocator.geocode(query)
                if location:
                    time.sleep(3)
                    return pd.Series([location.latitude, location.longitude])
        except Exception as e:
            print(f"Error geocoding {query}: {e}")
        return pd.Series([None, None])


    school_data[['latitude', 'longitude']] = school_data.apply(geocode_school, axis=1)

    # Save
    school_data.to_csv('/content/drive/MyDrive/Module 5/Delhi/School_data_Coords.csv', index=False)
    print("Schhol Locations saved.")

    print(school_data['latitude'].isnull().sum(), "records with missing latitude")
    print(school_data['longitude'].isnull().sum(), "records with missing longitude")


    import pandas as pd
    import folium


    df = pd.read_csv('/content/drive/MyDrive/Module 5/Delhi/School_data_Coords.csv')
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11)


    for _, row in df.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=row['SCHOOL_NAME'],
            tooltip=row['SCHOOL_NAME'],
            icon=folium.Icon(color='blue', icon='school', prefix='fa')
        ).add_to(m)


    output_path = "/content/drive/MyDrive/Module 5/Delhi/School_map.html"
    m.save(output_path)
    m

    school_data= pd.read_csv('/content/drive/MyDrive/Module 5/Delhi/School_data_Coords.csv')
    # Convert to GeoDataFrame
    geometry = [Point(xy) for xy in zip(school_data['longitude'], school_data['latitude'])]
    merged_gdf = gpd.GeoDataFrame(school_data, geometry=geometry, crs='EPSG:4326')
    merged_gdf = merged_gdf.to_crs('EPSG:32644')

    # Convert Other Data to CRS
    fault_data = fault_data.to_crs('EPSG:32644')
    earthquake_data = earthquake_data.to_crs('EPSG:32644')
    waterbody_data = waterbody_data.to_crs('EPSG:32644')

    # Convert Metro Data to GeoDataFrame
    geometry = [Point(xy) for xy in zip(metro_data['Longitude'], metro_data['Latitude'])]
    metro_data = gpd.GeoDataFrame(metro_data, geometry=geometry, crs='EPSG:4326')
    metro_data = metro_data.to_crs('EPSG:32644')

    # Merge the data
    school_data['_id'] = school_data['_id'].astype(str)
    facilities_data['_id'] = facilities_data['_id'].astype(str)
    merged_data = pd.merge(school_data, facilities_data, on="_id", how="inner")

    # Convert to GeoDataFrame
    geometry = [Point(xy) for xy in zip(merged_data['longitude'], merged_data['latitude'])]
    merged_gdf = gpd.GeoDataFrame(merged_data, geometry=geometry, crs='EPSG:4326')
    merged_gdf = merged_gdf.to_crs('EPSG:32644')

    #Population Density
    population_density_dict = {
        str(row['District']).strip().lower(): row['Population'] / row['Area'] for _, row in population_data.iterrows()}

    # Normalize
    merged_gdf['DISTNAME'] = merged_gdf['DISTNAME'].str.strip().str.lower()

    # Mapping
    merged_gdf['POP_DENSITY'] = merged_gdf['DISTNAME'].map(population_density_dict)


    # Distance Calculation
    def calculate_distance(merged_gdf, target_gdf, column_name):
        merged_gdf[column_name] = merged_gdf.geometry.apply(lambda x: target_gdf.geometry.distance(x).min())
        return merged_gdf

    merged_gdf = calculate_distance(merged_gdf, fault_data, 'DIST_FAULT')
    merged_gdf = calculate_distance(merged_gdf, earthquake_data, 'DIST_EARTHQUAKE')
    merged_gdf = calculate_distance(merged_gdf, waterbody_data, 'DIST_WATERBODY')
    merged_gdf = calculate_distance(merged_gdf, metro_data, 'DIST_METRO')


    #Open space
    landuse_data = landuse_data.to_crs('EPSG:32644')
    open_space_types = ['meadow', 'grass', 'village_green', 'recreation_groun','green_belt', 'greenfield', 'allotments', 'plant_nursery']

    merged_gdf['OPEN_SPACES'] = merged_gdf.geometry.apply(
        lambda x: landuse_data[landuse_data['TYPE'].isin(open_space_types)].geometry.distance(x).min())

    # Save Data
    merged_output_path = '/content/drive/MyDrive/Module 5/Delhi/Final_Data.csv'
    merged_gdf.to_csv(merged_output_path, index=False)
    print(f'Final data saved.')
    print(merged_gdf.columns)

    merged_data = pd.read_csv('/content/drive/MyDrive/Module 5/Delhi/Final_Data.csv')

    # Weights Based on the Paper
    weights = {
        'DIST_FAULT': 0.12,
        'DIST_EARTHQUAKE': 0.115,
        'POP_DENSITY': 0.115,
        'OPEN_SPACES': 0.095,
        'DIST_METRO': 0.017,
        'DIST_WATERBODY': 0.019,
    }

    # Normalize
    total_weight = sum(weights.values())
    normalized_weights = {k: v / total_weight for k, v in weights.items()}

    #GPR Model
    features = ['DIST_FAULT', 'DIST_EARTHQUAKE', 'POP_DENSITY', 'OPEN_SPACES', 'DIST_METRO', 'DIST_WATERBODY']
    X = merged_gdf[features]
    y = np.dot(X, list(normalized_weights.values()))

    # Normalize Data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Fit GPR Model
    kernel = C(1.0, (1e-4, 1e4)) * RBF(10, (1e-2, 1e2))
    gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10)
    gpr.fit(X_scaled, y)
    shelter_scores = gpr.predict(X_scaled)

    min_score = np.min(shelter_scores)
    max_score = np.max(shelter_scores)
    normalized_scores = 1 + 9 * (shelter_scores - min_score) / (max_score - min_score)
    merged_gdf['SHELTER_SCORE'] = np.round(normalized_scores, 2)

    # Save
    output_path = '/content/drive/MyDrive/Module 5/Delhi/School_Scores.csv'
    merged_gdf.to_csv(output_path, index=False)
    print(f'Results saved.')


    import folium
    import pandas as pd
    import geopandas as gpd

    # Load the data
    score_gdf = pd.read_csv('/content/drive/MyDrive/Module 5/Delhi/School_Scores.csv')
    earthquake_gdf = gpd.read_file('/content/drive/MyDrive/Module 5/Delhi/Earthquake.shp')
    fault_gdf = gpd.read_file('/content/drive/MyDrive/Module 5/Delhi/Fault.shp')
    water_gdf = gpd.read_file('/content/drive/MyDrive/Module 5/Delhi/Waterbody.shp')
    landuse_data = gpd.read_file('/content/drive/MyDrive/Module 5/Delhi/Landuse.shp')


    # Filter Open Spaces
    landuse_data = landuse_data.to_crs('EPSG:32644')
    open_space_types = ['meadow', 'grass', 'village_green', 'recreation_groun','green_belt', 'greenfield', 'allotments', 'plant_nursery']
    open_space_gdf = landuse_data[landuse_data['TYPE'].isin(open_space_types)]

    # Create Map
    m = folium.Map(location=[28.7041, 77.1025], zoom_start=11)

    # Define colors
    colors = ['red', 'orange', 'green']

    # Color Adjustment Logic
    for _, row in score_gdf.iterrows():
        school_name = row['SCHOOL_NAME'].split(',')[0]
        score = row['SHELTER_SCORE']
        status = int(row['BLDSTATUS'])
        electricity = int(row['ELECTRIC_YN'])
        functional_toilets = row['TOILETB_FUNC'] + row['TOILETG_FUNC']

        # Determine Color Index Based on Score
        if score <= 3:
            color_index = 0
        elif score <= 7:
            color_index = 1
        else:
            color_index = 2

        # Adjust for Building Status and Electricity only if initial score > 3
        if color_index > 0:
            if status == 3:  # Under Construction
                color_index = max(color_index - 1, 0)
                status_text = 'Under Construction'
            elif status == 2:  # Partially Damaged
                color_index = max(color_index - 1, 0)
                status_text = 'Partially Damaged'
            else:
                status_text = 'Functional'

            if electricity == 0:
                color_index = max(color_index - 1, 0)
        else:
            status_text = 'Functional' if status == 1 else 'Partially Damaged' if status == 2 else 'Under Construction'

        # Final Color Selection
        color = colors[color_index]

        # Create Popup Message
        popup_text = (f"""
        School: {school_name}<br>
        Score:{score}<br>
        Building Status: {status_text}<br>
        Electricity: {'Yes' if electricity == 1 else 'No'}<br>
        Functional Toilets: {functional_toilets}
        """)

        # Add Marker to the Map
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_text, max_width=400),
            icon=folium.Icon(color=color)
        ).add_to(m)

    # Plot Earthquake Points
    for _, row in earthquake_gdf.iterrows():
        folium.CircleMarker(
            location=[row['LAT'], row['LONG_']],
            radius=5,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.7,
            popup=f"Earthquake Point: {row['MW']} Magnitude"
        ).add_to(m)

    # Plot Fault Lines
    for _, row in fault_gdf.iterrows():
        folium.GeoJson(
            data=row['geometry'],
            style_function=lambda x: {'color': 'purple', 'weight': 3},
            name='Fault Line'
        ).add_to(m)

    # Plot Water Bodies
    for _, row in water_gdf.iterrows():
        folium.GeoJson(
            data=row['geometry'],
            style_function=lambda x: {'color': 'cyan', 'weight': 3},
            name='Water Body'
        ).add_to(m)

    # Plot Open Spaces
    for _, row in open_space_gdf.iterrows():
        folium.GeoJson(
            data=row['geometry'],
            style_function=lambda x: {'color': 'lightgreen', 'weight': 1},
            name='Open Space'
        ).add_to(m)

    # Add Legend
    legend_html = '''
    <div style="position: fixed;
                bottom: 50px; left: 50px; width: 220px; height: 170px;
                background-color: white; z-index:9999; font-size:14px;
                border-radius:10px; padding: 10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.3);">
        <i class="fa fa-map-marker fa-1x" style="color:red"></i> Low Shelter Score<br>
        <i class="fa fa-map-marker fa-1x" style="color:orange"></i> Medium Shelter Score<br>
        <i class="fa fa-map-marker fa-1x" style="color:green"></i> High Shelter Score<br>
        <i style="background:blue; width: 10px; height: 10px; display: inline-block;"></i> Earthquake Point<br>
        <i style="background:purple; width: 10px; height: 10px; display: inline-block;"></i> Fault Line<br>
        <i style="background:cyan; width: 10px; height: 10px; display: inline-block;"></i> Water Body<br>
        <i style="background:lightgreen; width: 10px; height: 10px; display: inline-block;"></i> Open Space
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    map_path = '/content/drive/MyDrive/Module 5/Delhi/School_Shelter_Map.html'
    m.save(map_path)
    print(f"Map saved!")
    m

    #Visulaisation
    import folium
    import pandas as pd
    import geopandas as gpd

    score_gdf = pd.read_csv('/content/drive/MyDrive/Module 5/Delhi/School_Scores.csv')
    earthquake_gdf = gpd.read_file('/content/drive/MyDrive/Module 5/Delhi/Earthquake.shp')
    fault_gdf = gpd.read_file('/content/drive/MyDrive/Module 5/Delhi/Fault.shp')
    water_gdf = gpd.read_file('/content/drive/MyDrive/Module 5/Delhi/Waterbody.shp')

    # Convert Metro Data to GeoDataFrame
    #geometry = [Point(xy) for xy in zip(metro_data['Longitude'], metro_data['Latitude'])]
    #metro_gdf = gpd.GeoDataFrame(metro_data, geometry=geometry, crs='EPSG:4326')
    #metro_gdf = metro_gdf.to_crs('EPSG:32644')

    # Create Map
    m = folium.Map(location=[28.7041, 77.1025], zoom_start=11)
    colors = ['red', 'orange', 'green']


    for _, row in score_gdf.iterrows():
        school_name = row['SCHOOL_NAME'].split(',')[0]
        score = row['SHELTER_SCORE']
        status = int(row['BLDSTATUS'])
        electricity = int(row['ELECTRIC_YN'])
        functional_toilets = row['TOILETB_FUNC'] + row['TOILETG_FUNC']

        if score <= 3:
            color_index = 0
        elif score <= 7:
            color_index = 1
        else:
            color_index = 2

        if color_index > 0:
            if status == 3:
                color_index = max(color_index - 1, 0)
                status_text = 'Under Construction'
            elif status == 2:
                color_index = max(color_index - 1, 0)
                status_text = 'Partially Damaged'
            else:
                status_text = 'Functional'

            if electricity == 0:
                color_index = max(color_index - 1, 0)
        else:
            status_text = 'Functional' if status == 1 else 'Partially Damaged' if status == 2 else 'Under Construction'


        color = colors[color_index]

        popup_text = (f"""
        School: {school_name}<br>
        Score:{score}<br>
        Building Status: {status_text}<br>
        Electricity: {'Yes' if electricity == 1 else 'No'}<br>
        Functional Toilets: {functional_toilets}
        """)

        #School_Marker
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_text, max_width=400),
            icon=folium.Icon(color=color)
        ).add_to(m)

    #Earthquake Points
    for _, row in earthquake_gdf.iterrows():
        folium.CircleMarker(
            location=[row['LAT'], row['LONG_']],
            radius=5,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.7,
            popup=f"Earthquake Point: {row['MW']} Magnitude"
        ).add_to(m)

    #Fault Lines
    for _, row in fault_gdf.iterrows():
        folium.GeoJson(
            data=row['geometry'],
            style_function=lambda x: {'color': 'purple', 'weight': 3},
            name='Fault Line'
        ).add_to(m)

    #Water Bodies
    for _, row in water_gdf.iterrows():
        folium.GeoJson(
            data=row['geometry'],
            style_function=lambda x: {'color': 'cyan', 'weight': 3},
            name='Water Body'
        ).add_to(m)


    legend_html = '''
    <div style="position: fixed;
                bottom: 50px; left: 50px; width: 220px; height: 150px;
                background-color: white; z-index:9999; font-size:14px;
                border-radius:10px; padding: 10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.3);">
        <i class="fa fa-map-marker fa-1x" style="color:red"></i> Low Shelter Score<br>
        <i class="fa fa-map-marker fa-1x" style="color:orange"></i> Medium Shelter Score<br>
        <i class="fa fa-map-marker fa-1x" style="color:green"></i> High Shelter Score<br>
        <i style="background:blue; width: 10px; height: 10px; display: inline-block;"></i> Earthquake Point<br>
        <i style="background:purple; width: 10px; height: 10px; display: inline-block;"></i> Fault Line<br>
        <i style="background:cyan; width: 10px; height: 10px; display: inline-block;"></i> Water Body
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    map_path = '/content/drive/MyDrive/Module 5/Delhi/Adjusted_School_Shelter_Map.html'
    m.save(map_path)
    print(f"Map saved!")
    m
