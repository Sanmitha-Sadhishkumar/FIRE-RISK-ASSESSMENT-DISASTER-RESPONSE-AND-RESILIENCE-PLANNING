import os
import json
import cv2
import numpy as np
import rasterio
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from rasterio.transform import rowcol
from shapely.wkt import loads
from shapely.geometry import Polygon
import ipywidgets as widgets
from IPython.display import display, clear_output
import folium
from io import BytesIO
from shapely import wkt
from PIL import Image


# === Analysis ===
def on_button_clicked(b):
    with output:
        clear_output()

        if not post_image_uploader.value or not post_json_uploader.value:
            print("Please upload post-disaster image and JSON.")
            return

        image_filename = list(post_image_uploader.value.keys())[0]
        json_filename = list(post_json_uploader.value.keys())[0]
        image_bytes = BytesIO(post_image_uploader.value[image_filename]["content"])
        json_bytes = BytesIO(post_json_uploader.value[json_filename]["content"])
        data = json.load(json_bytes)

        selected_country = country_dropdown.value
        cost_per_m2 = country_cost_map[selected_country]
        cost_per_sqft = cost_per_m2 / 10.7639
        currency_code, conversion_rate = usd_to_local_currency[selected_country]

        with rasterio.open(image_bytes) as dataset:
            transform = dataset.transform
            height, width = dataset.height, dataset.width
            image = dataset.read([1, 2, 3])
            image = np.stack(image, axis=-1)
            image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

        def lonlat_to_pixel(lon, lat):
            row, col = rowcol(transform, lon, lat)
            return int(col), int(row)

        mask = np.zeros((height, width), dtype=np.uint8)
        for feature in data.get("features", {}).get("lng_lat", []):
            if "wkt" not in feature: continue
            polygon = loads(feature["wkt"])
            pts = np.array([lonlat_to_pixel(x, y) for x, y in polygon.exterior.coords], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.fillPoly(mask, [pts], 255)

        damage_colors = {
            "no-damage": (0, 255, 0),
            "minor-damage": (255, 255, 0),
            "major-damage": (255, 165, 0),
            "destroyed": (255, 0, 0),
            "un-classified": (160, 160, 160)
        }
        damage_percentage = {
            "no-damage": 0.0,
            "minor-damage": 0.25,
            "major-damage": 0.50,
            "destroyed": 1.00
        }

        colored_mask = np.zeros((height, width, 3), dtype=np.uint8)
        all_building_sizes, records, damage_counts = [], [], {}
        latlng_coords = []

        for idx, feature in enumerate(data["features"]["xy"]):
            damage_type = feature["properties"].get("subtype", "un-classified")
            polygon = loads(feature["wkt"])
            coords = np.array(polygon.exterior.coords, dtype=np.int32)
            cv2.fillPoly(colored_mask, [coords], damage_colors.get(damage_type, (255, 255, 255)))

            building_mask = np.zeros_like(mask)
            cv2.fillPoly(building_mask, [coords], 255)
            x, y, w, h = cv2.boundingRect(coords)
            cropped = mask[y:y+h, x:x+w]
            area_pixels = np.count_nonzero(cropped)
            all_building_sizes.append(area_pixels)
            damage_counts[damage_type] = damage_counts.get(damage_type, 0) + 1

        pixels_per_sqft = max(all_building_sizes) / 5000 if all_building_sizes else 10

        for idx, feature in enumerate(data["features"]["xy"]):
            damage_type = feature["properties"].get("subtype", "un-classified")
            polygon = loads(feature["wkt"])
            coords = np.array(polygon.exterior.coords, dtype=np.int32)
            x, y, w, h = cv2.boundingRect(coords)
            cropped = mask[y:y+h, x:x+w]
            area_pixels = np.count_nonzero(cropped)
            area_sqft = area_pixels / pixels_per_sqft
            usd_cost = area_sqft * cost_per_sqft * damage_percentage.get(damage_type, 0.0)
            local_cost = usd_cost * conversion_rate

            lon, lat = polygon.centroid.xy
            latlng_coords.append((lat[0], lon[0]))

            records.append({
                "Building_ID": idx,
                "Damage_Type": damage_type,
                "Building_Size_Pixels": area_pixels,
                "Building_Size_SqFt": round(area_sqft, 2),
                "Reconstruction_Cost_USD": round(usd_cost, 2),
                f"Reconstruction_Cost_{currency_code}": round(local_cost, 2),
                "Latitude": lat[0],
                "Longitude": lon[0]
            })

        df = pd.DataFrame(records)
        os.makedirs("output", exist_ok=True)
        df.to_csv("output/building_cost_estimates.csv", index=False)
        display(df.head())

        # === Visualizations ===
        plt.figure(figsize=(10, 10))
        plt.imshow(colored_mask)
        plt.title("Damage Classification Mask")
        legend_patches = [mpatches.Patch(color=np.array(damage_colors[k])/255, label=k.replace("-", " ").capitalize())
                          for k in damage_counts.keys()]
        plt.legend(handles=legend_patches, loc="lower left", bbox_to_anchor=(1.02, 0.5))
        plt.axis("off")
        plt.tight_layout()
        plt.show()

        plt.figure(figsize=(8, 5))
        plt.bar(damage_counts.keys(), damage_counts.values(),
                color=[np.array(damage_colors[k])/255 for k in damage_counts])
        plt.title("Damage Type Distribution")
        plt.xlabel("Damage Type")
        plt.ylabel("Count")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

        # === Improved Interactive Map ===
        print("Generating interactive map...")
        first_feature = data["features"]["lng_lat"][0]
        first_polygon = wkt.loads(first_feature["wkt"])
        lon, lat = first_polygon.centroid.x, first_polygon.centroid.y
        m = folium.Map(location=[lat, lon], zoom_start=15)

        for feature in data["features"]["lng_lat"]:
            damage_type = feature["properties"].get("subtype", "un-classified")
            color = "#{:02x}{:02x}{:02x}".format(*damage_colors.get(damage_type, (255, 255, 255)))
            polygon = wkt.loads(feature["wkt"])
            if isinstance(polygon, Polygon):
                coords = [[y, x] for x, y in polygon.exterior.coords]
                folium.Polygon(
                    locations=coords,
                    color=color,
                    fill=True,
                    fill_opacity=0.5,
                    popup=f"{damage_type}"
                ).add_to(m)

        m.save("output/damage_map.html")
        display(m)

# === COUNTRY COST DATA ===
country_cost_map = {
    "United States": 506.37,
    "Japan": 435.96,
    "Switzerland": 433.30,
    "Hong Kong": 398.66,
    "Thailand": 369.78,
    "United Kingdom": 360.41,
    "Germany": 351.79,
    "Ireland": 344.61,
    "Australia": 334.01,
    "Brazil": 176.06,
    "Philippines": 120.77,
    "Indonesia": 75.42,
    "India": 27
}
usd_to_local_currency = {
    "United States": ("USD", 1),
    "Japan": ("JPY", 154.3),
    "Switzerland": ("CHF", 0.91),
    "Hong Kong": ("HKD", 7.83),
    "Thailand": ("THB", 36.7),
    "United Kingdom": ("GBP", 0.80),
    "Germany": ("EUR", 0.93),
    "Australia": ("AUD", 1.54),
    "Brazil": ("BRL", 5.17),
    "Philippines": ("PHP", 57.1),
    "Indonesia": ("IDR", 16145.0),
    "India": ("INR", 83.2)
}

def building_collapse_func():
    # === UI Widgets ===
    post_image_uploader = widgets.FileUpload(accept='.tif', multiple=False, description="Upload Post Image")
    post_json_uploader = widgets.FileUpload(accept='.json', multiple=False, description="Upload Post JSON")
    pre_image_uploader = widgets.FileUpload(accept='.tif', multiple=False, description="Upload Pre Image")
    pre_json_uploader = widgets.FileUpload(accept='.json', multiple=False, description="Upload Pre JSON")
    country_dropdown = widgets.Dropdown(
        options=list(country_cost_map.keys()), value="India", description="Select Country:"
    )
    run_button = widgets.Button(description="Run Analysis", button_style='success')
    display(post_image_uploader, post_json_uploader, pre_image_uploader, pre_json_uploader, country_dropdown, run_button)

    output = widgets.Output()
    display(output)
    run_button.on_click(on_button_clicked)