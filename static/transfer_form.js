// --- Lógica para poblar y sincronizar el select de primary_person también en la vista de edición ---
function updatePrimaryPersonSelect() {
	var $multi = $('#id_person_to_transfer');
	var $primary = $('#id_primary_person');
	if ($primary.length === 0) {
		return;
	}
	var selected = $multi.val() || [];
	$primary.empty();
	$primary.append('<option value="">Seleccione pasajero principal</option>');
	if (selected.length > 0) {
		$multi.find('option:selected').each(function() {
			var val = $(this).val();
			var text = $(this).text();
			$primary.append('<option value="' + val + '">' + text + '</option>');
		});
		$primary.prop('disabled', false);
	} else {
		$primary.prop('disabled', true);
	}
	if (window.initial_primary_person_id && !$primary.data('initialized')) {
		$primary.val(String(window.initial_primary_person_id));
		$primary.data('initialized', true);
	}
	$primary.trigger('change');
}

$(document).ready(function () {
	// Inicializar Select2 en el select de primary_person (en create y update)
	if ($.fn.select2) {
		var $primary = $('#id_primary_person');
		if ($primary.length) {
			$primary.select2({
				placeholder: 'Seleccione pasajero principal',
				width: '100%'
			});
		}
	}

	// Sincronizar el select de primary_person con los seleccionados en el multi-select
	$(document).on('change', '#id_person_to_transfer', function() {
		updatePrimaryPersonSelect();
	});
	// Inicializar el select de primary_person si ya hay seleccionados (para update)
	updatePrimaryPersonSelect();

	// Personalizar el placeholder del buscador multi.js
	setTimeout(function() {
		var $input = $('#id_person_to_transfer').next('.multi-wrapper').find('input[type="text"]');
		if ($input.length) {
			$input.attr('placeholder', 'Buscar pasajeros');
		}
	}, 100);

	// Si la vista es de cliente y no se muestra el select de empresa,
	// cargar automáticamente las personas de la empresa del usuario.
	$(function() {
		var initCompany = $('#id_company').val() || window.company || null;
		if (initCompany) {
			// Disparamos el mismo flujo que el change del select para reutilizar la lógica
			$('#id_company').trigger('change');
		}
	});
});
	// --- Cargar personas de la empresa seleccionada en el select multi ---
	$(document).on('change', '#id_company', function() {
		var companyId = $(this).val();
		if (!companyId) return;
		// Ensure url_form is defined
		if (typeof url_form === 'undefined' || !url_form) {
			window.url_form = '/transfer-request/people/create';
		}
		$.ajax({
			url: '/ajax/people-transfer/',
			method: 'GET',
			data: { company_id: companyId },
			success: function(response) {
				var $select = $('#id_person_to_transfer');
				var existingSelected = $select.val() || [];
				var initialSelected = Array.isArray(window.initial_people_ids) ? window.initial_people_ids.map(String) : [];
				var selectedSet = new Set(existingSelected.map(String).concat(initialSelected));
				$select.empty();
				if (response.people && response.people.length > 0) {
					response.people.forEach(function(person) {
						var isSelected = selectedSet.has(String(person.id));
						var option = new Option(person.name + ' (' + person.phone + ')', person.id, isSelected, isSelected);
						$select.append(option);
					});
				} else {
					$select.append(new Option('No hay personas registradas', '', false, false));
				}
				$select.trigger('change');
				// Destruir y volver a inicializar multi.js para refrescar visualmente
				if ($select.data('multi')) {
					$select.multi('destroy');
				}
				// Eliminar el select y su wrapper
				var $oldSelect = $('#id_person_to_transfer');
				var $wrapper = $oldSelect.next('.multi-wrapper');
				if ($wrapper.length) { $wrapper.remove(); }
				$oldSelect.remove();

				// Crear un nuevo select vacío
				var $nuevoSelect = $('<select class="form-select" aria-label="seleccione" multiple id="id_person_to_transfer" name="person_to_transfer" required></select>');
				// Insertar el nuevo select en el contenedor adecuado
				$('#id_person_to_transfer_container').append($nuevoSelect);

				// Llenar el select con las opciones traídas por AJAX
				if (response.people && response.people.length > 0) {
					response.people.forEach(function(person) {
						var isSelected = selectedSet.has(String(person.id));
						var option = new Option(person.name + ' (' + person.phone + ')', person.id, isSelected, isSelected);
						$nuevoSelect.append(option);
					});
				} else {
					$nuevoSelect.append(new Option('No hay personas registradas', '', false, false));
				}

				// Inicializar multi.js sobre el nuevo select
				$nuevoSelect.multi({
					search_placeholder: 'Buscar pasajeros',
					"none_text": 'No hay pasajeros seleccionados',
					"select_all": false
				});
				// Cambiar el placeholder del input de búsqueda si multi.js no lo toma
				setTimeout(function() {
					var $input = $nuevoSelect.next('.multi-wrapper').find('input[type="text"]');
					if ($input.length) {
						$input.attr('placeholder', 'Buscar pasajeros');
					}
				}, 100);
				// Forzar apertura/cierre para renderizar los options
				setTimeout(function() {
					var $label = $nuevoSelect.next('.multi-wrapper').find('.multi-label');
					$label.trigger('mousedown').trigger('mouseup');
				}, 50);

				// Re-sincronizar el pasajero principal con el estado actual
				if ($('#id_primary_person').length) {
					$nuevoSelect.trigger('change');
				}
			},
			error: function() {
				alert('Error al cargar personas de la empresa.');
			}
		});
	});
