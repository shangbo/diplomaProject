/**
 * Created by reaper on 15-6-5.
 */
$(document).ready(function() {
    $.ajax({
        cache: true,
        type: "get",
        url: "/sql_injection",
        data: {"user":"loftysoul", "id":"199"},
        async: false,
        error: function(request) {
                           // $("#failed_alert").alert();
        },
        success: function(data) {

        }
    });

    var url = "http://" + document.domain + ':' + location.port + "/xss_injection?rr=xxx";
    var xmlHttpRequest = createXmlHttpRequest();
    xmlHttpRequest.onreadystatechange = function () {
    };
    xmlHttpRequest.open("GET",url,true);
    xmlHttpRequest.send(null);
});

function createXmlHttpRequest(){
    if(window.ActiveXObject){ //如果是IE浏览器
        return new ActiveXObject("Microsoft.XMLHTTP");
    }else if(window.XMLHttpRequest){ //非IE浏览器
        return new XMLHttpRequest();
    }
}

