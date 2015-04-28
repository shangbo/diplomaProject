$(document).ready(function() {
    $("#confirm_go").click(function(event) {
                    $.ajax({
                        cache: true,
                        type: "POST",
                        url: "/submit_form.html",
                        data:$('#submit_form').serialize(),
                        async: false,
                        error: function(request) {
                            // $("#failed_alert").alert();
                        },
                        success: function(data) {
                            alert("submit success!")
                            // $("#success_alert").alert();
                        }
                    });
    });
    $("#submit_btn").click(function(event) {
        var root_url = $("#url_string").val()
        if(root_url !==""){
            $.post('/is_repeat_scan.html', {"root":root_url}, function(data, textStatus, xhr) {
                if(data === "1"){
                    $("#confirm_submit").modal("open");
                }
                else{
                    $.ajax({
                        cache: true,
                        type: "POST",
                        url: "/submit_form.html",
                        data:$('#submit_form').serialize(),
                        async: false,
                        error: function(request) {
                            // $("#failed_alert").alert();
                        },
                        success: function(data) {
                            alert("submit success!")
                            // $("#success_alert").alert();
                        }
                    });
                    
                }
            });
        }
    });
});