var map;
var directionsService;
var directionsRenderer;
var startMarker;
var endMarker;
directionsService = new google.maps.DirectionsService();
function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 6.42375, lng: -66.58973 },
        zoom: 5,
    });

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({ map: map });

    var autocompleteStart = new google.maps.places.Autocomplete(document.getElementById('id_destination_direc'), {
        componentRestrictions: { country: 'VE' }
    });
    
    var autocompleteEnd = new google.maps.places.Autocomplete(document.getElementById('id_departure_direc'), {
        componentRestrictions: { country: 'VE' }
    });

    autocompleteStart.addListener('place_changed', function () {
        calculateRoute();
        updateMarkers();
    });

    autocompleteEnd.addListener('place_changed', function () {
        calculateRoute();
        updateMarkers();
    });
    startMarker = new google.maps.Marker({
        position: { lat: 0, lng: 0 },
        map: map,
        icon: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
        draggable: true,
    });

    endMarker = new google.maps.Marker({
        position: { lat: 0, lng: 0 },
        icon: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
        draggable: true,
    });

    startMarker.addListener('dragend', function () {
        updateMarkers();
        calculateRoute();
    });

    endMarker.addListener('dragend', function () {
        updateMarkers();
        calculateRoute();
    });
    
    updateMarkers();
    calculateRoute();
}
function updateMarkers() {
    var startAddress = document.getElementById('id_destination_direc').value;
    var endAddress = document.getElementById('id_departure_direc').value;

    if (startAddress) {
        geocodeAddress(startAddress, function (latLng) {
            startMarker.setPosition(latLng);
            startMarker.setVisible(true);
            calculateRoute();
            console.log('Latitud de inicio:', latLng.lat());
            console.log('Longitud de inicio:', latLng.lng());
            $('#id_lat_1').val(latLng.lat())
            $('#id_long_1').val(latLng.lng())
            
            
        });
    } else {
        startMarker.setVisible(false);
    }

    if (endAddress) {
        geocodeAddress(endAddress, function (latLng) {
            endMarker.setPosition(latLng);
            endMarker.setVisible(true);
            calculateRoute();
            console.log('Latitud de destino:', latLng.lat());
            console.log('Longitud de destino:', latLng.lng());
            $('#id_lat_2').val(latLng.lat())
            $('#id_long_2').val(latLng.lng())
        });
    } else {
        endMarker.setVisible(false);
    }
}
function geocodeAddress(address, callback) {
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({ address: address }, function (results, status) {
        if (status === 'OK' && results[0]) {
            callback(results[0].geometry.location);
        }
    });
}
function calculateRoute() {
    var start = document.getElementById('id_destination_direc').value;
    var end = document.getElementById('id_departure_direc').value;
    console.log(start)
    console.log(end)

    if (start && end) {
        var request = {
            origin: start,
            destination: end,
            travelMode: 'DRIVING',
        };

        directionsService.route(request, function (result, status) {
            if (status === 'OK') {
                directionsRenderer.setDirections(result);
            }
        });
    } else {
        directionsRenderer.set('directions', null);
    }
}