from flask import Flask, render_template, request
from visualization import *

app = Flask(__name__, template_folder="../templates", static_url_path='', static_folder='../static',)
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/architecture')
def architecture():
    return render_template('architecture.html')

@app.route('/literature_survey', methods=['GET', 'POST'])
def literature_survey():
    return render_template('literature-survey.html')

@app.route('/fire_risk', methods=['GET', 'POST'])
def fire_risk():
    return render_template('fire_risk.html')

@app.route('/resource', methods=['GET', 'POST'])
def resource():
    import pandas as pd

    def load_data(file_path):
        # Check if the file is a CSV or Excel based on the file extension
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Only .csv and .xlsx are supported.")
        
        # Extract first 30 records and summary statistics
        df_sample = df.head(30)  # First 30 records
        df_desc = df.describe().to_dict()  # Summary statistics
        
        return {"data": df_sample.to_dict(orient="records"), "description": df_desc}


    # Load data from CSV files
    data_list1, data_list2, data_list3, data_list4, data_list5 = [], [], [], [], []
    data_list1.append(load_data("../files/boundaries.xlsx"))
    data_list2.append(load_data("../files/occ_count.xlsx"))
    data_list3.append(load_data("../files/Population_data.csv"))
    data_list4.append(load_data("../files/fire_data.csv"))
    data_list5.append(load_data("../files/intermediate.csv"))
    return render_template('resource.html', data_list1 = data_list1, data_list2 = data_list2, data_list3 = data_list3, data_list4 = data_list4, data_list5 = data_list5)

@app.route('/infrastructure', methods=['GET', 'POST'])
def infrastructure():
    if request.method == 'POST':
        # Get the list of uploaded files
        shapefiles = request.files.get('file1')  # Assuming these are the .shp files
        road_data_file = request.files.get('file2')  # Assuming this is road data
        railways_data_file = request.files.get('file3')  # Assuming this is railways data
        buildings_data_file = request.files.get('file4')
        shapefilesshx = request.files.get('file1shx')  # Assuming these are the .shp files
        road_data_fileshx = request.files.get('file2shx')  # Assuming this is road data
        railways_data_fileshx = request.files.get('file3shx')  # Assuming this is railways data
        buildings_data_fileshx = request.files.get('file4shx')
        earthquake_data_file = request.files.get('file5')  # Assuming this is the .csv file
        risk_data_file = request.files.get('file6')

        print(f"Shapefile received: {shapefiles.filename if shapefiles else 'None'}")
        print(f"Road Data received: {road_data_file.filename if road_data_file else 'None'}")
        print(f"Railways Data received: {railways_data_file.filename if railways_data_file else 'None'}")
        print(f"Railways Data received: {buildings_data_file.filename if buildings_data_file else 'None'}")
        print(f"Earthquake Data received: {earthquake_data_file.filename if earthquake_data_file else 'None'}")

        # For simplicity, you can store the files to disk or continue processing in memory
        # Example to save files (optional):
        shapefiles.save(f'../uploads/{shapefiles.filename}')
        road_data_file.save(f'../uploads/{road_data_file.filename}')
        railways_data_file.save(f'../uploads/{railways_data_file.filename}')
        buildings_data_file.save(f'../uploads/{buildings_data_file.filename}')
        shapefilesshx.save(f'../uploads/{shapefilesshx.filename}')
        road_data_fileshx.save(f'../uploads/{road_data_fileshx.filename}')
        railways_data_fileshx.save(f'../uploads/{railways_data_fileshx.filename}')
        buildings_data_fileshx.save(f'../uploads/{buildings_data_fileshx.filename}')
        earthquake_data_file.save(f'../uploads/{earthquake_data_file.filename}')
        risk_data_file.save(f'../uploads/{risk_data_file.filename}')

        # visualize_earthquake(f'../uploads/{shapefiles.filename}', f'../uploads/{earthquake_data_file.filename}')
        # visualize_shapefile(f'../uploads/{shapefiles.filename}', f'../uploads/{road_data_file.filename}', 2)
        # visualize_shapefile(f'../uploads/{shapefiles.filename}', f'../uploads/{railways_data_file.filename}', 3)
        # visualize_shapefile(f'../uploads/{shapefiles.filename}', f'../uploads/{buildings_data_file.filename}', 3)
        # visualize_shapefile(f'../uploads/{shapefiles.filename}', f'../uploads/{road_data_file.filename}', f'../uploads/{railways_data_file.filename}')
        
        return render_template('infrastructure.html', message="Files received successfully!", images=['display/visualize1.png', 'display/visualize2.png', 'display/visualize3.png', 'display/visualize_all.png'], data_list1=data_list1, data_list2=data_list2, data_list3=data_list3)
    data_list1, data_list2, data_list3, data_list4 = [], [], [], []

    # Load first 30 records and their descriptions
    def load_data(file_path):
        df = pd.read_csv(file_path)
        df_sample = df.head(30)  # First 30 records
        df_desc = df.describe().to_dict()  # Summary statistics
        return {"data": df_sample.to_dict(orient="records"), "description": df_desc}

    # Load data from CSV files
    data_list1.append(load_data("../files/building_railway_distances.csv"))
    data_list2.append(load_data("../files/building_road_distances.csv"))
    data_list3.append(load_data("../files/cluster_building_density_with_centroids.csv"))
    data_list4.append(load_data("../files/earthquake_risk_classification.csv"))

    return render_template('infrastructure.html', message="Please upload your files.", data_list1=data_list1, data_list2=data_list2, data_list3=data_list3, data_list4=data_list4)


if __name__ == '__main__':
    app.run(debug=True)
