$(document).ready(function() {
    $('#transfer_list_table').DataTable({
        order: false,
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
    $.fn.dataTable.ext.type.order['datetime-ddmmyyyy-hhmm-pre'] = function (date) {
    var dateTimeParts = date.split('-');
    var dateParts = dateTimeParts[0].split('/');
    var timeParts = dateTimeParts[1].split(':');
    return new Date(dateParts[2], dateParts[1] - 1, dateParts[0], timeParts[0], timeParts[1]).getTime();
};
});