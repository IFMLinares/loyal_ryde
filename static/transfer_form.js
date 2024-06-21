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

	$("#id_executive_transfer").change(function () {
		if (this.checked) {
			// Si el checkbox está seleccionado, quitamos la clase 'd-none' del div
			$("#localidad").removeClass("d-none");
		} else {
			// Si el checkbox no está seleccionado, agregamos la clase 'd-none' al div
			$("#localidad").addClass("d-none");
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

	$('#id_payment_method').change(function() {
        if($(this).val() == "1") {
            // Si el valor seleccionado es "1", quitamos la clase 'd-none' del div
            $('#data_required').removeClass('d-none');
        } else {
            // Si el valor seleccionado es cualquier otro, agregamos la clase 'd-none' al div
            $('#data_required').addClass('d-none');
        }
    });

});
