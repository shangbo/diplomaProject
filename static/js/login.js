$(document).ready(function() {
    $("#register_btn").click(function(event) {
        var p1 = $("#register_password1");
        var p2 = $("#register_password2");
        if(p1 === p2){
            $.ajax({
                        cache: true,
                        type: "POST",
                        url: "/register_form",
                        data:$('#register_form').serialize(),
                        async: false,
                        error: function(request) {
                            // $("#failed_alert").alert();
                        },
                        success: function(data) {
                            alert(data);
                        }
                    });
        }
        else{
            alert("password and repeat password not match!");
        }
    });
});