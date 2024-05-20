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
		if (!name || !phone || !company) {
			if (!name) {
				$("#name").css("border-color", "red");
			}
			if (!phone) {
				$("#phone").css("border-color", "red");
			}
			if (!company) {
				$("#company").css("border-color", "red");
			}
			return;
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
				console.log(response.people_transfer);
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
		$("#name, #phone, #company").on("input", function () {
			$(this).css("border-color", "");
		});
});
