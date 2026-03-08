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

// TODO: Write a function that draws the scatter plot


function draw_scatter(data, svg, scale) {
    svg.selectAll(".dot")
        .data(data)
        .join(
            enter => enter.append("circle")
                .attr("class", "dot")
                .attr("r", 4)
                .attr("cx", d => scale.x(d.AptitudeTestScore))
                .attr("cy", d => scale.y(d.CGPA))
                .attr('opacity', 0.7)
                .style("fill", "#3c7ab0")
                .style("stroke", "none"),
            update => update
                .attr("cx", d => scale.x(d.AptitudeTestScore))
                .attr("cy", d => scale.y(d.CGPA)),
            exit => exit.remove()
        );
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
        'Extracurricular_Activities': document.querySelector('input[name="extrabutton"]:checked').value,
        'Placement_Training': document.querySelector('input[name="placementbutton"]:checked').value
    }
}

function update_facet(value, type){    
    const x_val = document.getElementById("xdropdown").value;
    const y_val = document.getElementById("ydropdown").value;
    const facet = document.getElementById("facet").value;
    // document.getElementById("Country/Region-filter").value = "All";
    // document.getElementById("Region-filter").value = "All";
    // document.getElementById("State/Province-filter").value = "All";

    fetch('/update_facet', {
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify({"x_val": x_val, "y_val": y_val, "facet": facet}),
        cache: 'no-cache',
        headers: new Headers({
            'content-type': 'application/json'
        })
    }).then(async function(response){
        var results = JSON.parse(JSON.stringify((await response.json())))
        // TODO: DRAW THE SCATTER PLOT
    })
}

// TODO: Write a function that removes the old data points and redraws the scatterplot
function update_scatter(data, svg, scale){
    svg.selectAll(".dot").remove();
    draw_scatter(data, svg, scale)
}

function update(scatter_svg, bar_svg, scatter_scale, bar_scale){
    params = get_params()
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
        update_scatter(results['scatter_placed_data'], scatter_placed_svg, scatter_placed_scale)
        update_scatter(results['scatter_notplaced_data'], scatter_notplaced_svg, scatter_notplaced_scale)
    })
}