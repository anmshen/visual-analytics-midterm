const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
let currentX = "AptitudeTestScore";
let currentY = "CGPA";

function draw_svg(container_id, margin, width, height){
    svg = d3.select("#"+container_id)
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .style("background-color", "#dce0e4")
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    return svg
}

function draw_xaxis(plot_name, svg, height, scale, label="x"){
    svg.append("g")
        .attr('class', plot_name + "-xaxis")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(scale).tickSize(5).tickPadding(10));

    svg.append("text")
        .attr("class", "x-label")
        .attr("text-anchor", "middle")
        .attr("x", width / 2)
        .attr("y", height + 40)
        .text(label)
        .style("font-size", "14px")
        .style("font-weight", "bold");
}

function draw_yaxis(plot_name, svg, scale, label="y"){
    svg.append("g")
        .attr('class', plot_name + "-yaxis")
        .call(d3.axisLeft(scale).tickSize(5).tickPadding(10));

    svg.append("text")
        .attr("class", "y-label")
        .attr("text-anchor", "middle")
        .attr("transform", "rotate(-90)")
        .attr("y", -45)
        .attr("x", -height / 2)
        .text(label)
        .style("font-size", "14px")
        .style("font-weight", "bold");
}

function draw_axis(plot_name, axis, svg, height, domain, range, discrete){
    if (discrete){
        var scale = d3.scaleBand()
            .domain(domain)
            .range(range)
            .padding([0.2])
    } else {
        var scale = d3.scaleLinear()
            .domain(domain)
            .range(range);
    }
    if (axis=='x'){
        draw_xaxis(plot_name, svg, height, scale, label=currentX)
    } else if (axis=='y'){
        draw_yaxis(plot_name, svg, scale, label=currentY)
    }
    return scale
}

function draw_axes(plot_name, svg, width, height, domainx, domainy, x_discrete){
    let x_buffer = (domainx[1] - domainx[0]) * 0.1;
    let padded_x = [domainx[0] - x_buffer, domainx[1] + x_buffer];
    let y_buffer = (domainy[1] - domainy[0]) * 0.1;
    let padded_y = [domainy[0] - y_buffer, domainy[1] + y_buffer];

    var x_scale = draw_axis(plot_name, 'x', svg, height, padded_x, [0, width], false)
    var y_scale = draw_axis(plot_name, 'y', svg, height, padded_y, [height, 0], false)
    return {'x': x_scale, 'y': y_scale}
}

function draw_slider(column, min, max, scatter_svg, bar_svg, scatter_scale, bar_scale){
    slider = document.getElementById(column+'-slider')
    noUiSlider.create(slider, {
      start: [min, max],
      connect: false,
          tooltips: true,
      step: 1,
      range: {'min': min, 'max': max}
    });
    slider.noUiSlider.on('change', function(){
        update(scatter_svg, bar_svg, scatter_scale, bar_scale)
    });
}

function calculate_regression(data, x_name, y_name, x_scale, y_scale) {
    const n = data.length;
    if (n < 2) return null;

    const sumX = d3.sum(data, d => d[x_name]);
    const sumY = d3.sum(data, d => d[y_name]);
    const sumXY = d3.sum(data, d => d[x_name] * d[y_name]);
    const sumX2 = d3.sum(data, d => d[x_name] * d[x_name]);

    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;

    const xCoords = data.map(d => d[x_name]);
    const minX = d3.min(xCoords);
    const maxX = d3.max(xCoords);

    return {
        x1: x_scale(minX),
        y1: y_scale(slope * minX + intercept),
        x2: x_scale(maxX),
        y2: y_scale(slope * maxX + intercept)
    };
}

// TODO: Write a function that draws the scatter plot


