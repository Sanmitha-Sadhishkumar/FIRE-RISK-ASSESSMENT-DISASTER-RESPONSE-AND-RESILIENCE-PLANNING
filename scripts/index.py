from flask import Flask, render_template, request
from visualization import *
from safe_zone import *
from infrastructure import *
from building_collapse import *
from resource import *
from emergency_shelter import *
from fire_risk import *

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
    if request.method == 'POST':
        lat = request.form.get('file1')  # Or request.form['file1']
        long = request.form.get('file2') # Or request.form['file2']
        #fire_risk_func()
        if type(lat) is str:
                return render_template('fire_risk.html', image=True, html1="Fire_Spread_Simulation.html", html2="Combined_Chennai_Emergency_Map.html")
        
    return render_template('fire_risk.html')

@app.route('/shelter_asses', methods=['GET', 'POST'])
def shelter_asses():
    if request.method == 'POST':
        college_file = request.files.get('file1')  # Assuming these are the .shp files
        pop_den_file = request.files.get('file2')  # Assuming this is road data
        metro_file = request.files.get('file3')  # Assuming this is railways data
        fault_file = request.files.get('file4')
        faultshx_file = request.files.get('file5')
        earthquake_file = request.files.get('file6')
        earthquakeshx_file = request.files.get('file7')
        waterbody_file = request.files.get('file8')
        waterbodyshx_file = request.files.get('file9')
        landuse_file = request.files.get('file10')
        landuseshx_file = request.files.get('file11')
        #emergency_shelter_func()
        if college_file.filename.startswith('college'):
                return render_template('shelter_assess.html', image=True, html1="college_map.html", html2="College_Shelter_Map.html")
        elif college_file.filename.startswith('school'):
                return render_template('shelter_assess.html', image=True, html1="school_map.html", html2="School_Shelter_Map.html")
        
    return render_template('shelter_assess.html')

@app.route('/building_collapse', methods=['GET', 'POST'])
def building_collapse():
    if request.method == 'POST':
        pre_file = request.files.get('file1')  # Assuming these are the .shp files
        post_file = request.files.get('file2')
        #building_collapse_func()
        if pre_file.filename:
            return render_template('building_collapse.html', image=True, html1="damage_map.html", html2="shelter_analysis_map_with_route_with_damage.html")
         
    return render_template('building_collapse.html')

@app.route('/module1', methods=['GET', 'POST'])
def module1():
    return render_template('module1.html')

@app.route('/safe_zone', methods=['GET', 'POST'])
def safe_zone():
    if request.method == 'POST':
        tents_file = request.files.get('file1')  # Assuming these are the .shp files
        fire_file = request.files.get('file2')  # Assuming this is road data
        damage_file = request.files.get('file3')  # Assuming this is railways data
        crop_file = request.files.get('file4')
        greenhouse_file = request.files.get('file5')
        tentsshx_file = request.files.get('file6')
        #safe_zone_func()
        if tents_file.filename.startswith('model'):
                return render_template('safe_zone.html', image=True, html1="shelter_analysis_map_with_route.html", html2="shelter_analysis_map_with_route_with_damage.html")
        
    return render_template('safe_zone.html')

@app.route('/resource', methods=['GET', 'POST'])
def resource():
    if request.method == 'POST':
        boundary_file = request.files.get('file1')  # Assuming these are the .shp files
        occupation_file = request.files.get('file2')  # Assuming this is road data
        population_data_file = request.files.get('file3')  # Assuming this is railways data
        fire_data_file = request.files.get('file4')
        land_area_file = request.files.get('file5')
        #resource_func()
        if boundary_file.filename.startswith('boundaries'):
                return render_template('resource.html', image=True, html1="initial_allocation_map.html", html2="final_allocation_map.html", html3="final_route_map.html")
        
    return render_template('resource.html')

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
        tiff_data_file = request.files.get('file7')
        litho_data_file = request.files.get('file8')

        print(f"Shapefile received: {shapefiles.filename if shapefiles else 'None'}")
        print(f"Road Data received: {road_data_file.filename if road_data_file else 'None'}")
        print(f"Railways Data received: {railways_data_file.filename if railways_data_file else 'None'}")
        print(f"Railways Data received: {buildings_data_file.filename if buildings_data_file else 'None'}")
        print(f"Earthquake Data received: {earthquake_data_file.filename if earthquake_data_file else 'None'}")

        #infrastructure_func()
        
        if shapefiles.filename.startswith('turkey'):
            return render_template('infrastructure.html', image=True, html1="turkey_risk_points.html", img1="turkey_risk.png", html2="turkey_risk_pred.html", img2="turkey_pred.png")
        elif shapefiles.filename.startswith('delhi'):
            return render_template('infrastructure.html', image=True, html1="delhi_risk_points.html", img1="delhi_risk.png", html2="delhi_risk_pred.html", img2="delhi_pred.png")
        elif shapefiles.filename.startswith('gujarat'):
            return render_template('infrastructure.html', image=True, html1="gujarat_risk_points.html", img1="gujarat_risk.png", html2="gujarat_risk_pred.html", img2="gujarat_pred.png")
    

    return render_template('infrastructure.html', message="Please upload your files.")


if __name__ == '__main__':
    app.run(debug=True)
