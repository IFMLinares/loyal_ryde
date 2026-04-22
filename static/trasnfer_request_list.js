$(document).ready(function() {
    $('#transfer_list_table').DataTable({
        order: [[1, 'desc']], // Ordenar por la segunda columna (Fecha y Hora) de forma descendente
        columnDefs: [
            { type: 'datetime-ddmmyyyy-hhmm', targets: 1 } // Definir el tipo de columna personalizada para la fecha y hora
        ]
    });

    // Función genérica optimizada para manejar las acciones con AJAX y SweetAlert2 (usando preConfirm)
    function handleAction(requestId, url, actionTitle, confirmButtonText, confirmButtonColor) {
        Swal.fire({
            title: '¿Estás seguro?',
            text: `¿Deseas ${actionTitle} esta solicitud?`,
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: confirmButtonText,
            cancelButtonText: 'No, cancelar',
            confirmButtonColor: confirmButtonColor,
            showLoaderOnConfirm: true, // Mostrar spinner en el botón
            allowOutsideClick: () => !Swal.isLoading(),
            preConfirm: () => {
                // Realizar la petición AJAX directamente en el preConfirm
                return $.ajax({
                    url: url,
                    type: 'POST',
                    data: {
                        'request_id': requestId,
                        'csrfmiddlewaretoken': csr_token
                    }
                }).then(response => {
                    // Si el servidor responde con error aunque el HTTP sea 200
                    if (response.status === 'error') {
                        throw new Error(response.message);
                    }
                    return response;
                }).catch(error => {
                    // Manejar errores (HTTP o lanzados arriba)
                    let msg = 'Hubo un problema al procesar la solicitud.';
                    if (error.responseJSON && error.responseJSON.message) {
                        msg = error.responseJSON.message;
                    } else if (error.message) {
                        msg = error.message;
                    }
                    Swal.showValidationMessage(`Error: ${msg}`);
                });
            }
        }).then((result) => {
            if (result.isConfirmed && result.value) {
                const data = result.value;
                Swal.fire({
                    title: '¡Éxito!',
                    text: data.message,
                    icon: data.status == 'warning' ? 'warning' : 'success'
                }).then(function() {
                    if (typeof url_list !== 'undefined') {
                        window.location.href = url_list;
                    } else {
                        window.location.reload();
                    }
                });
            }
        });
    }

    $(document).on('click', '.validar', function(e) {
        e.preventDefault();
        var requestId = $(this).data('id');
        handleAction(requestId, url_approve_ajax, 'validar', 'Sí, validar', '#3085d6');
    });
    
    $(document).on('click', '.aprobar', function(e) {
        e.preventDefault();
        var requestId = $(this).data('id');
        handleAction(requestId, url_approve_ajax_admin, 'aprobar', 'Sí, aprobar', '#28a745');
    });

    $(document).on('click', '.cancelar', function(e) {
        e.preventDefault();
        var requestId = $(this).data('id');
        handleAction(requestId, url_cancel_ajax, 'cancelar', 'Sí, cancelar', '#dc3545');
    });

    $.fn.dataTable.ext.type.order['datetime-ddmmyyyy-hhmm-pre'] = function (date) {
        var dateTimeParts = date.split('-');
        var dateParts = dateTimeParts[0].split('/');
        var timeParts = dateTimeParts[1].split(':');
        return new Date(dateParts[2], dateParts[1] - 1, dateParts[0], timeParts[0], timeParts[1]).getTime();
    };

    $(document).on('click', '.whatsapp-btn', function() {
        var transferId = $(this).data('transfer-id');
        $.ajax({
            url: '/transfer-request/whatsapp-link/',
            method: 'POST',
            data: {
                transfer_id: transferId,
                csrfmiddlewaretoken: csr_token
            },
            success: function(response) {
                if (response.status === 'success') {
                    window.open(response.whatsapp_url, '_blank');
                } else {
                    Swal.fire('¡Error!', response.message, 'error');
                }
            },
            error: function() {
                Swal.fire('¡Error!', 'No se pudo generar el enlace de WhatsApp.', 'error');
            }
        });
    });

});