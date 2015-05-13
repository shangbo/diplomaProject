$(document).ready(function() {
    $("#process_query").hide('fast', function() {
        $("#submit_history").hide('fast', function() {
            $("#mod_personal_info").hide('fast', function() {
                $("#submit_window").show('fast');
            });
        });
    });
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
                            if(data !== "-1"){
                                alert("submit success!")
                            }
                            else{
                                alert("please login!")
                            }
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
                else if(data === "0"){
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
                        }
                    });
                }
                else{
                    alert("please login!")
                }
            });
        }
    });
    $("#ch_submit_window").click(function(event) {
        $("#ch_submit_window").attr('class', 'am-active');
        $("#ch_submit_history").attr("class", '');
        $("#ch_mod_personal_info").attr("class", '');
        $("#ch_process_query").attr("class", '');
        $("#process_query").hide('fast', function() {
            $("#submit_history").hide('fast', function() {
                $("#mod_personal_info").hide('fast', function() {
                    $("#submit_window").show('fast');
                });
            });
        });
    });
    $("#ch_submit_history").click(function(event) {
        $("#ch_submit_window").attr('class', '');
        $("#ch_submit_history").attr("class", 'am-active');
        $("#ch_mod_personal_info").attr("class", '');
        $("#ch_process_query").attr("class", '');

        $("#submit_window").hide('fast', function() {
            $("#process_query").hide('fast', function() {
                $("#mod_personal_info").hide('fast', function() {
                    $("#submit_history").show('fast');
                });
            });
        });
        $.post('/get_history', {"0":"0"}, function(data, textStatus, xhr) {
            if(data === "need login"){
                alert(data);
            }
            else{
                $("#table_body").html("");
                for(var i=0;i<data['fields'].length;i++){
                    $("#table_head").append("<th>" + data['fields'][i] + "</th>");
                }
                for(var i=0;i<data['history'].length;i++){
                    var html = "<tr>";
                    for(var j=0;j<data['history'][i].length;j++){
                        html += "<td>"
                        html += data['history'][i][j];
                        html += "</td>"
                    }
                    html += "</tr>"
                    console.log(html);
                    $("#table_body").append(html);
                    var html = "";
                }
            }
        });
    });
    $("#ch_mod_personal_info").click(function(event) {
        $("#ch_submit_window").attr('class', '');
        $("#ch_submit_history").attr("class", '');
        $("#ch_mod_personal_info").attr("class", 'am-active');
        $("#ch_process_query").attr("class", '');

        $("#submit_window").hide('fast', function() {
            $("#submit_history").hide('fast', function() {
                $("#process_query").hide('fast', function() {
                    $("#mod_personal_info").show('fast');
                });
            });
        });
        $.post('/get_email', {"0":"0"}, function(data, textStatus, xhr) {
            if(data !== "need login"){
                $("#update_email").val("");
                $("#update_password1").val("");    
                if(data !== ""){
                    $("#update_email").attr("placeholder","Current Email: " + data);
                }
                else{
                    $("#update_email").attr("placeholder","Not Set Email");   
                }
            }
        });
        $("#change_user_info_btn").click(function(event) {
            if($("#update_password1") === $("#update_password2")){
                console.log('..');
                $.ajax({
                        cache: true,
                        type: "POST",
                        url: "/change_user_info",
                        data:$('#change_user_info_form').serialize(),
                        async: false,
                        error: function(request) {
                            // $("#failed_alert").alert();
                        },
                        success: function(data) {
                            if(data === "-1"){
                                alert("password incorrect");
                            }
                            else if(data === "2"){
                                alert("nothing to change");
                            }
                            else if(data === "need login"){
                                alert("need login");
                            }
                            else{
                                alert("update success");   
                            }
                        }
                });
            }
            else{
                alert("password and repeat password not match!");
            }
        });
        
    });

    $("#ch_process_query").click(function(event) {

        //socket.on("get_total_status",{url: })
        $("#ch_submit_window").attr('class', '');
        $("#ch_submit_history").attr("class", '');
        $("#ch_mod_personal_info").attr("class", '');
        $("#ch_process_query").attr("class", 'am-active');

        $("#submit_window").hide('fast', function() {
            $("#submit_history").hide('fast', function() {
                $("#mod_personal_info").hide('fast', function() {
                    $("#process_query").show('fast');
                });
            });
        });

        $.post('/get_process_info', {}, function(data, textStatus, xhr) {
            var socket = io.connect("http://" + document.domain + ':' + location.port);
            socket.on("connect", function() {
                socket.emit('get_all_status');
            });
            $("#process_query").html("");
            var count = 0;
            var url_div = '<div class="am-panel-group" id="accordion_primary"></div>';
            var div1 = $(url_div);
            $("#process_query").append(div1); 
            for(i in data){    
                var url_count = "url_" + count.toString();
                var url_div2 = '<div id="' + url_count + '_primary_panel' + '" class="am-panel am-panel-default"></div>';
                var div2 = $(url_div2);
                div1.append(div2);
                var div3 =$('<div class="am-panel-hd"></div>');
                div2.append(div3);
                var url_h4 = "<h4 class='am-panel-title' data-am-collapse=\"{parent: '#accordion_primary', target: '#primary_content_" + count.toString() + "'}\"></h4>"
                var h4 = $(url_h4);
                div3.append(h4);
                h4.text(i);
                url_div4 = '<div id="primary_content_' + count.toString() + '" class="am-panel-collapse am-collapse am-in"></div>';
                div4 = $(url_div4);
                div2.append(div4);
                url_div5 = '<div class="am-panel-bd"></div>';
                div5 = $(url_div5);
                div4.append(div5);
                div4.collapse('close');
                var url_count = count.toString();
                var url_div = '<div class="am-panel-group" id="accordion_second_' + url_count +'"></div>';
                var div6 = $(url_div);
                div5.append(div6);
                var check_type = data[i]['check_types'];
                for(var j=0;j<check_type.length;j++){
                    var url_div7 = '<div id="' + count + '_' + check_type[j] + '_second_panel' + '" class="am-panel am-panel-default "></div>'
                    var div7 = $(url_div7);
                    div6.append(div7);
                    var div8 = $('<div class="am-panel-hd"></div>');
                    div7.append(div8);
                    var url_h4 = "<h5 class='am-panel-title  get_info_class' data-am-collapse=\"{parent: '#accordion_second_" + url_count + "', target: '#" + check_type[j] + "_second_content_" + count.toString() + "'}\"></h5>"
                    var h4 = $(url_h4);
                    h4.text(check_type[j].replace(/_/gm,' ')); //amazing!
                    div8.append(h4);
                    var url_div9 = '<div id="' + check_type[j] + "_second_content_" + count.toString() + '" class="am-panel-collapse am-collapse am-in"></div>';
                    var div9 = $(url_div9);
                    div7.append(div9);
                    url_div10 = '<div class="am-panel-bd"></div>';
                    div10 = $(url_div10);
                    div9.append(div10);
                    div9.collapse('close');
                    }
                count += 1;
            }
            $('.get_info_class').click(function(e){
                var type_info_ele = $(e.target).parent().parent();
                var type_info = type_info_ele.attr('id');
                var url_info = type_info_ele.parent().parent().parent().siblings("div").children().text();
                var judge_conditon = ($(e.target).attr('class') === "am-panel-title  get_info_class am-collapsed");
                var count = 0;
                if(judge_conditon){
                    var table_ele_str = '<table class="am-table am-table-bordered am-table-radius am-table-striped"></table>';
                    var table_ele = $(table_ele_str);
                    var head_ele = $("<thead><tr><th>Url</th><th>Status</th></tr></thead>");
                    table_ele.append(head_ele);
                    var body_ele = $("<tbody></tbody>");
                    table_ele.append(body_ele);
                    $(type_info_ele.children('.am-panel-collapse').children()).append(table_ele);
                    socket.emit('get_status_info', {"type_info":type_info,"url_info":url_info,"count":count});
                    socket.on("get_status_info", function(data){
                        if(data['result'] !== ""){
                            var item_html = ""
                            if(data['result']["status"]==="ok" || data['result']["status"]>=2){
                                item_html += '<tr class="am-success">';
                            }
                            else if(data['result']["status"]==="doing") {
                                item_html += '<tr class="am-warning">';
                            }
                            else if(data['result']["status"]===-1){
                                item_html += '<tr class="am-danger>';
                            }

                            item_html += "<td>" + data['result']["url"] + "</td>";
                            if(data['result']["status"]===-1){
                                item_html += "<td>" + "Exception" + "</td>";
                            }
                            else if(data['result']["status"]>=2){
                                item_html += "<td>" + data['result']["status"] - 2 + "</td>";
                            }
                            else{
                                item_html += "<td>" + data['result']["status"] + "</td>";
                            }
                            item_html += "</tr>"

                            body_ele.append($(item_html));
                            count += 1;

                            socket.emit('get_status_info', {"type_info":type_info,"url_info":url_info,"count":count});
                        }
                    })
                }
                else{
                    $(type_info_ele.children('.am-panel-collapse').children()).html("");
                }
            })

            socket.on("get_all_status", function(msg){
                for(var url in msg){
                    x = document.getElementsByTagName("h4");
                    for(var i=0;i<x.length;i++){
                        if(url === x[i].textContent){
                            if(msg[url]["all_status"] === '-1'){
                                x[i].parentNode.parentNode.className = "am-panel am-panel-danger";
                            }
                            else if(msg[url]['total_status'] === '0'){
                                x[i].parentNode.parentNode.className = "am-panel am-panel-default";
                            }
                            else if(msg[url]['total_status'] === '1'){
                                x[i].parentNode.parentNode.className = "am-panel am-panel-warning";
                            }
                            else if(msg[url]['total_status'] === '2'){
                                x[i].parentNode.parentNode.className = "am-panel am-panel-success";
                            }
                            else{
                                x[i].parentNode.parentNode.className = "am-panel am-panel-danger";
                            }
                            var sub_type = x[i].parentNode.parentNode.lastChild.firstChild.firstChild.childNodes;
                            for(var i=0; i<sub_type.length; i++){
                                var text = sub_type[i].firstChild.firstChild.textContent;
                                var key = text.replace(/ /gm,'_');
                                if(key === "Scan"){
                                    key = "scan";
                                }
                                if(msg[url][key] === "0"){
                                    sub_type[i].className = "am-panel am-panel-default";
                                }
                                else if(msg[url][key] === "1"){
                                    sub_type[i].className = "am-panel am-panel-warning";
                                }
                                else if(msg[url][key] === "2"){
                                    sub_type[i].className = "am-panel am-panel-success";
                                }
                                else if(msg[url][key] === "-1"){
                                    sub_type[i].className = "am-panel am-panel-danger";
                                }
                                else{
                                    sub_type[i].className = "am-panel am-panel-danger";
                                }
                            }

                        }

                    }
                }
                socket.emit('get_all_status');
            });

        });
        
    });
});
