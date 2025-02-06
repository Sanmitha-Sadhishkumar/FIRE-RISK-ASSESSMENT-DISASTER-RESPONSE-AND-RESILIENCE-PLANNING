import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')  # Use the non-interactive Agg backend

import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
from shapely.geometry import Point

# Load the CSV for earthquake data
def visualize_earthquake(shapefile_path, csv_path):
    df = pd.read_csv(csv_path, encoding='utf-8')

    # Convert to GeoDataFrame (Check column names and update if needed)
    geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")  # Set CRS to WGS84

    # Load the shapefile for Turkey boundaries
    shapefile_gdf = gpd.read_file(shapefile_path)

    # Plot earthquake points and Turkey boundaries
    fig, ax = plt.subplots(figsize=(10, 10))
    shapefile_gdf.plot(ax=ax, color="lightgray", edgecolor="black", alpha=0.5)  # Plot Turkey boundaries
    gdf.plot(ax=ax, color="red", markersize=5, alpha=0.5)  # Red dots for earthquakes

    # Adding title and labels
    plt.title("Earthquake Locations in Turkey with Boundaries")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.savefig("../static/display/visualize1.png")

def visualize_shapefile(shapefile_path, roads_shapefile_path, i):
    shapefile_gdf = gpd.read_file(shapefile_path)

    # Load the shapefile for roads
    roads_gdf = gpd.read_file(roads_shapefile_path)

    # Plot earthquake points, Turkey boundaries, and roads
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot Turkey boundaries
    shapefile_gdf.plot(ax=ax, color="lightgray", edgecolor="black", alpha=0.5)

    # Plot roads
    roads_gdf.plot(ax=ax, color="blue", linewidth=1, alpha=0.7)

    # Adding title and labels
    plt.title("Earthquake Locations, Turkey Boundaries, and Roads")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    # Show the plot
    plt.savefig(f"../static/display/visualize{i}.png")

def visualize_all(shapefile_path1, shapefile_path2, shapefile_path3):
    gdf1 = gpd.read_file(shapefile_path1)
    print(gdf1.columns)
    gdf2 = gpd.read_file(shapefile_path2)
    print(gdf2.columns)
    gdf3 = gpd.read_file(shapefile_path3)
    print(gdf2.columns)

    # Create a single figure and axis
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot each layer on the same axis
    gdf1.plot(ax=ax, edgecolor='black', label="Layer 1")
    gdf2.plot(ax=ax, edgecolor='red', label="Layer 2")
    gdf3.plot(ax=ax, edgecolor='blue', label="Layer 3")

    # Add legend
    plt.legend(["Layer 1", "Layer 2", "Layer 3"], loc="upper right")
    plt.savefig(f"../static/display/visualize_all.png")