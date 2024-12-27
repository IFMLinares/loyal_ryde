
$(document).ready(function() {
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

    $('#transfer_list_table').DataTable({
        "order": [[0, "desc"]]
    });


});
