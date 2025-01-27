var map;
var directionsService;
var directionsRenderer;
var startMarker;
var endMarker;
var waypointMarkers = [];

directionsService = new google.maps.DirectionsService();
function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 6.42375, lng: -66.58973 },
        zoom: 5,
    });

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        map: map,
        suppressMarkers: true,
    });

    var autocompleteStart = new google.maps.places.Autocomplete(
        document.getElementById("id_destination_direc"),
        {
            componentRestrictions: { country: "VE" },
        }
    );

    var autocompleteEnd = new google.maps.places.Autocomplete(
        document.getElementById("id_departure_direc"),
        {
            componentRestrictions: { country: "VE" },
        }
    );

    autocompleteStart.addListener("place_changed", function () {
        var place = autocompleteStart.getPlace();
        if (place.geometry) {
            startMarker.setPosition(place.geometry.location);
            startMarker.setVisible(true);
            $("#id_lat_1").val(place.geometry.location.lat());
            $("#id_long_1").val(place.geometry.location.lng());
            calculateRoute();
        }
    });
    

    autocompleteEnd.addListener("place_changed", function () {
        var place = autocompleteEnd.getPlace();
        if (place.geometry) {
            endMarker.setPosition(place.geometry.location);
            endMarker.setVisible(true);
            $("#id_lat_2").val(place.geometry.location.lat());
            $("#id_long_2").val(place.geometry.location.lng());
            calculateRoute();
            
            handleAddressChange(); // Llama a la función después del autocomplete
        }
    });

    startMarker = new google.maps.Marker({
        position: { lat: 0, lng: 0 },
        map: map,
        icon: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png",
        draggable: true,
    });

    endMarker = new google.maps.Marker({
        position: { lat: 0, lng: 0 },
        map: map,
        icon: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
        draggable: true,
    });

    startMarker.addListener("dragend", function () {
        var position = startMarker.getPosition();
        $("#id_lat_1").val(position.lat());
        $("#id_long_1").val(position.lng());
        calculateRoute();
    });

    endMarker.addListener("dragend", function () {
        var position = endMarker.getPosition();
        $("#id_lat_2").val(position.lat());
        $("#id_long_2").val(position.lng());
        calculateRoute();
    });

    updateMarkers();
    calculateRoute();
    
}

$(document).ready(function() {
    
});

function updateMarkers() {
    var startAddress = document.getElementById("id_destination_direc").value;
    var endAddress = document.getElementById("id_departure_direc").value;

    if (startAddress) {
        geocodeAddress(startAddress, function (latLng) {
            startMarker.setPosition(latLng);
            startMarker.setVisible(true);
            $("#id_lat_1").val(latLng.lat());
            $("#id_long_1").val(latLng.lng());
            calculateRoute();
        });
    } else {
        startMarker.setVisible(false);
    }

    if (endAddress) {
        geocodeAddress(endAddress, function (latLng) {
            endMarker.setPosition(latLng);
            endMarker.setVisible(true);
            $("#id_lat_2").val(latLng.lat());
            $("#id_long_2").val(latLng.lng());
            calculateRoute();
        });
    } else {
        endMarker.setVisible(false);
    }
}

function geocodeAddress(address, callback) {
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({ address: address }, function (results, status) {
        if (status === "OK" && results[0]) {
            callback(results[0].geometry.location);
        }
    });
}

function calculateRoute() {
    var startLat = parseFloat($('#id_lat_1').val());
    var startLng = parseFloat($('#id_long_1').val());
    var endLat = parseFloat($('#id_lat_2').val());
    var endLng = parseFloat($('#id_long_2').val());

    // Verificar que las coordenadas de inicio y fin sean válidas
    if (isNaN(startLat) || isNaN(startLng) || isNaN(endLat) || isNaN(endLng)) {
        console.error('Invalid latitude and longitude');
        return;
    }

    var start = { lat: startLat, lng: startLng };
    var end = { lat: endLat, lng: endLng };
    var waypoints = [];

    var waypointInputs = $('[waypoint="true"]');
    waypointInputs.each(function (index, element) {
        var lat = parseFloat($(`#id_lat_${index + 3}`).val());
        var lng = parseFloat($(`#id_long_${index + 3}`).val());
        if (!isNaN(lat) && !isNaN(lng)) {
            waypoints.push({
                location: { lat: lat, lng: lng },
                stopover: true
            });
        }
    });

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
                var marker = new google.maps.Marker({
                    position: waypoint.location,
                    map: map,
                    icon: 'https://maps.google.com/mapfiles/ms/icons/green-dot.png',
                    title: `Waypoint ${index + 3}`,
                    draggable: true
                });

                marker.addListener('dragend', function () {
                    updateWaypointPosition(index, marker.getPosition());
                    calculateRoute(); // Recalcular la ruta después de mover el waypoint
                });

                waypointMarkers.push(marker);
            });
        } else {
            console.error('Error al calcular la ruta:', status);
        }
    });
}