function draw_scatter(data, svg, scale, x_name=currentX, y_name=currentY) {
    svg.selectAll(".dot")
        .data(data)
        .join(
            enter => enter.append("circle")
                .attr("class", "dot")
                .attr("r", 4)
                .attr("cx", d => scale.x(d[x_name]))
                .attr("cy", d => scale.y(d[y_name]))
                .attr('opacity', 0.7)
                .style("fill", "#3c7ab0")
                .style("stroke", "none"),
            update => update
                .attr("cx", d => scale.x(d[x_name]))
                .attr("cy", d => scale.y(d[y_name])),
            exit => exit.remove()
        );
    
    const lineCoords = calculate_regression(data, x_name, y_name, scale.x, scale.y);
    svg.selectAll(".trendline").remove();

    if (lineCoords) {
        svg.append("line")
            .attr("class", "trendline")
            .attr("x1", lineCoords.x1)
            .attr("y1", lineCoords.y1)
            .attr("x2", lineCoords.x2)
            .attr("y2", lineCoords.y2)
            .style("stroke", "#c03308") 
            .style("stroke-width", 3)
    }
}

// TODO: Write a function that extracts the selected days and minimum/maximum values for each slider
function get_params(){
    return {
        'Internships': document.getElementById('internships-slider').noUiSlider.get().map(Number),
        'Projects': document.getElementById('projects-slider').noUiSlider.get().map(Number),
        'AptitudeTestScore': document.getElementById('aptitude-slider').noUiSlider.get().map(Number),
        'SoftSkillsRating': document.getElementById('soft-slider').noUiSlider.get().map(Number),
        'SSC_Marks': document.getElementById('ssc-marks-slider').noUiSlider.get().map(Number),
        'HSC_Marks': document.getElementById('hsc-marks-slider').noUiSlider.get().map(Number),
        'Extracurricular_Activities': [...document.querySelectorAll('input[name="extrabutton"]:checked')].map(x => x.value),
        'Placement_Training': [...document.querySelectorAll('input[name="placebutton"]:checked')].map(x => x.value),
        'x_axis': document.getElementById("xdropdown").value,
        'y_axis': document.getElementById("ydropdown").value
    }
}

// TODO: Write a function that removes the old data points and redraws the scatterplot
function update_scatter(data, svg, scale){
    // svg.selectAll(".x-axis")
    // draw_axes(plot_name, svg, width, height, domainx, domainy, x_discrete)
    svg.selectAll(".dot").remove();
    draw_scatter(data, svg, scale)

}

function update(scatter_placed_svg, scatter_notplaced_svg, scatter_placed_scale, scatter_notplaced_scale){
    params = get_params()
    currentX = params.x_axis
    currentY = params.y_axis
    // retrieve the x and y axis
    fetch('/update', {
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify(params),
        cache: 'no-cache',
        headers: new Headers({
            'content-type': 'application/json'
        })
    }).then(async function(response){
        var results = JSON.parse(JSON.stringify((await response.json()))) 

        scatter_placed_svg.selectAll(".scatter_placed-xaxis").remove()
        scatter_placed_svg.selectAll(".scatter_placed-yaxis").remove()
        scatter_placed_svg.selectAll(".y-label").remove()
        scatter_placed_svg.selectAll(".x-label").remove()
        
        scatter_notplaced_svg.selectAll(".scatter_notplaced-xaxis").remove()
        scatter_notplaced_svg.selectAll(".scatter_notplaced-yaxis").remove()
        scatter_notplaced_svg.selectAll(".x-label").remove()
        scatter_notplaced_svg.selectAll(".y-label").remove()

        scatter_placed_scale = draw_axes('scatter_placed', scatter_placed_svg, width, height, results.x_range, results.y_range, false)
        scatter_notplaced_scale = draw_axes('scatter_notplaced', scatter_notplaced_svg, width, height, results.x_range, results.y_range, false)

        update_scatter(results['scatter_placed_data'], scatter_placed_svg, scatter_placed_scale)
        update_scatter(results['scatter_notplaced_data'], scatter_notplaced_svg, scatter_notplaced_scale)
    })
}