import geopandas as gpd
from pyproj import CRS
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.impute import KNNImputer
from imblearn.over_sampling import SMOTE
import pandas as pd
import xgboost as xgb
import joblib

from shapely.geometry import Point
from folium import plugins
import scipy.interpolate as interp
from shapely.geometry import Point
import folium
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt


def load_data(file1, file2):
    """Load the two CSV files into pandas DataFrames."""
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    return df1, df2

def merge_datasets(df1, df2):
    """Perform an outer join on longitude and latitude."""
    merged_df = pd.merge(df1, df2, on=["longitude", "latitude"], how="outer")
    return merged_df

def handle_missing_values(df):
    """Fill missing values using interpolation and KNN imputation."""
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')

    df.interpolate(method='linear', inplace=True)

    imputer = KNNImputer(n_neighbors=5)
    numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
    df[numerical_cols] = imputer.fit_transform(df[numerical_cols])

    return df

def apply_smote(df, target_column=None):
    """Apply SMOTE if a classification target column is present."""
    if target_column and target_column in df.columns:
        smote = SMOTE(sampling_strategy="auto", random_state=42)
        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
        X_resampled, y_resampled = smote.fit_resample(df[numerical_cols], df[target_column])

        df_resampled = pd.DataFrame(X_resampled, columns=numerical_cols)
        df_resampled[target_column] = y_resampled
        return df_resampled
    return df

def save_data(df, output_file):
    df.to_csv(output_file, index=False)
    print(f"Merged dataset saved as {output_file}")

