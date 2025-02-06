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

        return render_template('infrastructure.html', message="Files received successfully!", images=['display/visualize1.png', 'display/visualize2.png', 'display/visualize3.png', 'display/visualize_all.png'])

    return render_template('infrastructure.html', message="Please upload your files.")


if __name__ == '__main__':
    app.run(debug=True)
