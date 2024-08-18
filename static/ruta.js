var map;
var directionsService;
var directionsRenderer;
var startMarker;
var endMarker;
var waypointMarkers = [];

directionsService = new google.maps.DirectionsService();

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 6.42375, lng: -66.58973 },
        zoom: 5,
    });

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({ map: map, suppressMarkers: true });

    var autocompleteStart = new google.maps.places.Autocomplete(document.getElementById('id_destination_direc'), {
        componentRestrictions: { country: 'VE' }
    });

    var autocompleteEnd = new google.maps.places.Autocomplete(document.getElementById('id_departure_direc'), {
        componentRestrictions: { country: 'VE' }
    });

    autocompleteStart.addListener('place_changed', function () {
        var place = autocompleteStart.getPlace();
        if (place.geometry) {
            startMarker.setPosition(place.geometry.location);
            startMarker.setVisible(true);
            $('#id_lat_1').val(place.geometry.location.lat());
            $('#id_long_1').val(place.geometry.location.lng());
            calculateRoute();
        }
    });

    autocompleteEnd.addListener('place_changed', function () {
        var place = autocompleteEnd.getPlace();
        if (place.geometry) {
            endMarker.setPosition(place.geometry.location);
            endMarker.setVisible(true);
            $('#id_lat_2').val(place.geometry.location.lat());
            $('#id_long_2').val(place.geometry.location.lng());
            calculateRoute();
        }
    });

    startMarker = new google.maps.Marker({
        position: { lat: 0, lng: 0 },
        map: map,
        icon: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
        draggable: true,
    });

    endMarker = new google.maps.Marker({
        position: { lat: 0, lng: 0 },
        map: map,
        icon: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
        draggable: true,
    });

    startMarker.addListener('dragend', function () {
        var position = startMarker.getPosition();
        $('#id_lat_1').val(position.lat());
        $('#id_long_1').val(position.lng());
        calculateRoute();
    });

    endMarker.addListener('dragend', function () {
        var position = endMarker.getPosition();
        $('#id_lat_2').val(position.lat());
        $('#id_long_2').val(position.lng());
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
            $('#id_lat_1').val(latLng.lat());
            $('#id_long_1').val(latLng.lng());
            calculateRoute();
        });
    } else {
        startMarker.setVisible(false);
    }

    if (endAddress) {
        geocodeAddress(endAddress, function (latLng) {
            endMarker.setPosition(latLng);
            endMarker.setVisible(true);
            $('#id_lat_2').val(latLng.lat());
            $('#id_long_2').val(latLng.lng());
            calculateRoute();
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
    var start = { lat: parseFloat($('#id_lat_1').val()), lng: parseFloat($('#id_long_1').val()) };
    var end = { lat: parseFloat($('#id_lat_2').val()), lng: parseFloat($('#id_long_2').val()) };
    var waypoints = [];

    var waypointInputs = document.getElementsByName('waypoint');
    for (var i = 0; i < waypointInputs.length; i++) {
        if (waypointInputs[i].value) {
            waypoints.push({
                location: waypointInputs[i].value,
                stopover: true
            });
        }
    }

    if (start && end) {
        directionsService.route({
            origin: start,
            destination: end,
            waypoints: waypoints,
            travelMode: google.maps.TravelMode.DRIVING,
        }, function (response, status) {
            if (status === google.maps.DirectionsStatus.OK) {
                directionsRenderer.setDirections(response);
                // Limpiar marcadores de waypoints anteriores
                waypointMarkers.forEach(marker => marker.setMap(null));
                waypointMarkers = [];

                // Agregar nuevos marcadores de waypoints
                waypoints.forEach((waypoint, index) => {
                    geocodeAddress(waypoint.location, function (latLng) {
                        var marker = new google.maps.Marker({
                            position: latLng,
                            map: map,
                            icon: 'https://maps.google.com/mapfiles/ms/icons/green-dot.png',
                            title: `Waypoint ${index + 1}`,
                            draggable: true
                        });

                        marker.addListener('dragend', function () {
                            updateWaypointPosition(index, marker.getPosition());
                            calculateRoute(); // Recalcular la ruta después de mover el waypoint
                        });

                        waypointMarkers.push(marker);
                    });
                });
            } else {
                console.error('Error al calcular la ruta:', status);
            }
        });
    } else {
        directionsRenderer.set('directions', null);
    }
}

function updateWaypointPosition(index, position) {
    var waypointInputs = document.getElementsByName('waypoint');
    var waypointInput = waypointInputs[index];
    var latInput = document.getElementById(`id_lat_${index + 3}`);
    var lngInput = document.getElementById(`id_long_${index + 3}`);

    geocodeLatLng(position, function (address) {
        waypointInput.value = address;
        latInput.value = position.lat();
        lngInput.value = position.lng();
    });
}

function geocodeLatLng(latLng, callback) {
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({ location: latLng }, function (results, status) {
        if (status === 'OK' && results[0]) {
            callback(results[0].formatted_address);
        }
    });
}
