$(document).ready(function() {
    // Definir un tipo de columna personalizado para fechas en formato DD/MM/YYYY-HH:mm
    $.fn.dataTable.ext.type.order['datetime-ddmmyyyy-hhmm-pre'] = function(d) {
        var parts = d.split('-');
        var dateParts = parts[0].split('/');
        var timeParts = parts[1].split(':');
        return new Date(
            parseInt(dateParts[2], 10),  // Año
            parseInt(dateParts[1], 10) - 1,  // Mes (0-indexed)
            parseInt(dateParts[0], 10),  // Día
            parseInt(timeParts[0], 10),  // Hora
            parseInt(timeParts[1], 10)   // Minuto
        ).getTime();
    };

    $('#transfer_list_table').DataTable({
        "order": [[0, "desc"]],
        "columnDefs": [
            { "type": "datetime-ddmmyyyy-hhmm", "targets": 0 }
        ]
    });

    $('.validar').click(function(e) {
        e.preventDefault();
        var requestId = $(this).data('id');
        $.ajax({
            url: url_approve_ajax,
            type: 'POST',
            data: {
                'request_id': requestId,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(data) {
                if (data.status == 'success') {
                    Swal.fire({
                        title: '¡Éxito!',
                        text: data.message,
                        icon: 'success'
                    }).then(function() {
                        // Redireccionar a una URL después de hacer clic en el botón "OK"
                        window.location.reload()
                    });
                } else {
                    Swal.fire({
                        title: '¡Error!',
                        text: data.message,
                        icon: 'error'
                    });
                }
            }            
        });
    });
    
    $('.aprobar').click(function(e) {
        e.preventDefault();
        var requestId = $(this).data('id');
        $.ajax({
            url: url_approve_ajax_admin,
            type: 'POST',
            data: {
                'request_id': requestId,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(data) {
                if (data.status == 'success') {
                    Swal.fire({
                        title: '¡Éxito!',
                        text: data.message,
                        icon: 'success'
                    }).then(function() {
                        // Redireccionar a una URL después de hacer clic en el botón "OK"
                        window.location.reload()
                    });
                } else {
                    Swal.fire({
                        title: '¡Error!',
                        text: data.message,
                        icon: 'error'
                    });
                }
            }            
        });
    });

    $('.cancelar').click(function(e) {
        e.preventDefault();
        var requestId = $(this).data('id');
        $.ajax({
            url: url_cancel_ajax,
            type: 'POST',
            data: {
                'request_id': requestId,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(data) {
                if (data.status == 'warning') {
                    Swal.fire({
                        title: '¡Éxito!',
                        text: data.message,
                        icon: 'Warning'
                    }).then(function() {
                        // Redireccionar a una URL después de hacer clic en el botón "OK"
                        window.location.reload()
                    });
                } else {
                    Swal.fire({
                        title: '¡Error!',
                        text: data.message,
                        icon: 'error'
                    });
                }
            }            
        });
    });
});