$(document).ready(function () {
	$("#id_date").daterangepicker({
		singleDatePicker: true,
		showDropdowns: true,
		minYear: 1901,
		maxYear: parseInt(moment().format("DD/MM/YYYY"), 10),
			locale: {
		format: "DD/MM/YYYY",
		separator: " - ",
		applyLabel: "Aplicar",
		cancelLabel: "Cancelar",
		daysOfWeek: ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sa"],
		monthNames: [
			"Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
			"Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
		],
		firstDay: 1
	}
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
		var c = $("#id_company").val();
		console.log(name, phone, c);
		// Validación de campos
		if (!name || !phone || !c) {
			if (!name) {
				$("#name").css("border-color", "red");
			}
			if (!phone) {
				$("#phone").css("border-color", "red");
			}
			if (!c) {
				$("#id_company")[0].setCustomValidity("Debe seleccionar una empresa");
				$("#id_company")[0].reportValidity();
			}
			return;
		}
		if (c == "") {
			c = "N/A";
		}
		console.log(name, phone, c);
		// Realiza la petición AJAX
		// Ensure url_form is defined
		if (typeof url_form === 'undefined' || !url_form) {
			window.url_form = '/transfer-request/people/create';
		}
		$.ajax({
			url: url_form,
			method: "POST",
			data: {
				name: name,
				phone: phone,
				company: c,
			},
			success: function (response) {
				console.log(response.people_transfer);

				$("#name").val("");
				$("#phone").val("");

				var created = true;
				if (typeof response.created !== 'undefined') {
					created = !!response.created;
				}

				var people = JSON.parse(response.people_transfer);
				// Collect existing options into an array
				var options = [];
				$('#id_person_to_transfer option').each(function() {
					var $opt = $(this);
					if ($opt.val()) {
						options.push({ value: $opt.val(), text: $opt.text(), selected: $opt.prop('selected') });
					}
				});

				// Handle response: if already existed, prefer selecting existing option and warn
				people.forEach(function(person) {
					var pid = String(person.pk);
					var ptext = person.fields.name + ' (' + person.fields.phone + ')';
					var alreadyPresent = options.some(function(o) { return String(o.value) === pid; });
					if (!alreadyPresent) {
						options.push({ value: pid, text: ptext, selected: true });
					} else {
						// If present, ensure it's selected
						options = options.map(function(o) {
							if (String(o.value) === pid) { o.selected = true; }
							return o;
						});
					}
				});

				// Remove old select and wrapper
				var $oldSelect = $('#id_person_to_transfer');
				var $wrapper = $oldSelect.next('.multi-wrapper');
				if ($wrapper.length) { $wrapper.remove(); }
				$oldSelect.remove();

				// Create a new select and populate options
				var $nuevoSelect = $('<select class="form-select" aria-label="seleccione" multiple id="id_person_to_transfer" name="person_to_transfer" required></select>');
				options.forEach(function(opt) {
					var $opt = $('<option></option>').val(opt.value).text(opt.text);
					if (opt.selected) { $opt.prop('selected', true); }
					$nuevoSelect.append($opt);
				});

				// Insert and initialize multi.js
				$('#id_person_to_transfer_container').append($nuevoSelect);
				$nuevoSelect.multi({
					search_placeholder: 'Buscar pasajeros',
					"none_text": 'No hay pasajeros seleccionados',
					"select_all": false
				});

				// Ensure primary person select is updated
				$nuevoSelect.trigger('change');

				// Notify user if record already existed
				if (!created) {
					if (typeof Swal !== 'undefined') {
						Swal.fire({ icon: 'warning', title: 'Ya existe', text: response.message || 'La persona ya existe.' });
					} else {
						alert(response.message || 'La persona ya existe.');
					}
				} else {
					// optional success feedback
					if (typeof Swal !== 'undefined') {
						Swal.fire({ icon: 'success', title: 'Añadido', toast: true, position: 'top-end', showConfirmButton: false, timer: 1500 });
					}
				}
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
		}else if ($(this).val() == "4") {
			$("#data_required_pago_movil").removeClass("d-none");
		} 
		else {
			// Si el valor seleccionado es cualquier otro, agregamos la clase 'd-none' al div
			$("#data_required").addClass("d-none");
			$("#data_required_pago_movil").addClass("d-none");
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


	$('#id_discount_code').on('input', function () {
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

	$('#id_discount_code').on('keyup', function () {
		console.log('Descuento')
		var code = $(this).val();
		var discountMessage = $('#discount_message');
		var discountedPriceContainer = $('#discounted_price_container');
		var discountedPriceInput = $('#id_discounted_price');
		var price = parseFloat($('#id_price').val());
		var aditionalPrice = parseFloat($('#id_aditional').val()) || 0;
		var subtotal = price + aditionalPrice;

		if (code.length > 0) {
			$.ajax({
				url: urlverify_discount_code,
				type: 'POST',
				data: {
					'code': code,
					'csrfmiddlewaretoken': '{{ csrf_token }}'
				},
				success: function (data) {
					console.log(data);
					if (data.valid) {
						discountMessage.html('<span class="text-success">Código válido. Descuento: ' + data.discount_value +  ')</span>');
						// verificar si es fixed o percentage
						var discountedPrice = parseFloat($('#id_price').val());
						if (data.discount_type === 'percentage') {
							// calcular el porcentaje a restar
							var discountAmount = (data.discount_value / 100) * subtotal;
							$('#id_final_price').val((subtotal - discountAmount).toFixed(2));

						} else if (data.discount_type === 'fixed') {
							// si es fixed calcular el total menos el descuento
							discountedPrice = subtotal - data.discount_value;
							$('#id_final_price').val(discountedPrice.toFixed(2));
						}
						// updateDiscountedPrice(data.discount_value, data.discount_type);
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
	
	// Añade la función getCityFromAddress
});
