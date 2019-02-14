// Add a feature to the geojson file: number of publications per country
function getPublications(geoJSON) {
  for (var i = 0; i < geoJSON.features.length; i++) {
    var country_i = geoJSON.features[i].properties.ISO_A3;
    if (country_i in countByCountry) {
      geoJSON.features[i].properties.PUBLICATIONS = countByCountry[country_i];
    } else {
      geoJSON.features[i].properties.PUBLICATIONS = 0;
    }
  }
}
getPublications(admin_0);

/*
Choropleth map: number of publications per country, based on the example at
leafletjs.com
*/

// Blank map without tiles
var map = L.map('map').setView([20, 30], 1);

// The geojson var must be defined before the event listener.
var geojson;

// Event listener
function highlightFeature(e) {
    var layer = e.target;
    layer.setStyle({
        fillColor: '#7f7f7f'
    });
    map_info.update(layer.feature.properties);
}

function resetHighlight(e) {
    geojson.resetStyle(e.target);
    map_info.update();
}

function getPublicationsByCountry(e) {
    var layer = e.target;
    location.href = path + layer.feature.properties.ISO_A3 + '/';
}

function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        click: getPublicationsByCountry
    });
}


// Custom controls
var map_info = L.control();

// Create a div with the class "map_info"
map_info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'map_info');
    this.update();
    return this._div;
};
// Function for updating map_info with feature properties
map_info.update = function (properties) {
    this._div.innerHTML = (properties ? properties.ADMIN + '<br />'
        + properties.PUBLICATIONS + ' publications' : 'Hover over a country<br />'
        + '(click to see publications)');
};
map_info.addTo(map);


// Geojson
// Color gradient for choropleth
function getColor(n) {
    return n > 50  ? '#b30000' :
           n > 40  ? '#e34a33' :
           n > 30  ? '#fc8d59' :
           n > 20  ? '#fdbb84' :
           n > 10  ? '#fdd49e' :
           n > 0   ? '#fef0d9' :
                     '#E0E0E0' ;
}
function style(feature) {
    return {
        fillColor: getColor(feature.properties.PUBLICATIONS),
        weight: 1,
        opacity: 1,
        color: 'white',
        fillOpacity: 1
    };
}


// GeoJSON: world countries from Natural Earth
geojson = L.geoJson(admin_0, {
    style: style,
    onEachFeature: onEachFeature
});
geojson.getAttribution = function() { return '<a href="https://www.naturalearthdata.com">Natural Earth</a>'; };
geojson.addTo(map);


// Map legend
var legend = L.control({position: 'bottomright'});
legend.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'map_info map_legend'),
        grades = [0, 10, 20, 30, 40, 50],  // Breaks in the color gradient from getColor()
        labels = [];
    for (var i = 0; i < grades.length; i++) {
        div.innerHTML +=
            '<i style="background:' + getColor(grades[i] + 1) + '"></i> ' +  // Get the color for each grade in the gradient
            (grades[i + 1] ? '&#8804; ' + grades[i + 1] + '<br>' : '> ' + grades[i]);  // Get the text for each grade (e.g., "> 50")
    }
    return div;
};
legend.addTo(map);