function updateWaypointPosition(index, position) {
    var waypointInputs = $('[waypoint="true"]');
    var waypointInput = waypointInputs[index];
    var latInput = $(`#id_lat_${index + 3}`);
    var lngInput = $(`#id_long_${index + 3}`);

    geocodeLatLng(position, function (address) {
        waypointInput.value = address;
        latInput.val(position.lat());
        lngInput.val(position.lng());
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

async function handleAddressChange() {
    const departureAddress = $("#id_destination_direc").val();
    const arrivalAddress = $("#id_departure_direc").val();
    const nro = $('#id_person_to_transfer option:selected').length;

    try {
        const departureCity = await getCityFromAddress(departureAddress);
        const arrivalCity = await getCityFromAddress(arrivalAddress);

        console.log(departureCity, arrivalCity);

        $.ajax({
            url: rates_ajax,  // URL de la vista Django
            type: "GET",
            data: {
                departure_city: departureCity,
                arrival_city: arrivalCity,
                nro: nro,
            },
            success: function (data) {
                console.log(data);
                const tarifas = data.rates; // Obtén todas las tarifas de la respuesta

                // Verifica si hay tarifas disponibles
                if (tarifas.length === 0) {
                    $("#rates_div").html(`
                        <div class="mt-5 col-md-12">
                            <label class="btn btn-outline btn-outline-dashed btn-outline-default p-7 d-flex align-items-center mb-5">
                                <span class="d-block fw-bold text-start">
                                    <span class="text-dark fw-bolder d-block fs-3">
                                        No hemos encontrado tarifa para tu ruta, para una ruta personalizada por favor contáctanos.
                                    </span>
                                </span>
                            </label>
                        </div>
                    `).removeClass('d-none');
                    return;
                }

                // Itera sobre las tarifas y genera el HTML para cada una
                let tarifasHtml = "";
                tarifas.forEach((tarifa, index) => {
                    tarifasHtml += `
                        <div class="mt-5 col-md-6">
                            <label class="btn btn-outline btn-outline-dashed btn-outline-default p-7 d-flex align-items-center mb-5" for="">
                                <svg class="svg-icon svg-icon-4x me-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512" width="60" height="60" >
                                    <path d="M312 24V34.5c6.4 1.2 12.6 2.7 18.2 4.2c12.8 3.4 20.4 16.6 17 29.4s-16.6 20.4-29.4 17c-10.9-2.9-21.1-4.9-30.2-5c-7.3-.1-14.7 1.7-19.4 4.4c-2.1 1.3-3.1 2.4-3.5 3c-.3 .5-.7 1.2-.7 2.8c0 .3 0 .5 0 .6c.2 .2 .9 1.2 3.3 2.6c5.8 3.5 14.4 6.2 27.4 10.1l.9 .3c11.1 3.3 25.9 7.8 37.9 15.3c13.7 8.6 26.1 22.9 26.4 44.9c.3 22.5-11.4 38.9-26.7 48.5c-6.7 4.1-13.9 7-21.3 8.8V232c0 13.3-10.7 24-24 24s-24-10.7-24-24V220.6c-9.5-2.3-18.2-5.3-25.6-7.8c-2.1-.7-4.1-1.4-6-2c-12.6-4.2-19.4-17.8-15.2-30.4s17.8-19.4 30.4-15.2c2.6 .9 5 1.7 7.3 2.5c13.6 4.6 23.4 7.9 33.9 8.3c8 .3 15.1-1.6 19.2-4.1c1.9-1.2 2.8-2.2 3.2-2.9c.4-.6 .9-1.8 .8-4.1l0-.2c0-1 0-2.1-4-4.6c-5.7-3.6-14.3-6.4-27.1-10.3l-1.9-.6c-10.8-3.2-25-7.5-36.4-14.4c-13.5-8.1-26.5-22-26.6-44.1c-.1-22.9 12.9-38.6 27.7-47.4c6.4-3.8 13.3-6.4 20.2-8.2V24c0-13.3 10.7-24 24-24s24 10.7 24 24zM568.2 336.3c13.1 17.8 9.3 42.8-8.5 55.9L433.1 485.5c-23.4 17.2-51.6 26.5-80.7 26.5H192 32c-17.7 0-32-14.3-32-32V416c0-17.7 14.3-32 32-32H68.8l44.9-36c22.7-18.2 50.9-28 80-28H272h16 64c17.7 0 32 14.3 32 32s-14.3 32-32 32H288 272c-8.8 0-16 7.2-16 16s7.2 16 16 16H392.6l119.7-88.2c17.8-13.1 42.8-9.3 55.9 8.5zM193.6 384l0 0-.9 0c.3 0 .6 0 .9 0z"/>
                                </svg>
                                <span class="d-block fw-bold text-start">
                                    <span class="text-dark fw-bolder d-block fs-3">
                                        <input type="radio" class="form-check-input rate-radio" name="rate-checkbox" value="${tarifa.rate_price}" data-rate-id="${tarifa.rate_id}" data-round-trip-price="${tarifa.rate_price_round_trip}"  data-detour-local="${tarifa.rate_detour_local}" required/> Tarifa ${tarifa.rate_id}: ${tarifa.rate_vehicle}
                                    </span>
                                    <span class="text-dark">${tarifa.rate_route}</span> <br>
                                    <span class="text-dark">Tipo de Vehiculo: ${tarifa.rate_vehicle}</span><br>
                                    <span class="text-dark">Precio Base: </span> <span style="color:green">${tarifa.rate_price}$</span><br>
                                    <span class="text-dark">Precio Base Ida y vuelta: </span> <span style="color:green">${tarifa.rate_price_round_trip}$</span><br>
                                    <span class="text-dark">Precio de espera por hora (diurna) C/U: </span> <span style="color:green">${tarifa.rate_daytime_waiting_time}$<br>
                                    <span class="text-dark">Precio de espera por hora (noctura) C/U: </span> <span style="color:green">${tarifa.rate_nightly_waiting_time}$</span><br>
                                    <span class="text-dark">Precio por desvio local C/U: </span> <span style="color:green">${tarifa.rate_detour_local}$</span><br>
                                </br>
                            </label>
                        </div>
                    `;
                });

                // Inserta el HTML generado en el elemento con ID rates_div
                $("#rates_div").html(tarifasHtml).removeClass('d-none');

                // Añadir evento para actualizar el precio con la tarifa seleccionada
                $(".rate-radio").change(function () {
                    var rateId = $("input[name='rate-checkbox']:checked").data('rate-id');
                    $("#id_rate").val(rateId);
                    updatePrice();
                    updateSelectRate($(this).data("rate-id"));
                });

                // Añadir evento para actualizar el precio cuando se cambia el checkbox de ida y vuelta
                $("#id_is_round_trip").change(function () {
                    updatePrice();
                });

                // Función para actualizar el precio
                function updatePrice() {
                    const selectedRate = $("input[name='rate-checkbox']:checked");
                    if (selectedRate.length > 0) {
                        const selectedPrice = selectedRate.val();
                        const roundTripPrice = selectedRate.data("round-trip-price");
                        const isRoundTrip = $("#id_is_round_trip").is(":checked");

                        if (isRoundTrip) {
                            $("#id_price").val(roundTripPrice);
                            $("#id_final_price").val(roundTripPrice);
                            AditionalDetour();
                        } else {
                            $("#id_price").val(selectedPrice);
                            $("#id_final_price").val(selectedPrice);
                            AditionalDetour();
                        }

                        // Si hay un descuento válido, actualizar el precio con descuento
                        const discountValue = $('#discount_message span.text-success').text().match(/(\d+)%/);
                        if (discountValue) {
                            const discount = parseFloat(discountValue[1]) / 100;
                            const discountedPrice = isRoundTrip ? roundTripPrice * (1 - discount) : selectedPrice * (1 - discount);
                            $("#id_discounted_price").val(discountedPrice.toFixed(2));
                            $("#id_final_price").val(discountedPrice.toFixed(2));
                            AditionalDetour();
                        }
                    }
                }

                // Función para actualizar el campo select con la tarifa seleccionada
                function updateSelectRate(rateId) {
                    $("#id_rate").val(rateId);
                }
            },
            error: function () {
                // Maneja el error si no se encuentra una tarifa
                $("#rates_div").html(`
                    <div class="mt-5 col-md-6">
                        <label class="btn btn-outline btn-outline-dashed btn-outline-default p-7 d-flex align-items-center mb-5">
                            <span class="d-block fw-bold text-start">
                                <span class="text-dark fw-bolder d-block fs-3">
                                    No hemos encontrado tarifa para tu ruta, para una ruta personalizada por favor contáctanos.
                                </span>
                            </span>
                        </label>
                    </div>
                `).removeClass('d-none');
            }
        });
    } catch (error) {
        console.error("Error al obtener la ciudad de la dirección:", error);
    }
}

async function getCityFromAddress(address) {
    var city = "";
    var geocoder = new google.maps.Geocoder();
    return new Promise((resolve, reject) => {
        geocoder.geocode({ 'address': address }, function (results, status) {
            if (status === 'OK' && results[0]) {
                var addressComponents = results[0].address_components;
                for (var i = 0; i < addressComponents.length; i++) {
                    if (addressComponents[i].types.includes("locality")) {
                        city = addressComponents[i].long_name;
                        break;
                    }
                }
                // Si no se encuentra la ciudad, intenta obtener el estado
                if (!city) {
                    for (var i = 0; i < addressComponents.length; i++) {
                        if (addressComponents[i].types.includes("administrative_area_level_1")) {
                            city = addressComponents[i].long_name;
                            break;
                        }
                    }
                }
                resolve(city);
            } else {
                reject(status);
            }
        });
    });
}