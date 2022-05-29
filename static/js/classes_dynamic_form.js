$(document).ready(function () {
    var current_fields = 0;

    // add row
    $("#addRow").click(function () {
        current_fields++;
        var html = '';
        html += '<div id="inputFormRow">';
        html += '<div class="input-group mb-3">';
        html += `<input type="text" name="class_name_${current_fields}" class="form-control m-input" placeholder="Class name">`;
        html += `<input type="text" name="class_synonyms_${current_fields}" class="form-control m-input" placeholder="Class synonyms">`;
        html += '<div class="input-group-append">';
        html += '<button id="removeRow" type="button" class="btn btn-danger">Remove</button>';
        html += '</div>';
        html += '</div>';

        $('#newRow').append(html);
    });

    // remove row
    $(document).on('click', '#removeRow', function () {
        current_fields--;
        $(this).closest('#inputFormRow').remove();
    });
});