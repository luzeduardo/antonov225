/**
 * Created by eduardo on 6/26/15.
 */
    //INICIALIZANDO O DATATABLE
function datataTableStart(elementoId,paging,searching) {
    $(elementoId).dataTable({
        initComplete: function () {
            this.api().columns().every( function () {
                var column = this;
                var select = $('<select><option value=""></option></select>')
                    .appendTo( $(column.footer()).empty() )
                    .on( 'change', function () {
                        var val = $.fn.dataTable.util.escapeRegex(
                            $(this).val()
                        );

                        column
                            .search( val ? '^'+val+'$' : '', true, false )
                            .draw();
                    } );

                column.data().unique().sort().each( function ( d, j ) {
                    select.append( '<option value="'+d+'">'+d+'</option>' )
                } );
            } );
        },
        searching: searching,
        paging: paging,
        "pageLength": 5,
        "language": {
            "search": "Filter records:"
        },
        "bLengthChange": false,
        "oLanguage": {
            "sLengthMenu": "Mostrar _MENU_ registros",
            "sZeroRecords": "N&atilde;o foram encontrados resultados",
            "sInfo": "",
            "sInfoEmpty": "",
            "sInfoFiltered": "(filtrado de _MAX_ registros no total)",
            "sInfoPostFix": "",
            "sUrl": "",
            "sSearch": "Buscar:",
            "oPaginate": {
                "sFirst": "<<",
                "sPrevious": "<",
                "sNext": ">",
                "sLast": ">>"
            }
        }
    });
}

$(document).ready(function () {

    $("button[data-ctr-edit]").on('click', function () {
        var id = $(this).data('id');
        $('#modal-schedule-edit-' + id).modal('toggle');
    });

    $("button[data-ctr-new]").on('click', function () {
        $('#modal-schedule-new').modal('toggle');
    });

    $("button[data-ctr-del]").on('click', function () {
        var id = $(this).data('id');
        $('#modal-schedule-delete-' + id).modal('toggle');
    });

    $("button[data-ctr-play]").on('click', function () {
        var id = $(this).data('id');

        $.ajax({
                type: 'POST',
                data: {
                    'id':id
                },
                url: '/manual/',
                success: function (result, status, xhr) {

                },
                error: function (result, status, xhr) {
                }
            });

    });

    $("button[data-ctr-fly]").on('click', function () {
        var id = $(this).data('id');

        $.ajax({
                type: 'POST',
                sync: false,
                data: {
                    'id':id
                },
                url: '/flights/',
                success: function (result, status, xhr) {
                    $("#result-fligths").html("");
                    $("#result-fligths").html(result);
                    $('#modal-schedule-flights').modal('toggle');
                },
                error: function (result, status, xhr) {
                }
            });

    });

    $("button[data-ctr-play-auto]").on('click', function () {
        var id = $(this).data('id');

        $.ajax({
                type: 'POST',
                data: {
                    'id':id
                },
                url: '/automatic/',
                success: function (result, status, xhr) {

                },
                error: function (result, status, xhr) {
                }
            });

    });

    $("button[data-ctr-stop-auto]").on('click', function () {
        var id = $(this).data('id');

        $.ajax({
                type: 'POST',
                data: {
                    'id':id
                },
                url: '/stop-automatic/',
                success: function (result, status, xhr) {

                },
                error: function (result, status, xhr) {
                }
            });

    });

})
