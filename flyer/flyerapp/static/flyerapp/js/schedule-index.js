/**
 * Created by eduardo on 6/26/15.
 */
$(document).ready(function () {

    $("button[data-ctr-edit]").on('click', function () {
        var id = $(this).data('id');
        $('#modal-schedule-edit-' + id).modal('toggle');
    });
})
