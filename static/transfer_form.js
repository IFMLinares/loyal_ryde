$(document).ready(function () {
	$("#id_date").daterangepicker({
		singleDatePicker: true,
		showDropdowns: true,
		minYear: 1901,
		maxYear: parseInt(moment().format("DD/MM/YYYY"), 10),
	});
	$("#id_in_town").change(function () {
		if ($(this).prop("checked")) {
			$("#id_outside_town").prop("checked", false);
		}
	});

	$("#id_outside_town").change(function () {
		if ($(this).prop("checked")) {
			$("#id_in_town").prop("checked", false);
		}
	});

	$("#people-transfer-form").on("click", function (e) {
		e.preventDefault();
		var name = $("#name").val();
		var phone = $("#phone").val();
		var company = $("#company").val();
		// Validación de campos
		if (!name || !phone) {
			if (!name) {
				$("#name").css("border-color", "red");
			}
			if (!phone) {
				$("#phone").css("border-color", "red");
			}
			return;
		}
		if (!company) {
			company = "N/A";
		}

		$.ajax({
			url: url_form,
			method: "POST",
			data: {
				name: name,
				phone: phone,
				company: company,
			},
			success: function (response) {
				// console.log(response.people_transfer);

				$("#name").val("");
				$("#phone").val("");
				$("#company").val("");
				var people = JSON.parse(response.people_transfer);
				people.forEach(function (person) {
					var option = new Option(
						person.fields.name,
						person.pk,
						true,
						true
					);
					$("#id_person_to_transfer")
						.append(option)
						.trigger("change");
				});
			},
		});
	});

	// Evento input para quitar el borde rojo cuando se llena el campo
	$("#name, #phone").on("input", function () {
		$(this).css("border-color", "");
	});

	$("#id_in_town").change(function () {
		if (this.checked) {
			// Si el checkbox está seleccionado, quitamos la clase 'd-none' del div
			$("#local_traslade").removeClass("d-none");
		} else {
			// Si el checkbox no está seleccionado, agregamos la clase 'd-none' al div
			$("#local_traslade").addClass("d-none");
		}
	});
	$("#id_outside_town").change(function () {
		if (this.checked) {
			// Si el checkbox está seleccionado, quitamos la clase 'd-none' del div
			$("#local_traslade").addClass("d-none");
		} else {
		}
	});

	$("#id_executive_transfer").change(function () {
		if (this.checked) {
			// Si el checkbox está seleccionado, quitamos la clase 'd-none' del div
			$("#localidad").removeClass("d-none");
		} else {
			// Si el checkbox no está seleccionado, agregamos la clase 'd-none' al div
			$("#localidad").addClass("d-none");
		}
	});
	$("#id_driver").change(function () {
		if (this.checked) {
			$("#id_executive_transfer").prop("checked", false);
			$("#id_encomienda").prop("checked", false);
			$("#id_executive_transfer").prop("disabled", true);
			$("#id_encomienda").prop("disabled", true);
		} else {
			$("#id_executive_transfer").prop("disabled", false);
			$("#id_encomienda").prop("disabled", false);
		}
	});

	// $('#id_route_init').on('change', function(){
	// 	console.log('asdasd')
	// })

	$("#id_fly_checkbox").change(function () {
		if (this.checked) {
			// Si el checkbox está seleccionado, quitamos la clase 'd-none' del div
			$("#fly_div").removeClass("d-none");
		} else {
			// Si el checkbox no está seleccionado, agregamos la clase 'd-none' al div
			$("#fly_div").addClass("d-none");
		}
	});

	$("#id_payment_method").change(function () {
		if ($(this).val() == "1") {
			// Si el valor seleccionado es "1", quitamos la clase 'd-none' del div
			$("#data_required").removeClass("d-none");
		} else {
			// Si el valor seleccionado es cualquier otro, agregamos la clase 'd-none' al div
			$("#data_required").addClass("d-none");
		}
	});

	const $idInTownCheckbox = $("#id_in_town");
	const $idOutsideTownCheckbox = $("#id_outside_town");
	const $idFullDayCheckbox = $("#id_full_day");
	const $idHalfDayCheckbox = $("#id_half_day");

	// Función para habilitar/deshabilitar los checkboxes
	function updateCheckboxes() {
		if ($idInTownCheckbox.is(":checked")) {
			$idFullDayCheckbox.prop("disabled", false);
			$idHalfDayCheckbox.prop("disabled", false);
		} else {
			$idFullDayCheckbox.prop("disabled", true);
			$idHalfDayCheckbox.prop("disabled", true);
		}

		if ($idOutsideTownCheckbox.is(":checked")) {
			$idFullDayCheckbox.prop("disabled", true);
			$idHalfDayCheckbox.prop("disabled", true);
		}

		// Verificamos si ambos checkboxes están seleccionados
		if (
			$idFullDayCheckbox.is(":checked") &&
			$idHalfDayCheckbox.is(":checked")
		) {
			// Si ambos están seleccionados, deseleccionamos uno de ellos
			$idFullDayCheckbox.prop("checked", false);
			$idHalfDayCheckbox.prop("checked", false);
		}
	}

	// Escuchamos los cambios en los checkboxes
	$idInTownCheckbox.on("change", updateCheckboxes);
	$idOutsideTownCheckbox.on("change", updateCheckboxes);
	$idFullDayCheckbox.on("change", updateCheckboxes);
	$idHalfDayCheckbox.on("change", updateCheckboxes);

	// Llamamos a la función inicialmente para establecer el estado correcto
	updateCheckboxes();

	$("#addWaypointBtn").on("click", function () {
		waypointCount++;
		console.log(waypointCount)
		var waypointsContainer = $("#waypointsContainer");
		var waypointDiv = $("<div>")
			.addClass("waypoint-div")
			.attr("data-index", waypointCount);

		var waypointLabelContainer = $("<div>").addClass("mt-8 col-md-12");
		var waypointLabel = $("<h3>").text(`Desvío # ${waypointCount}`);
		waypointLabelContainer.append(waypointLabel);

		var waypointInput = $("<input>")
			.addClass("form-control")
			.attr("type", "text")
			.attr("waypoint", "true")
			.attr("placeholder", "Ingrese desvío")
			.attr("name", `waypoint-${waypointCount + 2}`);
		var latInput = $("<input>")
			.attr("type", "hidden")
			.attr("id", `id_lat_${waypointCount + 2}`)
			.attr("name", `lat_${waypointCount + 2}`);
		var lngInput = $("<input>")
			.attr("type", "hidden")
			.attr("id", `id_long_${waypointCount + 2}`)
			.attr("name", `lng_${waypointCount + 2}`);
		var removeBtn = $("<button>")
			.addClass("btn btn-danger mt-3 delete-waypoint")
			.text("Eliminar")
			.on("click", function () {
				var index = waypointDiv.attr("data-index");
				waypointDiv.remove();
				removeWaypointMarker(index);
				updateWaypointNumbers();
				waypointCount = waypointCount - 1
				AditionalDetour();
			});

		waypointDiv
			.append(waypointLabelContainer)
			.append(waypointInput)
			.append(latInput)
			.append(lngInput)
			.append(removeBtn);
		waypointsContainer.append(waypointDiv);

		// Añadir funcionalidad de autocompletado de Google Maps
		var autocomplete = new google.maps.places.Autocomplete(
			waypointInput[0],
			{
				componentRestrictions: { country: "VE" },
			}
		);

		autocomplete.addListener("place_changed", function () {
			var place = autocomplete.getPlace();
			if (place.geometry) {
				latInput.val(place.geometry.location.lat());
				lngInput.val(place.geometry.location.lng());
				calculateRoute();
			}
		});
		$("#id_waypoints_numbers").val(waypointCount);
	});

	function updateWaypointNumbers() {
		$(".waypoint-div").each(function (index, element) {
			waypointCount++;
			$(element).attr("data-index", waypointCount);
			$(element).find("h3").text(`Desvío # ${waypointCount}`);
			$(element)
				.find("input[type='hidden']")
				.each(function () {
					var name = $(this).attr("name");
					if (name.startsWith("lat_")) {
						$(this).attr("id", `id_lat_${waypointCount + 2}`);
						$(this).attr("name", `lat_${waypointCount + 2}`);
					} else if (name.startsWith("lng_")) {
						$(this).attr("id", `id_long_${waypointCount + 2}`);
						$(this).attr("name", `lng_${waypointCount + 2}`);
					}
				});
		});
		console.log(waypointCount + 'update')
		$("#id_waypoints_numbers").val(waypointCount); // Actualiza el valor del input
		calculateRoute();
	}
	
	function removeWaypointMarker(index) {
		console.log(waypointCount + 'Eliminar')
		var marker = waypointMarkers[index - 1];
		if (marker) {
			marker.setMap(null);
			waypointMarkers.splice(index - 1, 1);
		}
		waypointCount = waypointCount - 1
		// updateWaypointNumbers(); // Llama a la función para actualizar el número de desvíos
		calculateRoute();
	}


    $('#addWaypointBtn').on('click', function(){
        AditionalDetour();
    });

    function AditionalDetour(){
        var detour_price = $('input[name="rate-checkbox"]:checked');
        var detourLocalValue = parseFloat(detour_price.data('detour-local'));
        var waypointCount = $('#waypointsContainer').children().length; // Asegúrate de definir waypointCount

        // Si detourLocalValue es NaN, se devuelve 0
        if (isNaN(detourLocalValue)) {
            detourLocalValue = 0;
        }

        $('#id_aditional').val(detourLocalValue * waypointCount);
		$('#id_final_price').val(parseFloat($('#id_price').val()) + parseFloat($('#id_aditional').val()));
    }

	// Añadir evento para actualizar el precio cuando se cambia el checkbox de ida y vuelta
	$("#id_is_round_trip").change(function () {
			const selectedRate = $("input[name='rate']:checked");
			if (selectedRate.length > 0) {
				const selectedPrice = selectedRate.val();
				const roundTripPrice = selectedRate.data("round-trip-price");
				const isRoundTrip = $(this).is(":checked");
	
				if (isRoundTrip) {
					$("#id_price").val(roundTripPrice);
				} else {
					$("#id_price").val(selectedPrice);
				}
	
				// Si hay un descuento válido, actualizar el precio con descuento
				const discountValue = $('#discount_message span.text-success').text().match(/(\d+)%/);
				if (discountValue) {
					const discount = parseFloat(discountValue[1]) / 100;
					const discountedPrice = isRoundTrip ? roundTripPrice * (1 - discount) : selectedPrice * (1 - discount);
					$("#id_discounted_price").val(discountedPrice.toFixed(2));
				}
			}
	});

	
    function updateDiscountedPrice(discountValue, discountType) {
        const selectedRate = $("input[name='rate-checkbox']:checked");
        if (selectedRate.length > 0) {
            const selectedPrice = parseFloat(selectedRate.val());
            const roundTripPrice = parseFloat(selectedRate.data("round-trip-price"));
            const isRoundTrip = $("#id_is_round_trip").is(":checked");

            let price = isRoundTrip ? roundTripPrice : selectedPrice;
            let discountedPrice;

            if (discountType === 'percentage') {
                discountedPrice = price * (1 - (discountValue / 100));
            } else if (discountType === 'fixed') {
                discountedPrice = price - discountValue;
            }

            $("#id_discounted_price").val(discountedPrice.toFixed(2));
            $("#id_final_price").val(discountedPrice.toFixed(2));
        }
    }

	$('input[name="rate-checkbox"]').on('change', function(){
		AditionalDetour();
	})

	$('#id_discount_code').on('input', function () {
        var code = $(this).val();
        var discountMessage = $('#discount_message');
        var discountedPriceContainer = $('#discounted_price_container');
        var discountedPriceInput = $('#id_discounted_price');

        if (code.length > 0) {
            $.ajax({
                url: urlverify_discount_code,
                type: 'POST',
                data: {
                    'code': code,
                    'csrfmiddlewaretoken': '{{ csrf_token }}'
                },
                success: function (data) {
                    if (data.valid) {
                        discountMessage.html('<span class="text-success">Código válido. Descuento: ' + data.discount_value + ' (' + data.discount_type + ')</span>');
                        console.log(data.discount_value, data.discount_type);
                        updateDiscountedPrice(data.discount_value, data.discount_type);
                        discountedPriceContainer.removeClass('d-none');
                    } else {
                        discountMessage.html('<span class="text-danger">' + data.message + '</span>');
                        discountedPriceContainer.addClass('d-none');
                        discountedPriceInput.val('');
                        $('#id_final_price').val($('#id_price').val());
                        $("#id_final_price").val(discountedPrice.toFixed(2));
                        AditionalDetour();
                    }
                },
                error: function (xhr, status, error) {
                    console.error('Error:', error);
                    discountMessage.html('<span class="text-danger">Error al verificar el código de descuento.</span>');
                    discountedPriceContainer.addClass('d-none');
                    discountedPriceInput.val('');
                }
            });
        } else {
            discountMessage.html('');
            discountedPriceContainer.addClass('d-none');
            discountedPriceInput.val('');
        }
    });
    // Cuando cambia el select de salida
	$("#id_departure_site_route").change(function () {
        const selectedDeparture = $(this).val();

        // Realizar la petición AJAX
        $.ajax({
            url: url_routes_ajax,  // URL de la vista Django
            type: "GET",
            data: { departure: selectedDeparture },
            success: function (data) {
                // Limpiar el select de destino
                $("#id_destination_route").empty();
                console.log(data)
                // Agregar las opciones de destino
                $("#id_destination_route").append(
                    $("<option>", {
                        value: '',
                        text: 'Selecciona un punto de destino',
                        selected: true,
                        disabled: true
                    })
                );
                data.forEach(function (route) {
                    $("#id_destination_route").append(
                        $("<option>", {
                            value: route.arrival_point,
                            text: route.arrival_point
                        })
                    );
                });
            }
        });
    });
    
    $("#id_departure_site_route, #id_destination_route").change(function () {
        const departureId = $("#id_departure_site_route").val();
        const arrivalId = $("#id_destination_route").val();
        const nro = $('#id_person_to_transfer option:selected').length;
        $.ajax({
        url: rates_ajax,  // URL de la vista Django
            type: "GET",
            data: {
                departure_id: departureId,
                arrival_id: arrivalId,
                nro: nro,
            },
            success: function (data) {
                console.log(data)
                const tarifas = data.rates; // Obtén todas las tarifas de la respuesta

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
                $("#precio").text("No disponible");
                $("#precio_ida_vuelta").text("No disponible");
            }
        });

    });
});
