var frm = $('#frm');
$(document).on('click', '#submit', function (e) {
    e.preventDefault();

    $.ajax({
        type: "POST",
        url: "/upload",
        data: frm.serialize(),
        success: function (data) {
            if (data === 'ok') {
                bootbox.alert('successful')
            } else {
                bootbox.alert('not successful');
            }
        }
    });

});

