var platform = new H.service.Platform({
    'apikey': 'wTlHrZB0LowCHxVr9C2swXDxBZXdi_QplnpCz6uh8dw'
    });
// Obtain the default map types from the platform object:
var defaultLayers = platform.createDefaultLayers();

// Instantiate (and display) a map object:
var map = new H.Map(
    document.getElementById('mapContainer'),
    defaultLayers.vector.normal.map,
    {
    zoom: 11.5,
    center: { lat: -3.738, lng: -38.5458 }
    });
var provider = map.getBaseLayer().getProvider();

var service = platform.getSearchService();

// Call the geocode method with the geocoding parameters,
// the callback and an error callback function (called if a
// communication error occurs):

// var geocoder = platform.getGeocodingService();
// var geocodingParams = {
//   searchText: '255 Avenida Doutor Mendel Steinbruch, Fortaleza, Ceará, Brazil'
// };

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

service.geocode({
  q: '255 Avenida Doutor Mendel Steinbruch, Fortaleza, Ceará, Brazil'
}, (result) => {
  // Add a marker for each location found
  result.items.forEach((item) => {
    map.addObject(new H.map.Marker(item.position));
  });
}, alert);

// Create the parameters for the routing request:
// var routingParameters = {
//     'routingMode': 'fast',
//     'transportMode': 'car',
//     // The start point of the route:
//     'origin': '-3.709,-38.53',
//     // The end point of the route:
//     'destination': '-3.715,-38.54',
//     // Include the route shape in the response
//     'return': 'polyline'
//   };
  

