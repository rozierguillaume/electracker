<img id="jpg-export"></img>

var d3 = require("d3");
var img_jpg= d3.select('#jpg-export');

// Plotting the Graph

var trace={x:[3,9,8,10,4,6,5],y:[5,7,6,7,8,9,8],type:"scatter"};
var trace1={x:[3,4,1,6,8,9,5],y:[4,2,5,2,1,7,3],type:"scatter"};
var data = [trace,trace1];
var layout = {title : "Simple JavaScript Graph"};
Plotly.newPlot(
  'plotly_div',
   data,
   layout)

// static image in jpg format

.then(
    function(gd)
     {
      Plotly.toImage(gd,{height:300,width:300})
         .then(
             function(url)
         {
             img_jpg.attr("src", url);
         }
         )
    });


