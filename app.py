import duckdb
from flask import Flask, render_template, request

app = Flask(__name__)
continuous_columns = ['Internships', 'Projects', 'AptitudeTestScore', 'SoftSkillsRating', 'SSC_Marks', 'HSC_Marks']
discrete_columns = ['ExtracurricularActivities, PlacementTraining']

@app.route('/')
def index():
    # get x and y axis min/max values 
    scatter_ranges_query = f'SELECT MIN(AptitudeTestScore), MAX(AptitudeTestScore), MIN(CGPA), MAX(CGPA) FROM placementdata.csv' # Retrieves the minimum and maximum X and Y coordinates
    scatter_ranges_results = duckdb.sql(scatter_ranges_query).df() 
    scatter_ranges = scatter_ranges_results.iloc[0].to_list()

    # get minimum and maximum value for each slider
    internship_min_max_query = 'SELECT MIN(Internships), MAX(Internships) FROM placementdata.csv'
    filter_internship_ranges = duckdb.sql(internship_min_max_query).df()

    projects_min_max_query = 'SELECT MIN(Projects), MAX(Projects) FROM placementdata.csv' 
    filter_projects_ranges = duckdb.sql(projects_min_max_query).df()

    aptitude_min_max_query = 'SELECT MIN(AptitudeTestScore), MAX(AptitudeTestScore) FROM placementdata.csv' 
    filter_aptitude_ranges = duckdb.sql(aptitude_min_max_query).df()

    softskills_min_max_query = 'SELECT MIN(SoftSkillsRating), MAX(SoftSkillsRating) FROM placementdata.csv' 
    filter_softskills_ranges = duckdb.sql(softskills_min_max_query).df()
    
    ssc_min_max_query = 'SELECT MIN(SSC_Marks), MAX(SSC_Marks) FROM placementdata.csv' 
    filter_ssc_ranges = duckdb.sql(ssc_min_max_query).df()
    
    hsc_min_max_query = 'SELECT MIN(HSC_Marks), MAX(HSC_Marks) FROM placementdata.csv' 
    filter_hsc_ranges = duckdb.sql(hsc_min_max_query).df()
    
    # dict of all slider ranges
    filter_ranges = {'internships': filter_internship_ranges.iloc[0].to_list(), 
                     'projects': filter_projects_ranges.iloc[0].to_list(), 
                     'aptitude': filter_aptitude_ranges.iloc[0].to_list(),
                     'soft': filter_softskills_ranges.iloc[0].to_list(),
                     'ssc-marks': filter_ssc_ranges.iloc[0].to_list(),
                     'hsc-marks': filter_hsc_ranges.iloc[0].to_list()} 
    
    return render_template(
        'index.html',
        filter_ranges=filter_ranges, 
        scatter_ranges=scatter_ranges,
        x_vals=['FIX THIS LATER', "x val 2"],
        y_vals=['FIX THIS LATER', "FIX 2"],
        facets = ['FIX THIS LATER', 'facet 2']
    )


# TODO: Complete the update_aggregate
@app.route("/update_facet", methods=["POST"])
def update_facet():
    data = request.get_json()
    print(data)

    # app.grouper = data.get("grouper", app.grouper)
    # app.value = data.get("value", app.value)
    # app.agg = data.get("agg", app.agg)

    # # Reset to all 3b
    # app.filters = {}

    # aggregated_data = get_aggregated_data()

    # result = [{"x": str(key), "y": float(value)}
    #           for key, value in aggregated_data.items()]

    # return {'data': result, 'x_column': app.grouper}

    # idea: if x and y change, then we need to just update what we pass as the data for x and y/column to javascript
    return {'data': [], 'x_column': ""}

@app.route('/update', methods=["POST"])
def update():
    request_data = request.get_json()
    print(request_data)
    
    # parameterized query for sliders
    continuous_predicate = ' AND '.join([f'({column} >= {request_data[column][0]} AND {column} <= {request_data[column][1]})' for column in continuous_columns])
    
    # paramaterized query for buttons
    extraval = "Yes"
    if request_data["Extracurricular_Activities"] == False:
        extraval = "No"

    placeval = "Yes"
    if request_data["Placement_Training"] == False:
        placeval = "No"
        
    discrete_predicate = f"(ExtracurricularActivities == '{extraval}') AND (PlacementTraining == '{placeval}')"

    combined_predicate = ' AND '.join([continuous_predicate, discrete_predicate])
    
    placed_predicate = ' AND '.join([combined_predicate, "PlacementStatus == 'Placed'"])
    notplaced_predicate = ' AND '.join([combined_predicate, "PlacementStatus == 'NotPlaced'"])

    # placed data
    scatter_placed_query = f'SELECT AptitudeTestScore, CGPA FROM placementdata.csv WHERE {placed_predicate}'
    scatter_placed_results = duckdb.sql(scatter_placed_query).df()
    scatter_placed_data = scatter_placed_results.to_dict(orient='records') 
    
    # not placed data
    scatter_notplaced_query = f'SELECT AptitudeTestScore, CGPA FROM placementdata.csv WHERE {notplaced_predicate}'
    scatter_notplaced_results = duckdb.sql(scatter_notplaced_query).df()
    scatter_notplaced_data = scatter_notplaced_results.to_dict(orient='records') 
    
    return {'scatter_placed_data': scatter_placed_data, 'scatter_notplaced_data': scatter_notplaced_data}

if __name__ == "__main__":
    app.run(debug=True)
    