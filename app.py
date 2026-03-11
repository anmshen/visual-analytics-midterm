import duckdb
import numpy as np
from flask import Flask, render_template, request

app = Flask(__name__)
continuous_columns = ['Internships', 'Projects', 'AptitudeTestScore', 'SoftSkillsRating', 'SSC_Marks', 'HSC_Marks']
discrete_columns = ['ExtracurricularActivities, PlacementTraining']
x_axis = 'AptitudeTestScore'
y_axis = 'CGPA'
valid_axes = ['CGPA', 'AptitudeTestScore', 'SoftSkillsRating', 'SSC_Marks', 'HSC_Marks']

def get_regression_coords(df, x_col, y_col):
    if df.empty or len(df) < 2:
        return None
    
    x = df[x_col].values
    y = df[y_col].values
    
    m, b = np.polyfit(x, y, 1)
    
    min_x = float(x.min())
    max_x = float(x.max())
    
    return {
        "x1": min_x,
        "y1": m * min_x + b,
        "x2": max_x,
        "y2": m * max_x + b
    }
    
@app.route('/')
def index():
    # get x and y axis min/max values 
    scatter_ranges_query = f'SELECT MIN({x_axis}), MAX({x_axis}), MIN({y_axis}), MAX({y_axis}) FROM placementdata.csv' # Retrieves the minimum and maximum X and Y coordinates
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
        x_vals=valid_axes,
        y_vals=valid_axes
    )

@app.route('/update', methods=["POST"])
def update():
    request_data = request.get_json()
    print(request_data)
    x_axis = request_data.get('x_axis', 'AptitudeTestScore')
    y_axis = request_data.get('y_axis', 'CGPA')

    ranges_query = f'SELECT MIN({x_axis}), MAX({x_axis}), MIN({y_axis}), MAX({y_axis}) FROM placementdata.csv'
    ranges_results = duckdb.sql(ranges_query).df() 
    axes_ranges = ranges_results.iloc[0].to_list()
    
    # parameterized query for sliders
    continuous_predicate = ' AND '.join([f'({column} >= {request_data[column][0]} AND {column} <= {request_data[column][1]})' for column in continuous_columns])

    extra_vals = ["'Yes'" if v == "True" else "'No'" for v in request_data["Extracurricular_Activities"]]
    place_vals = ["'Yes'" if v == "True" else "'No'" for v in request_data["Placement_Training"]]

    if (not place_vals) or (not extra_vals):
        combined_predicate = continuous_predicate
        print("here")
        return {
            'scatter_placed_data': [],
            'scatter_notplaced_data': [],
            'x_range': axes_ranges[:2],
            'y_range': axes_ranges[2:]
        }
    
    extra_in = ", ".join(extra_vals)
    place_in = ", ".join(place_vals)
    discrete_predicate = f"(ExtracurricularActivities IN ({extra_in})) AND (PlacementTraining IN ({place_in}))"
    combined_predicate = ' AND '.join([continuous_predicate, discrete_predicate])
    
    placed_predicate = ' AND '.join([combined_predicate, "PlacementStatus == 'Placed'"])
    notplaced_predicate = ' AND '.join([combined_predicate, "PlacementStatus == 'NotPlaced'"])

    # placed data
    scatter_placed_query = f'SELECT {x_axis}, {y_axis} FROM placementdata.csv WHERE {placed_predicate}'
    scatter_placed_results = duckdb.sql(scatter_placed_query).df()
    scatter_placed_data = scatter_placed_results.to_dict(orient='records') 
    
    # not placed data
    scatter_notplaced_query = f'SELECT {x_axis}, {y_axis} FROM placementdata.csv WHERE {notplaced_predicate}'
    scatter_notplaced_results = duckdb.sql(scatter_notplaced_query).df()
    scatter_notplaced_data = scatter_notplaced_results.to_dict(orient='records') 
    
    return {'scatter_placed_data': scatter_placed_data, 
            'scatter_notplaced_data': scatter_notplaced_data, 
            'x_range': axes_ranges[:2], 
            "y_range": axes_ranges[2:],
            'placed_trendline': get_regression_coords(scatter_placed_results, x_axis, y_axis),
            'notplaced_trendline': get_regression_coords(scatter_notplaced_results, x_axis, y_axis)}

if __name__ == "__main__":
    app.run(debug=True)
    