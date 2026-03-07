import duckdb
from flask import Flask, render_template, request

app = Flask(__name__)
continuous_columns = ['Internships', 'Projects', 'AptitudeTestScore', 'SoftSkillsRating', 'SSC_Marks', 'HSC_Marks']
discrete_columns = ['ExtracurricularActivities, PlacementTraining']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
days = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
sorted_months = sorted(months)

@app.route('/')
def index():
    scatter_ranges_query = f'SELECT MIN(AptitudeTestScore), MAX(AptitudeTestScore), MIN(CGPA), MAX(CGPA) FROM placementdata.csv' # Retrieves the minimum and maximum X and Y coordinates
    scatter_ranges_results = duckdb.sql(scatter_ranges_query).df() 
    scatter_ranges = scatter_ranges_results.iloc[0].to_list()
      
    #TODO remove max count
    max_count_query = '''
        SELECT MAX(month_count) 
        FROM (
            SELECT COUNT(*) AS month_count 
            FROM 'forestfires.csv' 
            GROUP BY month
        ) AS maxFFCount
    ''' # TODO: Write a query that retrieves the maximum number of forest fires that occurred in a single month
    max_count_results = duckdb.sql(max_count_query).df()
    max_count = int(max_count_results.iloc[0, 0]) # TODO: Extract the maximum count from the query results

    # TODO: write a query that retrieves the the minimum and maximum value for each slider
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
    
    filter_ranges = {'internships': filter_internship_ranges.iloc[0].to_list(), 
                     'projects': filter_projects_ranges.iloc[0].to_list(), 
                     'aptitude': filter_aptitude_ranges.iloc[0].to_list(),
                     'soft': filter_softskills_ranges.iloc[0].to_list(),
                     'ssc-marks': filter_ssc_ranges.iloc[0].to_list(),
                     'hsc-marks': filter_hsc_ranges.iloc[0].to_list()} 
    
    return render_template(
        'index.html', months=months, days=days,
        filter_ranges=filter_ranges, scatter_ranges=scatter_ranges, max_count=0
    )

@app.route('/update', methods=["POST"])
def update():
    request_data = request.get_json()
    print(request_data)
    
    continuous_predicate = ' AND '.join([f'({column} >= {request_data[column][0]} AND {column} <= {request_data[column][1]})' for column in continuous_columns]) # TODO: update where clause from sliders
    # days_list = "', '".join(request_data['day'])
    # discrete_predicate = f"day IN ('{days_list}')"
    # discrete_predicate = ' AND '.join([f'{column} IN ({days})' for column in discrete_columns]) # TODO: update where clause from checkboxes
    # predicate = ' AND '.join([continuous_predicate, discrete_predicate]) # Combine where clause from sliders and checkboxes
    # predicate = ' AND '.join([continuous_predicate]) # Combine where clause from sliders and checkboxes
    placed_predicate = ' AND '.join([continuous_predicate, "PlacementStatus == True"])
    notplaced_predicate = ' AND '.join([continuous_predicate, "PlacementStatus == False"])

    scatter_placed_query = f'SELECT AptitudeTestScore, CGPA FROM placementdata.csv WHERE {placed_predicate}'
    scatter_placed_results = duckdb.sql(scatter_placed_query).df()
    scatter_placed_data = scatter_placed_results.to_dict(orient='records') 

    scatter_notplaced_query = f'SELECT AptitudeTestScore, CGPA FROM placementdata.csv WHERE {notplaced_predicate}'
    scatter_notplaced_results = duckdb.sql(scatter_notplaced_query).df()
    scatter_notplaced_data = scatter_notplaced_results.to_dict(orient='records') 
    
    return {'scatter_placed_data': scatter_placed_data, 'scatter_notplaced_data': scatter_notplaced_data}

if __name__ == "__main__":
    app.run(debug=True)
    