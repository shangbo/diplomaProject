$(document).ready(function() {
    $("#register_btn").click(function(event) {
        var p1 = $("#register_password1").val();
        var p2 = $("#register_password2").val();
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
                            if(data === "1"){
                                alert("register successful!")
                            }
                            else if(data === "-1"){
                                alert("user has existed")
                            }
                            else if(data === "-2"){
                                alert("please fill required field")
                            }
                        }
                    });
        }
        else{
            alert("password and repeat password not match!");
        }
    });
});