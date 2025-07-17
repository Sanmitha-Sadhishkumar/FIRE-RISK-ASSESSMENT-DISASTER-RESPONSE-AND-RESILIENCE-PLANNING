import pandas as pd
import numpy as np
from scipy.spatial import KDTree

def resource_func():
    # Load data
    df = pd.read_csv('/content/drive/MyDrive/Module 2/final_data.csv')
    df['acq_date'] = pd.to_datetime(df['acq_date'])  # Ensure date format

    # Define scaling factors
    fire_per_1000_population = 20
    medical_per_1000_population = 10
    police_per_1000_population = 10

    # Store results
    allocations = []

    # Precompute state centroids and KDTree for fast lookup
    state_centroids = df.groupby('State')[['latitude', 'longitude']].mean()
    kdtree = KDTree(state_centroids.values)
    state_index_map = {state: i for i, state in enumerate(state_centroids.index)}

    # Function to find the nearest states
    def find_nearby_states(state, k=5):
        if state not in state_index_map:
            return []
        _, indices = kdtree.query(state_centroids.loc[state], k=k+1)  # +1 to exclude itself
        return [state_centroids.index[i] for i in indices if state_centroids.index[i] != state]

    # Group by date and sort within each date
    for date, group in df.groupby('acq_date'):
        group = group.sort_values(by='Fire_Intensity', ascending=False)

        # Track available personnel per state
        state_resources = {state: {
            'firefighters': group[group['State'] == state]['firefighters'].iloc[0],
            'medical': group[group['State'] == state]['medical'].iloc[0],
            'police': group[group['State'] == state]['police'].iloc[0],
            'fire_intensity': group[group['State'] == state]['Fire_Intensity'].iloc[0]
        } for state in group['State'].unique()}

        # Initial allocation
        for _, row in group.iterrows():
            state = row['State']
            population = row['Population']
            fire_intensity = row['Fire_Intensity']
            lat, lon = row['latitude'], row['longitude']
            available_firefighters = state_resources[state]['firefighters']
            available_medical = state_resources[state]['medical']
            available_police = state_resources[state]['police']

            # Calculate required personnel based on fire intensity for firefighters
            required_firefighters = int(fire_intensity * fire_per_1000_population)  # Firefighters based on fire intensity
            required_medical = int((population / 1000) * medical_per_1000_population)
            required_police = int((population / 1000) * police_per_1000_population)

            # Allocate available resources based on the calculated requirements
            allocated_firefighters = min(required_firefighters, available_firefighters)
            allocated_medical = min(required_medical, available_medical)
            allocated_police = min(required_police, available_police)

            # Deduct allocated resources
            state_resources[state]['firefighters'] -= allocated_firefighters
            state_resources[state]['medical'] -= allocated_medical
            state_resources[state]['police'] -= allocated_police

            # Store initial allocation data
            allocations.append([lat, lon, state, fire_intensity, population, available_firefighters, available_medical, available_police, date, allocated_firefighters, allocated_medical, allocated_police])

    # Save initial allocation
    initial_alloc_df = pd.DataFrame(allocations, columns=['latitude', 'longitude', 'State', 'Fire_Intensity', 'Population', 'Available_Firefighters', 'Available_Medical', 'Available_Police', 'date', 'firefighters_allocated', 'medical_allocated', 'police_allocated'])
    initial_alloc_df.to_csv('/content/drive/MyDrive/Module 2/initial_alloc2.csv', index=False)

    # Extra allocation step with reallocation
    for i, row in initial_alloc_df.iterrows():
        state = row['State']
        required_firefighters = int(row['Fire_Intensity'] * fire_per_1000_population) - row['firefighters_allocated']
        required_medical = int((row['Population'] / 1000) * medical_per_1000_population) - row['medical_allocated']
        required_police = int((row['Population'] / 1000) * police_per_1000_population) - row['police_allocated']

        if required_firefighters > 0 or required_medical > 0 or required_police > 0:
            # First, try reallocating from states with no fire (no fire intensity that day)
            no_fire_states = [state for state, resources in state_resources.items() if resources['fire_intensity'] == 0]
            for donor_state in no_fire_states:
                if donor_state not in state_resources:  # Skip if donor state has no available resources
                    continue

                # Reallocate firefighters
                if required_firefighters > 0 and state_resources[donor_state]['firefighters'] > 0:
                    additional_firefighters = min(state_resources[donor_state]['firefighters'], required_firefighters)
                    initial_alloc_df.at[i, 'firefighters_allocated'] += additional_firefighters
                    state_resources[donor_state]['firefighters'] -= additional_firefighters
                    required_firefighters -= additional_firefighters
                    print(f"Reallocated {additional_firefighters} firefighters from {donor_state} to {state}")

                # Reallocate medical personnel
                if required_medical > 0 and state_resources[donor_state]['medical'] > 0:
                    additional_medical = min(state_resources[donor_state]['medical'], required_medical)
                    initial_alloc_df.at[i, 'medical_allocated'] += additional_medical
                    state_resources[donor_state]['medical'] -= additional_medical
                    required_medical -= additional_medical
                    print(f"Reallocated {additional_medical} medical personnel from {donor_state} to {state}")

                # Reallocate police personnel
                if required_police > 0 and state_resources[donor_state]['police'] > 0:
                    additional_police = min(state_resources[donor_state]['police'], required_police)
                    initial_alloc_df.at[i, 'police_allocated'] += additional_police
                    state_resources[donor_state]['police'] -= additional_police
                    required_police -= additional_police
                    print(f"Reallocated {additional_police} police personnel from {donor_state} to {state}")

                # Stop once all required resources are allocated
                if required_firefighters == 0 and required_medical == 0 and required_police == 0:
                    break  # Stop if all needs are met

            # If unmet needs still exist, fall back to nearby states
            if required_firefighters > 0 or required_medical > 0 or required_police > 0:
                nearby_states = find_nearby_states(state, k=5)
                for donor_state in nearby_states:
                    if donor_state not in state_resources:  # Skip if donor state has no available resources
                        continue

                    # Reallocate firefighters
                    if required_firefighters > 0 and state_resources[donor_state]['firefighters'] > 0:
                        additional_firefighters = min(state_resources[donor_state]['firefighters'], required_firefighters)
                        initial_alloc_df.at[i, 'firefighters_allocated'] += additional_firefighters
                        state_resources[donor_state]['firefighters'] -= additional_firefighters
                        required_firefighters -= additional_firefighters
                        print(f"Reallocated {additional_firefighters} firefighters from {donor_state} to {state}")

                    # Reallocate medical personnel
                    if required_medical > 0 and state_resources[donor_state]['medical'] > 0:
                        additional_medical = min(state_resources[donor_state]['medical'], required_medical)
                        initial_alloc_df.at[i, 'medical_allocated'] += additional_medical
                        state_resources[donor_state]['medical'] -= additional_medical
                        required_medical -= additional_medical
                        print(f"Reallocated {additional_medical} medical personnel from {donor_state} to {state}")

                    # Reallocate police personnel
                    if required_police > 0 and state_resources[donor_state]['police'] > 0:
                        additional_police = min(state_resources[donor_state]['police'], required_police)
                        initial_alloc_df.at[i, 'police_allocated'] += additional_police
                        state_resources[donor_state]['police'] -= additional_police
                        required_police -= additional_police
                        print(f"Reallocated {additional_police} police personnel from {donor_state} to {state}")

                    # Stop once all required resources are allocated
                    if required_firefighters == 0 and required_medical == 0 and required_police == 0:
                        break  # Stop if all needs are met

    # Save final allocation
    initial_alloc_df.to_csv('/content/drive/MyDrive/Module 2/resourcealloc.csv', index=False)

    print("Resource allocation completed and saved to Google Drive!")
    import pandas as pd
    import openrouteservice
    from openrouteservice import convert
    import ast
    import time

    # Load data
    allocation_df = pd.read_csv("/content/drive/MyDrive/Module 2/final_allocation_new.csv")
    boundaries_df = pd.read_excel("/content/drive/MyDrive/Module 2/boundaries.xlsx")

    # Clean column names
    allocation_df.columns = allocation_df.columns.str.strip()
    boundaries_df.columns = boundaries_df.columns.str.strip()

    # Filter borrowed firefighter records (first 10 only)
    borrowed_df = allocation_df[allocation_df["Borrowed_Firefighters_Detail"] != "{}"].head(30)

    # ORS client
    client = openrouteservice.Client(key="5b3ce3597851110001cf624875b52f41a7004c508cf77b238e2e3517")

    # Store only successful routes
    successful_routes = []

    for idx, row in borrowed_df.iterrows():
        try:
            fire_lat = row['latitude']
            fire_lon = row['longitude']
            borrowed_dict = ast.literal_eval(row['Borrowed_Firefighters_Detail'])

            if not borrowed_dict:
                continue

            # Use first donor state
            first_state = next(iter(borrowed_dict))
            state_row = boundaries_df[boundaries_df['name'] == first_state]

            if state_row.empty:
                print(f" No coordinates for donor state: {first_state}")
                continue

            src_lat = float(state_row.iloc[0]['intptlat'])
            src_lon = float(state_row.iloc[0]['intptlon'])

            # Get road-based route
            coords = ((src_lon, src_lat), (fire_lon, fire_lat))

            time.sleep(1)

            route_result = client.directions(coords,profile='driving-car', preference='shortest')
            geometry = route_result['routes'][0]['geometry']
            decoded = convert.decode_polyline(geometry)

            # Format (lat, lon)
            route = [(point[1], point[0]) for point in decoded['coordinates']]

            successful_routes.append({
                'Fire_Location_Lat': fire_lat,
                'Fire_Location_Lon': fire_lon,
                'Borrowed_State': first_state,
                'Source_Lat': src_lat,
                'Source_Lon': src_lon,
                'Route': str(route)
            })

            print(f"Route found: {first_state} → Fire at ({fire_lat}, {fire_lon})")
            print(f"Route: {route}\n")

        except Exception as e:
            continue

    # Save only successful ones
    routes_df = pd.DataFrame(successful_routes)
    routes_df.to_csv("/content/drive/MyDrive/Module 2/path.csv", index=False)
    print(f"\n Saved routes.")
