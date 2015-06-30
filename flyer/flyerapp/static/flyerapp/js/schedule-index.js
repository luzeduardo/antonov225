/**
 * Created by eduardo on 6/26/15.
 */
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

})