def infrastructure_func():
    geology_path = "/content/drive/MyDrive/Module 4/turkey/geo4_2l.shp"
    boundary_path = "/content/drive/MyDrive/Module 4/turkey/tur_adm_2025_ab_shp/tur_admbnda_adm0_2025.shp"
    output_path = "/content/drive/MyDrive/Module 4/turkey/turkey_geology_clipped.shp"

    geology_gdf = gpd.read_file(geology_path)
    boundary_gdf = gpd.read_file(boundary_path)

    print(f"Original CRS (Geology): {geology_gdf.crs}")

    if geology_gdf.crs is None:
        print("Geology CRS missing! Assigning correct projection (LCC for Turkey).")
        geology_gdf = geology_gdf.set_crs("EPSG:4326")

    geology_gdf = geology_gdf.to_crs(epsg=4326)
    boundary_gdf = boundary_gdf.to_crs(epsg=4326)

    print(f"Fixed CRS (Geology): {geology_gdf.crs}")
    print(f"Fixed Bounds (Geology): {geology_gdf.total_bounds}")

    geology_clipped = gpd.overlay(geology_gdf, boundary_gdf, how="intersection")

    geology_clipped.to_file(output_path)
    print(f"Clipped shapefile saved to: {output_path}")



    shapefile_path = "/content/drive/MyDrive/Module 4/turkey/turkey_geology_clipped.shp"
    gdf = gpd.read_file(shapefile_path)

    gdf.plot(figsize=(20, 20), edgecolor='black')

    plt.title("Shapefile Visualization")
    plt.show()

    file_path = "/content/drive/MyDrive/Module 4/earthquakes_in_turkey.csv"
    boundary_shapefile = "/content/drive/MyDrive/Module 4/turkey/tur_adm_2025_ab_shp/tur_admbnda_adm0_2025.shp"
    dem_file = "/content/drive/MyDrive/Module 4/turkey/Turkey_DEM-0000000000-0000000000.tif"
    lithology_file = "/content/drive/MyDrive/Module 4/turkey/turkey_geology_clipped.shp"
    output_path = "/content/drive/MyDrive/Module 4/turkey_features.csv"
    main(file_path, boundary_shapefile, dem_file, lithology_file, output_path)


    if __name__ == "__main__":
        file1 = "/content/drive/MyDrive/Module 4/features_turkey.csv"
        file2 = "/content/drive/MyDrive/Module 4/turkey_features.csv"
        output_file = "/content/drive/MyDrive/Module 4/turkey_features_combined.csv"

        df1, df2 = load_data(file1, file2)
        merged_df = merge_datasets(df1, df2)
        merged_df = handle_missing_values(merged_df)
        merged_df = apply_smote(merged_df, target_column="risk_classification")
        save_data(merged_df, output_file)



    turkey_features_path = "/content/drive/MyDrive/Module 4/turkey_features_combined.csv"

    df_turkey = pd.read_csv(turkey_features_path)

    print("=== turkey Features Dataset ===")
    df_turkey.info()
    print("\n=== Earthquake Risk Classification Dataset ===")
    df_turkey.info()

    print("\n=== turkey Features Dataset - Numerical Summary ===")
    print(df_turkey.describe())

    print("\n=== Earthquake Risk Classification Dataset - Numerical Summary ===")
    print(df_turkey.describe())

    categorical_columns_turkey = df_turkey.select_dtypes(include=['object']).columns
    categorical_columns_earthquake = df_turkey.select_dtypes(include=['object']).columns

    print("\n=== turkey Features Dataset - Categorical Columns ===")
    for col in categorical_columns_turkey:
        print(f"{col}: {df_turkey[col].unique()}")

    print("\n=== Earthquake Risk Classification Dataset - Categorical Columns ===")
    for col in categorical_columns_earthquake:
        print(f"{col}: {df_turkey[col].unique()}")


    def load_xgboost_model(model_path):
        """Loads a pre-trained XGBoost model."""
        xgb_model = joblib.load(model_path)
        print("Model loaded successfully!")
        return xgb_model

    def preprocess_data(df, feature_columns):
        """Ensure dataset is numeric and matches model's input features."""
        df = df[feature_columns].copy()
        df = df.apply(pd.to_numeric, errors='coerce')
        df.fillna(df.mean(), inplace=True)
        return df

    def make_predictions(model, df):
        """Make predictions using the XGBoost model."""
        predictions = model.predict(df)
        return predictions

    if __name__ == "__main__":

        dataset_path = "/content/drive/MyDrive/Module 4/turkey_features_combined.csv"
        model_path = "/content/drive/MyDrive/Module 4/xgboost_iran_earthquake_risk.pkl"
        output_path = "/content/drive/MyDrive/Module 4/turkey_predictions.csv"

        df = pd.read_csv(dataset_path)

        feature_columns = [
            "magnitude_x", "epicenter_density", "magnitude_density", "pga_density", "distance_from_epicenter",
            "elevation", "slope", "index_right", "magnitude_y",
            "distance_to_building", "distance_to_road", "distance_to_railway", "building_density"
        ]

        if "latitude" not in df.columns or "longitude" not in df.columns:
            raise ValueError("Latitude and Longitude columns are missing from the dataset!")

        df_features = preprocess_data(df, feature_columns)

        model = load_xgboost_model(model_path)

        df["risk_prediction"] = make_predictions(model, df_features)

        df[["latitude", "longitude", "risk_prediction"]].to_csv(output_path, index=False)

        print(f"Predictions saved to {output_path}")


    df['risk_prediction'].describe()


    def load_earthquake_data(csv_path, risk_column):
        """Loads the earthquake predictions CSV and converts it into a GeoDataFrame."""
        df = pd.read_csv(csv_path)

        if "latitude" not in df.columns or "longitude" not in df.columns:
            raise ValueError("CSV file must contain 'Latitude' and 'Longitude' columns!")

        risk_labels = {0: "Low Risk", 1: "Moderate Risk", 2: "High Risk"}
        df["predicted_risk_label"] = df[risk_column].map(risk_labels)

        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["longitude"], df["latitude"]), crs="EPSG:4326")

        return gdf

    shapefile_path = "/content/drive/MyDrive/Module 4/turkey/tur_adm_2025_ab_shp/tur_admbnda_adm0_2025.shp"
    csv_path = "/content/drive/MyDrive/Module 4/turkey_predictions.csv"

    turkey_boundaries_gdf = gpd.read_file(shapefile_path)

    grid_gdf = load_earthquake_data(csv_path, "risk_prediction")

    grid_gdf = grid_gdf.to_crs(turkey_boundaries_gdf.crs)

    color_map = {"Low Risk": "green", "Moderate Risk": "orange", "High Risk": "red"}
    grid_gdf["color"] = grid_gdf["predicted_risk_label"].map(color_map)

    fig, ax = plt.subplots(figsize=(12, 8))

    turkey_boundaries_gdf.plot(ax=ax, color='lightgray', edgecolor='black', linewidth=0.5)

    grid_gdf.plot(ax=ax, color=grid_gdf["color"], markersize=5, alpha=0.7, label="Risk Zones")

    plt.title("Earthquake Risk Prediction for Turkey")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)

    plt.legend(handles=[
        plt.Line2D([0], [0], marker='o', color='w', label='Low Risk', markersize=10, markerfacecolor="green"),
        plt.Line2D([0], [0], marker='o', color='w', label='Moderate Risk', markersize=10, markerfacecolor="orange"),
        plt.Line2D([0], [0], marker='o', color='w', label='High Risk', markersize=10, markerfacecolor="red")
    ])

    plt.show()



    def load_earthquake_data(csv_path, risk_column):
        """Loads the earthquake predictions CSV and converts it into a GeoDataFrame."""
        df = pd.read_csv(csv_path)

        if "latitude" not in df.columns or "longitude" not in df.columns:
            raise ValueError("CSV file must contain 'Latitude' and 'Longitude' columns!")

        risk_labels = {0: "Low Risk", 1: "Moderate Risk", 2: "High Risk"}
        df["predicted_risk_label"] = df[risk_column].map(risk_labels)

        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["longitude"], df["latitude"]), crs="EPSG:4326")

        return gdf

    # File paths
    shapefile_path = "/content/drive/MyDrive/Module 4/turkey/tur_adm_2025_ab_shp/tur_admbnda_adm0_2025.shp"
    csv_path = "/content/drive/MyDrive/Module 4/turkey_predictions.csv"

    # Load data
    turkey_boundaries_gdf = gpd.read_file(shapefile_path)
    grid_gdf = load_earthquake_data(csv_path, "risk_prediction")

    # Create a base map centered around Turkey (latitude, longitude roughly)
    m = folium.Map(location=[39.0, 35.0], zoom_start=6)

    # Define color mapping for risk levels
    color_map = {"Low Risk": "green", "Moderate Risk": "orange", "High Risk": "red"}

    # Add earthquake risk markers to the map
    for _, row in grid_gdf.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=5,
            color=color_map.get(row['predicted_risk_label'], 'gray'),
            fill=True,
            fill_color=color_map.get(row['predicted_risk_label'], 'gray'),
            fill_opacity=0.7,
            popup=f"Risk: {row['predicted_risk_label']}",
        ).add_to(m)

    # Add country boundaries layer to the map
    folium.GeoJson(turkey_boundaries_gdf).add_to(m)

    # Add legend
    legend_html = """
        <div style="position: fixed; bottom: 10px; left: 10px; width: 120px; height: 120px;
        background-color: white; border:2px solid black; z-index: 9999; font-size: 12px;">
            <div style="background-color: green; height: 20px; width: 20px;"></div> Low Risk <br>
            <div style="background-color: orange; height: 20px; width: 20px;"></div> Moderate Risk <br>
            <div style="background-color: red; height: 20px; width: 20px;"></div> High Risk
        </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Show map
    m.save("earthquake_risk_map.html")
    m

    shapefile_path = "/content/drive/MyDrive/Module 4/turkey/tur_adm_2025_ab_shp/tur_admbnda_adm0_2025.shp"
    csv_path = "/content/drive/MyDrive/Module 4/turkey_predictions.csv"

    turkey_gdf = gpd.read_file(shapefile_path)
    turkey_boundary = turkey_gdf.geometry.unary_union

    df = pd.read_csv(csv_path, usecols=["latitude", "longitude", "risk_prediction"])
    x, y, z = df["longitude"].values, df["latitude"].values, df["risk_prediction"].values

    grid_x, grid_y = np.meshgrid(
        np.linspace(min(x), max(x), 200),
        np.linspace(min(y), max(y), 200)
    )

    grid_z = interp.griddata((x, y), z, (grid_x, grid_y), method="linear")

    grid_points = gpd.GeoDataFrame(geometry=[Point(lon, lat) for lon, lat in zip(grid_x.flatten(), grid_y.flatten())], crs="EPSG:4326")

    filtered_points = grid_points.sjoin(turkey_gdf, predicate="within", how="inner")

    valid_idx = filtered_points.index

    grid_z_flat = grid_z.flatten()
    grid_z_masked = np.full(grid_z_flat.shape, np.nan)
    grid_z_masked[valid_idx] = grid_z_flat[valid_idx]

    grid_z = grid_z_masked.reshape(grid_x.shape)

    fig, ax = plt.subplots(figsize=(10, 6))
    turkey_gdf.plot(ax=ax, color="lightgray", edgecolor="black", linewidth=0.5)

    contour = ax.contourf(grid_x, grid_y, grid_z, levels=[0, 0.5, 1.5, 2], colors=["green", "yellow", "red"], alpha=0.6)

    plt.title("Earthquake Risk Zones for Turkey")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)

    from matplotlib.patches import Patch
    legend_patches = [
        Patch(color="green", label="Low Risk"),
        Patch(color="yellow", label="Moderate Risk"),
        Patch(color="red", label="High Risk"),
    ]
    ax.legend(handles=legend_patches, loc="upper right")

    plt.show()


    # Paths to shapefile and CSV
    shapefile_path = "/content/drive/MyDrive/Module 4/turkey/tur_adm_2025_ab_shp/tur_admbnda_adm0_2025.shp"
    csv_path = "/content/drive/MyDrive/Module 4/turkey_predictions.csv"

    # Load Turkey shapefile
    turkey_gdf = gpd.read_file(shapefile_path)

    # Load earthquake predictions CSV and clean the column names
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    # Get the longitude, latitude, and risk prediction columns
    x, y, z = df["longitude"].values, df["latitude"].values, df["risk_prediction"].values

    # Create a grid for interpolation
    grid_x, grid_y = np.meshgrid(
        np.linspace(min(x), max(x), 200),
        np.linspace(min(y), max(y), 200)
    )

    # Interpolate the risk predictions onto the grid
    grid_z = interp.griddata((x, y), z, (grid_x, grid_y), method="linear")

    # Create a GeoDataFrame for the grid points
    grid_points = gpd.GeoDataFrame(geometry=[Point(lon, lat) for lon, lat in zip(grid_x.flatten(), grid_y.flatten())], crs="EPSG:4326")

    # Filter grid points to those inside Turkey's boundaries
    filtered_points = grid_points.sjoin(turkey_gdf, predicate="within", how="inner")

    valid_idx = filtered_points.index

    # Mask the grid values based on valid points
    grid_z_flat = grid_z.flatten()
    grid_z_masked = np.full(grid_z_flat.shape, np.nan)
    grid_z_masked[valid_idx] = grid_z_flat[valid_idx]

    # Reshape the masked grid values
    grid_z = grid_z_masked.reshape(grid_x.shape)

    # Create a Folium map centered around Turkey
    m = folium.Map(location=[38.9637, 35.2433], zoom_start=6)

    # Color mapping for risk zones
    color_map = {0: "green", 1: "yellow", 2: "red"}

    # Add the grid points to the map
    for lon, lat, risk in zip(grid_x.flatten(), grid_y.flatten(), grid_z.flatten()):
        if not np.isnan(risk):
            color = color_map.get(int(risk), "gray")  # Default to gray if risk is invalid
            folium.CircleMarker(location=[lat, lon], radius=3, color=color, fill=True, fill_opacity=0.6).add_to(m)

    # Optionally, you can also add the boundary of Turkey as a GeoJSON layer
    geojson = turkey_gdf.to_json()
    folium.GeoJson(geojson, name="Turkey Boundary", style_function=lambda x: {'color': 'black', 'weight': 1}).add_to(m)

    # Save the map to an HTML file
    m.save("/content/earthquake_risk_map_turkey.html")

    # Display map inline
    m
