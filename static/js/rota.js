var platform = new H.service.Platform({
    'apikey': ''
    });
// Obtain the default map types from the platform object:
var defaultLayers = platform.createDefaultLayers();

// Instantiate (and display) a map object:
var map = new H.Map(
    document.getElementById('mapContainer'),
    defaultLayers.vector.normal.map,
    {
    zoom: 11.5,
    // center: { lat: -3.738, lng: -38.5458 }
    center: { lat: -3.80315445, lng: -38.572173 }
    // −
    });
var provider = map.getBaseLayer().getProvider();

var service = platform.getSearchService();


// Define a callback function to process the geocoding response
var onResult = function(result) {
  var locations = result.Response.View[0].Result, position, marker;

  // Add a marker for each location found
  for (var i=0; i < locations.lenght; i++) {
    position = {
      lat: locations[i].Location.DisplayPosition.Latitude,
      lng: locations[i].Location.DisplayPosition.Longitude
    };
    map.setCenter(position);
    map.setZoom(14);
    marker = new H.map.Marker(position);
    map.addObject(marker);
  }
}

var routingParameters = {
    'routingMode': 'fast',
    'transportMode': 'car',
    // The start point of the route:
    'origin': '-3.8269357,-38.5797751',
    // The end point of the route:
    'destination': '-3.7793732,-38.5645709',
    // Include the route shape in the response
    'return': 'polyline'
  };
  
// Define a callback function to process the routing response:
var onResult = function(result) {
// ensure that at least one route was found
if (result.routes.length) {
    result.routes[0].sections.forEach((section) => {
        // Create a linestring to use as a point source for the route line
        let linestring = H.geo.LineString.fromFlexiblePolyline(section.polyline);

        // Create a polyline to display the route:
        let routeLine = new H.map.Polyline(linestring, {
        style: { strokeColor: 'blue', lineWidth: 3 }
        });

        // Create a marker for the start point:
        let startMarker = new H.map.Marker(section.departure.place.location);

        // Create a marker for the end point:
        let endMarker = new H.map.Marker(section.arrival.place.location);

        // Add the route polyline and the two markers to the map:
        map.addObjects([routeLine, startMarker, endMarker]);

        // Set the map's viewport to make the whole route visible:
        map.getViewModel().setLookAtData({bounds: routeLine.getBoundingBox()});
    });
}
};

// // Get an instance of the routing service version 8:
var router = platform.getRoutingService(null, 8);

// Call calculateRoute() with the routing parameters,
// the callback and an error callback function (called if a
// communication error occurs):
router.calculateRoute(routingParameters, onResult,
function(error) {
    alert(error.message);
});


