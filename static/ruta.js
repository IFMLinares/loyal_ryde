var map;
var directionsService;
var directionsRenderer;
var startMarker;
var endMarker;

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 6.42375, lng: -66.58973 },
        zoom: 5,
    });

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({ map: map });

    var autocompleteStart = new google.maps.places.Autocomplete(document.getElementById('id_destination_direc'));
    var autocompleteEnd = new google.maps.places.Autocomplete(document.getElementById('id_departure_direc'));

    autocompleteStart.addListener('place_changed', function () {
        calculateRoute();
        updateMarkers();
    });

    autocompleteEnd.addListener('place_changed', function () {
        calculateRoute();
        updateMarkers();
    });

    // Crear marcadores arrastrables
    startMarker = new google.maps.Marker({
        position: { lat: 0, lng: 0 }, // Posición de inicio (placeholder)
        map: map,
        icon: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
        draggable: true, // Habilita la opción de arrastrar
    });

    endMarker = new google.maps.Marker({
        position: { lat: 0, lng: 0 }, // Posición de fin (placeholder)
        map: map,
        icon: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
        draggable: true, // Habilita la opción de arrastrar
    });

    // Escuchar eventos de arrastre
    startMarker.addListener('dragend', function () {
        updateMarkers();
        calculateRoute();
    });

    endMarker.addListener('dragend', function () {
        updateMarkers();
        calculateRoute();
    });
}

function updateMarkers() {
    var startAddress = document.getElementById('id_destination_direc').value;
    var endAddress = document.getElementById('id_departure_direc').value;

    // Actualizar la posición de los marcadores según las direcciones ingresadas
    if (startAddress) {
        geocodeAddress(startAddress, function (latLng) {
            startMarker.setPosition(latLng);
            startMarker.setVisible(true); // Mostrar el marcador de inicio
            calculateRoute();
        });
    } else {
        startMarker.setVisible(false); // Ocultar el marcador de inicio si no hay dirección
    }

    if (endAddress) {
        geocodeAddress(endAddress, function (latLng) {
            endMarker.setPosition(latLng);
            endMarker.setVisible(true); // Mostrar el marcador de fin
            calculateRoute();
        });
    } else {
        endMarker.setVisible(false); // Ocultar el marcador de fin si no hay dirección
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