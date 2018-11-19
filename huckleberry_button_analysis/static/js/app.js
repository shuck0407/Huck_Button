
// Function that changes event when a new sample is selected 
// (i.e. fetch data for the newly selected sample)
function bbChanged(newbb) {

    // Define the Flask routes that need to happen for a change in button
    var bbURL = `/samples/${newbb}`;

    // Fetch the JSON data for the new sample and console log it       
    d3.json(bbURL, function(error, response) {
        if(error) {return console.warn(error);}
        console.log(response);  
        

        //First update the metadata table
        var metadata = response['meta'];
        console.log(metadata);
        // Select the table with id of `#sample-metadata` using d3
              var table = d3.select("#sample-metadata");
          
              // Use `.html("") to clear any existing metadata
              table.html("");
          
              // Use `Object.entries` to add each key and value pair to the panel
              
              Object.entries(metadata).forEach(([key, value]) => {
                table.append("h6").text(`${key}: ${value}`);
              });
        
                 
        // Grab values from the response json object to build the pie chart
        var pie_response = response['pie'];
        var data = [pie_response];
        console.log(data);
        var layout = {title: '<b>Top 10 Bacteria Found in Belly Button</b>'};
        var pie_chart_div = document.querySelector(".bb-pie");

        Plotly.newPlot(pie_chart_div, data, layout);

        // Grab values from the response json object to build the bubble chart
        var bubble_response = response['bubble'];
        var bubble_data = bubble_response['data'];
        var bubble_layout = bubble_response['layout']
        
        console.log(bubble_response, bubble_data, bubble_layout);
        
        var bubble_chart_div = document.querySelector(".bb-bubble");

        Plotly.newPlot(bubble_chart_div, bubble_data, bubble_layout);

       
    });
};

function init() {
      // create a URL variable for the buttons Flask route
      var buttonURL = '/buttons';
      
      //Use d3 to populate the dropdown list of belly buttons
      d3.json(buttonURL, function(error, response) {
          if (error) {
              return console.warn(error);
          };
      
          var firstSample = response[0];
          console.log(firstSample);

          var buttons = d3.select('#selDataset')
          response.forEach((metavalue) => {
              buttons.append('option')
                     .text(metavalue) 
                     .property('value', metavalue);
             });
          
      
          d3.select('#selDataset').on('change', function() {
              var newbb = this.options[this.selectedIndex].value;
              bbChanged(newbb);
              });


        // Use the first sample from the list to build the initial plots
        bbChanged(firstSample);

        });

    
};

init();

