import osmnx as ox
import folium
import numpy as np
import random
import time
import osmnx as ox
import folium
import networkx as nx
import pandas as pd
import numpy as np
import random
import requests
import time
from shapely.geometry import Point

def fire_risk_func():
    # Load Chennai Road Network
    G = ox.graph_from_place("Chennai, India", network_type="drive")

    # Get road network as a GeoDataFrame
    edges = ox.graph_to_gdfs(G, nodes=False, edges=True)

    # Initialize Chennai Map
    chennai_map = folium.Map(location=[13.0827, 80.2707], zoom_start=12)

    # Define Fire-Affected Area
    fire_start = (13.0496, 80.2824)  # Fire starting point
    fire_zones = set([fire_start])   # Active fire cells

    from shapely.geometry import Point

    # Fire Spread Simulation
    def spread_fire(fire_zones, steps=10):
        new_fire_zones = set(fire_zones)

        for _ in range(steps):
            next_fire = set()

            for lat, lon in new_fire_zones:
                for dx, dy in [(-0.002, 0), (0.002, 0), (0, -0.002), (0, 0.002)]:
                    new_lat, new_lon = lat + dx, lon + dy
                    point = Point(new_lon, new_lat)  # Convert to Shapely Point

                    # Check if point is near a road
                    is_road = any(edges.geometry.distance(point) < 0.0005)

                    spread_probability = 0.3 if is_road else 0.7  # Slow spread on roads

                    if random.random() < spread_probability:
                        next_fire.add((new_lat, new_lon))

            new_fire_zones.update(next_fire)
            time.sleep(5)

        return new_fire_zones

    # Run Fire Simulation
    final_fire_zones = spread_fire(fire_zones, steps=10)

    # Add Fire Zones to Map
    for lat, lon in final_fire_zones:
        folium.CircleMarker(
            location=[lat, lon], radius=5, color="red",
            fill=True, fill_color="red", fill_opacity=0.5, tooltip="Fire Zone"
        ).add_to(chennai_map)

    chennai_map

    import osmnx as ox
    import folium
    import numpy as np
    import random
    import time
    from shapely.geometry import Point

    # Load Chennai Road Network
    G = ox.graph_from_place("Chennai, India", network_type="drive")
    edges = ox.graph_to_gdfs(G, nodes=False, edges=True)

    # Load Water Bodies & Railways as Fire Blocks
    water_bodies = ox.features_from_place("Chennai, India", {"natural": "water"})
    railways = ox.features_from_place("Chennai, India", {"railway": True})

    # Initialize Chennai Map
    anna_university = (13.0102, 80.2335)  # Anna University, Chennai
    chennai_map = folium.Map(location=anna_university, zoom_start=14)

    # Define Fire-Affected Area
    fire_start = anna_university
    fire_zones = set([fire_start])

    # Fire Spread Simulation
    def spread_fire(fire_zones, steps=10):
        new_fire_zones = set(fire_zones)

        for _ in range(steps):
            next_fire = set()

            for lat, lon in new_fire_zones:
                for dx, dy in [(-0.002, 0), (0.002, 0), (0, -0.002), (0, 0.002)]:
                    new_lat, new_lon = lat + dx, lon + dy
                    point = Point(new_lon, new_lat)  # Convert to Shapely Point

                    # Check if fire is near a road (spreads slower)
                    is_road = any(edges.geometry.distance(point) < 0.0005)

                    # Check if fire reaches a railway or water body (fire blocked)
                    is_fire_blocked = any(water_bodies.geometry.distance(point) < 0.0005) or \
                                    any(railways.geometry.distance(point) < 0.0005)

                    if is_fire_blocked:
                        continue  # Skip fire spread in blocked areas

                    spread_probability = 0.3 if is_road else 0.7  # Slow spread on roads

                    if random.random() < spread_probability:
                        next_fire.add((new_lat, new_lon))

            new_fire_zones.update(next_fire)
            time.sleep(5)

        return new_fire_zones

    # Run Fire Simulation
    final_fire_zones = spread_fire(fire_zones, steps=10)

    # Add Fire Zones to Map
    for lat, lon in final_fire_zones:
        folium.CircleMarker(
            location=[lat, lon], radius=5, color="red",
            fill=True, fill_color="red", fill_opacity=0.5, tooltip="Fire Zone"
        ).add_to(chennai_map)

    # Save Map
    chennai_map.save("Anna_University_Fire_Spread.html")

    chennai_map

    # -------------------------------------
    # 1. Initialize Base Map
    # -------------------------------------
    chennai_center = (13.0827, 80.2707)
    chennai_map = folium.Map(location=chennai_center, zoom_start=12)

    # -------------------------------------
    # 2. Load Road Network and Fire Blocks
    # -------------------------------------
    G = ox.graph_from_place("Chennai, India", network_type="drive")
    edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
    water_bodies = ox.features_from_place("Chennai, India", {"natural": "water"})
    railways = ox.features_from_place("Chennai, India", {"railway": True})

    # -------------------------------------
    # 3. Fire Spread Simulation (around Anna University)
    # -------------------------------------
    anna_university = (13.0102, 80.2335)
    fire_start = anna_university
    fire_zones = set([fire_start])

    def spread_fire(fire_zones, steps=10):
        new_fire_zones = set(fire_zones)

        for _ in range(steps):
            next_fire = set()
            for lat, lon in new_fire_zones:
                for dx, dy in [(-0.002, 0), (0.002, 0), (0, -0.002), (0, 0.002)]:
                    new_lat, new_lon = lat + dx, lon + dy
                    point = Point(new_lon, new_lat)
                    is_road = any(edges.geometry.distance(point) < 0.0005)
                    is_fire_blocked = any(water_bodies.geometry.distance(point) < 0.0005) or \
                                    any(railways.geometry.distance(point) < 0.0005)
                    if is_fire_blocked:
                        continue
                    spread_prob = 0.3 if is_road else 0.7
                    if random.random() < spread_prob:
                        next_fire.add((new_lat, new_lon))
            new_fire_zones.update(next_fire)
        return new_fire_zones

    final_fire_zones = spread_fire(fire_zones, steps=10)

    for lat, lon in final_fire_zones:
        folium.CircleMarker(
            location=[lat, lon], radius=5, color="red",
            fill=True, fill_color="red", fill_opacity=0.5,
            tooltip="Fire Zone"
        ).add_to(chennai_map)

    # -------------------------------------
    # 4. Fire Evacuation: Fire Station → Fire Site → Shelter
    # -------------------------------------
    fire_stations = ox.features_from_place("Chennai, Tamil Nadu, India", {"amenity": "fire_station"})
    shelters = ox.features_from_place("Chennai, Tamil Nadu, India", {"amenity": "shelter"})
    fire_stations = fire_stations[fire_stations.geometry.type == 'Point'].reset_index()
    shelters = shelters[shelters.geometry.type == 'Point'].reset_index()

    fire_affected_point = (13.0496, 80.2824)
    fire_station_coords = (fire_stations.geometry.iloc[0].y, fire_stations.geometry.iloc[0].x)
    shelter_coords = (shelters.geometry.iloc[0].y, shelters.geometry.iloc[0].x)

    fire_affected_node = ox.distance.nearest_nodes(G, fire_affected_point[1], fire_affected_point[0])
    fire_station_node = ox.distance.nearest_nodes(G, fire_station_coords[1], fire_station_coords[0])
    shelter_node = ox.distance.nearest_nodes(G, shelter_coords[1], shelter_coords[0])

    for u, v, k, data in G.edges(keys=True, data=True):
        if 'maxspeed' in data:
            maxspeed = data['maxspeed']
            if isinstance(maxspeed, list):
                maxspeed = min(int(s.split()[0]) for s in maxspeed)
            else:
                maxspeed = int(str(maxspeed).split()[0])
            data['congestion_factor'] = 1 / maxspeed
        else:
            data['congestion_factor'] = 1 / 30

    rescue_route = nx.shortest_path(G, fire_station_node, fire_affected_node, weight='congestion_factor')
    evacuation_route = nx.shortest_path(G, fire_affected_node, shelter_node, weight='congestion_factor')

    rescue_distance = nx.shortest_path_length(G, fire_station_node, fire_affected_node, weight='length')
    evacuation_distance = nx.shortest_path_length(G, fire_affected_node, shelter_node, weight='length')

    avg_speed_kmh = 30
    rescue_time = rescue_distance / (avg_speed_kmh * 1000 / 60)
    evacuation_time = evacuation_distance / (avg_speed_kmh * 1000 / 60)

    rescue_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in rescue_route]
    evacuation_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in evacuation_route]

    folium.PolyLine(rescue_coords, color='red', weight=5, opacity=0.7, tooltip=f"Rescue Route ({rescue_time:.1f} mins)").add_to(chennai_map)
    folium.PolyLine(evacuation_coords, color='blue', weight=5, opacity=0.7, tooltip=f"Evacuation Route ({evacuation_time:.1f} mins)").add_to(chennai_map)

    folium.Marker(fire_station_coords, popup="Fire Station", icon=folium.Icon(color="red")).add_to(chennai_map)
    folium.Marker(fire_affected_point, popup="Fire-Affected Area", icon=folium.Icon(color="orange")).add_to(chennai_map)
    folium.Marker(shelter_coords, popup="Emergency Shelter", icon=folium.Icon(color="green")).add_to(chennai_map)

    # -------------------------------------
    # 5. Real-Time Traffic Data Overlay (TomTom API)
    # -------------------------------------
    api_key = "QmJYwz0fqZAvgi6xOOXN7lGX60NHBgnq"
    top_left = (13.173706, 80.098480)
    bottom_right = (12.822147, 80.305642)

    lat_steps = np.linspace(top_left[0], bottom_right[0], 8)
    lon_steps = np.linspace(top_left[1], bottom_right[1], 8)
    grid_points = [(lat, lon) for lat in lat_steps for lon in lon_steps]

    def get_traffic_data(lat, lon):
        url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={lat},{lon}&key={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None

    traffic_flows = []
    for lat, lon in grid_points:
        data = get_traffic_data(lat, lon)
        if data and "flowSegmentData" in data:
            segment = data["flowSegmentData"]
            coordinates = segment["coordinates"]["coordinate"]
            current_speed = segment["currentSpeed"]
            free_flow_speed = segment["freeFlowSpeed"]
            traffic_flows.append({
                "coordinates": [(coord["latitude"], coord["longitude"]) for coord in coordinates],
                "current_speed": current_speed,
                "free_flow_speed": free_flow_speed
            })
        time.sleep(1)  # Respect API rate limit

    def get_color(speed_ratio):
        if speed_ratio > 0.75:
            return "green"
        elif speed_ratio > 0.5:
            return "orange"
        else:
            return "red"

    for flow in traffic_flows:
        speed_ratio = flow["current_speed"] / flow["free_flow_speed"]
        color = get_color(speed_ratio)
        folium.PolyLine(
            flow["coordinates"], color=color, weight=5, opacity=0.7,
            tooltip=f"Speed: {flow['current_speed']} km/h"
        ).add_to(chennai_map)

    # -------------------------------------
    # 6. Display Combined Map
    # -------------------------------------
    chennai_map.save("Combined_Chennai_Emergency_Map.html")
    chennai_map
