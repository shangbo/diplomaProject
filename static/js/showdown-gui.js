//
// showdown-gui.js
//
// A sample application for Showdown, a javascript port
// of Markdown.
//
// Copyright (c) 2007 John Fraser.
//
// Redistributable under a BSD-style open source license.
// See license.txt for more information.
//
// The full source distribution is at:
//
//				A A L
//				T C A
//				T K B
//
//   <http://www.attacklab.net/>
//

//
// The Showdown converter itself is in showdown.js, which must be
// included by the HTML before this file is.
//
// showdown-gui.js assumes the id and class definitions in
// showdown.html.  It isn't dependent on the CSS, but it does
// manually hide, display, and resize the individual panes --
// overriding the stylesheets.
//
// This sample application only interacts with showdown.js in
// two places:
//
//  In startGui():
//
//      converter = new Showdown.converter();
//
//  In convertText():
//
//      text = converter.makeHtml(text);
//
// The rest of this file is user interface stuff.
//


//
// Register for onload
//
window.onload = startGui;

// function onbeforeunload_handler(){   
//         alert("test");
//     }   
       
// function onunload_handler(){   
//         var warning="谢谢光临";   
//         alert(warning);   
//     }
// window.onbeforeunload = onbeforeunload_handler;   
// window.onunload = onunload_handler; 
//
// Globals
//

var converter;
var convertTextTimer,processingTime;
var lastText,lastOutput,lastRoomLeft;
var convertTextSetting, convertTextButton, paneSetting;
var inputPane,previewPane,outputPane,syntaxPane;
var maxDelay = 3000; // longest update pause (in ms)

var tag = new Array();  //tag list

//
//	Initialization
//

function startGui() {
	// find elements
	convertTextSetting = document.getElementById("convertTextSetting");
	convertTextButton = document.getElementById("convertTextButton");
	paneSetting = document.getElementById("paneSetting");

	inputPane = document.getElementById("inputPane");
	previewPane = document.getElementById("previewPane");
	outputPane = document.getElementById("outputPane");
	syntaxPane = document.getElementById("syntaxPane");
	newButton = document.getElementById("newButton");
	tagList = document.getElementById("tagList");
	tagListButton = document.getElementById("tagListButton");
	allTagList = document.getElementById("allTagList");
	allEssayList = document.getElementById("allEssayList");
	// set event handlers
	convertTextSetting.onchange = onConvertTextSettingChanged;
	convertTextButton.onclick = onConvertTextButtonClicked;
	paneSetting.onchange = onPaneSettingChanged;
	window.onresize = setPaneHeights;

	//code highligt
	codeHighlight();

	// First, try registering for keyup events
	// (There's no harm in calling onInput() repeatedly)
	window.onkeyup = inputPane.onkeyup = onInput;

	// In case we can't capture paste events, poll for them
	var pollingFallback = window.setInterval(function(){
		if(inputPane.value != lastText)
			onInput();
	},1000);

	// Try registering for paste events
	inputPane.onpaste = function() {
		// It worked! Cancel paste polling.
		if (pollingFallback!=undefined) {
			window.clearInterval(pollingFallback);
			pollingFallback = undefined;
		}
		onInput();
	}

	// Try registering for input events (the best solution)
	if (inputPane.addEventListener) {
		// Let's assume input also fires on paste.
		// No need to cancel our keyup handlers;
		// they're basically free.
		inputPane.addEventListener("input",inputPane.onpaste,false);
	}

	// poll for changes in font size
	// this is cheap; do it often
	window.setInterval(setPaneHeights,250);

	// start with blank page?
	if (top.document.location.href.match(/\?blank=1$/))
		inputPane.value = "";

	// refresh panes to avoid a hiccup
	onPaneSettingChanged();

	// build the converter
	converter = new Showdown.converter();

	// do an initial conversion to avoid a hiccup
	convertText();

	// give the input pane focus
	inputPane.focus();

	// start the other panes at the top
	// (our smart scrolling moved them to the bottom)
	previewPane.scrollTop = 0;
	outputPane.scrollTop = 0;

	//sync markdown content to server
	window.setInterval(syncContent,10000);
	document.onkeydown = function(event) {
	    if (event.ctrlKey == true && event.keyCode == 83) {//Ctrl+S 
	        syncContent();
	        return false
	    }

	}

	//modified input panel table event
	inputPane.onkeydown = function(event) {
		if (event.keyCode == 9){
			var pos = addSpace(this);
			setCaretPosition(this, pos + 4);
			return false
		}

	}

	inputPane.onkeyup = function(event) {
		if(isChangingTag(this) === 1){
			if(event.ctrlKey == false){
				if(event.keyCode == 32 || event.keyCode == 13 || event.keyCode == 8){
					syncContent();
					getChangingTagInfo();
				}
			}
		}
		else{
			$("#tagDropdown").dropdown('close');
		}
	}

    //new build button click event 
    newButton.onclick = function(event) {
		syncContent();
		$.post("/loftysoul_new", '0',function(response_data, status) {
			if(response_data === '3'){
				$("#inputPane").val("#Markdown \r\n标签:\r\n\r\n---");
				previewPane.innerHTML = "<h1 id=\"markdown\">Markdown</h1>\n<a href=\"\"><code>\u672a\u5206\u7c7b</code></a> \n\n<hr>";
				syncContent();
			}
		});
	}
     
    //tag list button click event
    tagListButton.onclick = function(event) {
    	$("#tagDropdown").dropdown('close');
    	$("#tagPage").slideToggle("fast", function(){
    		allTagList.innerHTML = ""
    		allEssayList.innerHTML = ""
	    	allTagList.innerHTML = '<p class="tagListSpan preLoad">加载中...</p>';
	    	syncContent();
	    	$.post("/loftysoul_tag_info", {"tags":"ALL"}, function(response_data, status){
	    		if(response_data){
		    		allTagList.innerHTML = "";
		    		for(tag in response_data){
						allTagList.innerHTML += '<li class="am-btn am-btn-default am-btn-block tagItem"><a href="#"><b>' + tag + '</b>(' + response_data[tag]  + ')</a></li>';
					}
					$(".tagItem").click(function(){               //tagItem click event
						allEssayList.innerHTML = "";
						var tagName = "";
						var endIndex = $(this).children("a").html().indexOf("</b>");
						if(endIndex !== -1){
							tagName = $(this).children("a").html().substring(3, endIndex);
						}
						allEssayList.innerHTML = '<p class="tagListSpan preLoad">加载中...</p>';
						$.post("/loftysoul_essay_title", {"newWindow":"0","tagName":tagName}, function(data, status){
							allEssayList.innerHTML = "";
							if(data !== "4"){
								for(essayId in data){
									allEssayList.innerHTML += '<li class="am-btn am-btn-default am-btn-block essayItem"><a id="id_'+ essayId +'" href="#"><b>' + data[essayId]  + '</b></a></li>';
								}
							}
							else{
									allEssayList.innerHTML = '<p class="tagListSpan preLoad">没有任何文章</p>';				
							}
							$(".essayItem").click(function(){
								var essay_id_str = $(this).children("a").attr("id");
								essay_id = essay_id_str.substring(3, essay_id_str.length);
								$.post('/loftysoul_essay_info',{"essayId":essay_id}, function(data, status){
									$("#tagPage").slideToggle("fast", function(){
										$("#inputPane").val(data['markdown']);
										convertText();
										syncContent();
									});
								});
								
							});
						});
						
					});
				}
				else{
					allTagList.innerHTML = '<p class="tagListSpan preLoad">没有任何标签</p>';
				}
	    	});
    	});
    }

    //sync scroll event between inputPane and previewPane
    inputPane.onscroll = function() {
    	postion_percent = inputPane.scrollTop / inputPane.scrollHeight;
    	previewPane_postion = postion_percent * previewPane.scrollHeight;
    	previewPane.scrollTop = previewPane_postion;
    }


	//
	//tag click event
	//
	// $(".tagClick").click(function(){
	// 	syncContent();
	// });

	//
	//release button
	//
	$("#releaseButton").click(function(){
		syncContent();
		$.post("/loftysoul_release", {"release":"1"}, function(data, status){
			if(data === "2"){
				$("#modalTitle").text("你的文章已经是最新发布");
				$("#modal-box").modal('open');
			}
			else{
				var b = new Base64();
				var str = b.encode(data["title"]);
				var href_show = ""
				if(location.port === "80"){
					href_show = location.protocol + "://" + location.hostname + "/essay/" + data["essay_id"] + "/" + str + ".html";
				}
				else{
					href_show = location.protocol + "://" + location.hostname + ":" + location.port + "/essay/" + data["essay_id"] + "/" + str + ".html";	
				}
				href = "/essay/" + data["essay_id"] + "/" + str + ".html";
				$("#modalTitle").text("文章已经发布，链接为:");
				$("#releaseLink").text(href_show);
				$("#releaseLink").attr("href", href);
				$("#modal-box").modal('open');
			}
			syncContent();
		});
	});
}

function getChangingTagInfo(){
	$.post("/loftysoul_tag_info", {"tags":JSON.stringify(tag)}, function(response_data, status){
		$("#tagDropdown").dropdown('open');
		inputPane.focus();
		tagList.innerHTML = "";
		for(tag in response_data){
			tagList.innerHTML += '<li><a href="#"><b>' + tag + '</b>' + '<code id="essayNumInTag">共有' + response_data[tag] + '篇文章</code>' + '</a></li>';
		}
	});
}


function getCursortPosition (ctrl) {//获取光标位置函数
	var CaretPos = 0;	// IE Support
	if (document.selection) {
	ctrl.focus ();
		var Sel = document.selection.createRange ();
		Sel.moveStart ('character', -ctrl.value.length);
		CaretPos = Sel.text.length;
	}
	// Firefox support
	else if (ctrl.selectionStart || ctrl.selectionStart == '0')
		CaretPos = ctrl.selectionStart;
	return (CaretPos);
}

function setCaretPosition(ctrl, pos){
//设置光标位置函数 
	if(ctrl.setSelectionRange) 
	{ 
		ctrl.focus(); 
		ctrl.setSelectionRange(pos,pos); 
	} 
	else if (ctrl.createTextRange) { 
		var range = ctrl.createTextRange(); 
		range.collapse(true); 
		range.moveEnd('character', pos); 
		range.moveStart('character', pos); 
		range.select(); 
	} 
}	

function addSpace(obj){	
	pos = getCursortPosition(obj);
	s = obj.value;
	obj.value = s.substring(0, pos)+"    "+s.substring(pos);
	return pos
}

//
// sync content 
function syncContent(){
	var data = {"markdown":$("#inputPane").val(),"html_text":$("#previewPane").html(), "tags":JSON.stringify(tag)};
    $.post("/loftysoul_update", data, function(response_data, status) {
        if(response_data === '1'){
        	if($("#isRelease").text() === "已发布"){
	            $("#isRelease").attr("class", "am-topbar-btn am-btn am-btn-danger");
	            $("#isRelease").text("未发布");
	        }
	        if($("#hasUpdate").text() === "无更新"){
	            $("#hasUpdate").attr("class", "am-topbar-btn am-btn am-btn-primary");
	            $("#hasUpdate").text("有更新");
            }
        }
        else if (response_data === "11"){
        	if($("#isRelease").text() === "未发布"){
	        	$("#isRelease").attr("class", "am-topbar-btn am-btn am-btn-primary");
	            $("#isRelease").text("已发布");
	            $("#releaseButton").text("更新发布");
        	}
        	if($("#hasUpdate").text() === "无更新"){
	            $("#hasUpdate").attr("class", "am-topbar-btn am-btn am-btn-primary");
	            $("#hasUpdate").text("有更新");
        	}
        }
        else if (response_data === '2'){
        	if($("#isRelease").text() === "已发布"){
	        	$("#isRelease").attr("class", "am-topbar-btn am-btn am-btn-danger");
	            $("#isRelease").text("未发布");
        	}
            if($("#hasUpdate").text() === "有更新"){
	            $("#hasUpdate").attr("class", "am-topbar-btn am-btn am-btn-danger");
	            $("#hasUpdate").text("无更新");
            }	
        }
        else{
        	if($("#isRelease").text() === "未发布"){
	            $("#isRelease").attr("class", "am-topbar-btn am-btn am-btn-primary");
	            $("#isRelease").text("已发布");
	            $("#releaseButton").text("更新发布");
        	}
        	if($("#hasUpdate").text() === "有更新"){
	            $("#hasUpdate").attr("class", "am-topbar-btn am-btn am-btn-danger");
	            $("#hasUpdate").text("无更新");  
	        }
        }
	});
}

function isChangingTag(obj){
	current_pos = getCursortPosition(obj);
	s = obj.value;
	tag_row_start = s.indexOf("标签:");
	substr = s.substring(tag_row_start, current_pos);
	if(substr.indexOf("\n") === -1){
		return 1
	}
	else
	{
		return 0
	}
}

//
// get Tag
//
function getTag(text){

	var text_tmp_index  = text.indexOf("标签:"); //get 2th  row index
	
	if(text_tmp_index !== -1){
		var text_tmp = text.substring(text_tmp_index, text.length); //get text except first row
		
		var tag_row = text_tmp.substring(0, text_tmp.indexOf("\n")); //get row include tag
		
		text_tmp_index = text_tmp.indexOf(":") + 1;  
		//get pre tag string
		text_tmp = text_tmp.substring(text_tmp_index, text_tmp.indexOf("\n")); 
		//get pre tag array (include space)
		var pre_tag = text_tmp.split(" ");
		var _tag = new Array();
		var index = 0;
		for (i in pre_tag){
			if(pre_tag[i] !== "" && _tag.indexOf(pre_tag[i]) === -1){
				_tag[index] = pre_tag[i];
				index += 1;
			}
		}
		if(tag.length === 0 || tag !== _tag){
			tag = _tag;
			console.log(tag);
			return tag_row
		}
		else{
			return ""
		}
	}
}

//set tag on preview page

function setTag(text){
	var tag_row = "\n";
	if(tag.length === 0){
		tag[0] = "未分类";	
	}
	for (i in tag){
		var b = new Base64();
		var str = b.encode(tag[i]);
		tag_row += '<a href="/tag/' + str + '.html " class="tagClick" target="_blank"><code>';
		tag_row += tag[i];
		tag_row += "</code></a>";
		tag_row += " ";
	}
	tag_row += "\n";
	var first_row = text.substring(0, text.indexOf("</h1>") + 5);
	var other_rows = text.substring(text.indexOf("</h1>") + 6, text.length);
	text = "";
	text += first_row;
	
	text += tag_row;
	console.log(text);
	text += other_rows;
	return text
}


//
//	Conversion
//

function convertText() {
	// get input text
	var text = inputPane.value;
	
	// if there's no change to input, cancel conversion
	if (text && text == lastText) {
		return;
	} else {
		lastText = text;
	}

	var tag_row = getTag(text);
	text = text.replace(tag_row, "");

	var startTime = new Date().getTime();
	
	// Do the conversion

	text = converter.makeHtml(text);
	text = setTag(text);
	// display processing time
	var endTime = new Date().getTime();	
	processingTime = endTime - startTime;
	document.getElementById("processingTime").innerHTML = processingTime+" ms";

	// save proportional scroll positions
	saveScrollPositions();

	// update right pane
	if (paneSetting.value == "outputPane") {
		// the output pane is selected
		outputPane.value = text;
	} else if (paneSetting.value == "previewPane") {
		// the preview pane is selected
		previewPane.innerHTML = text;
		codeHighlight();
	}

	lastOutput = text;

	// restore proportional scroll positions
	restoreScrollPositions();
};


//
//	Event handlers
//

function onConvertTextSettingChanged() {
	// If the user just enabled automatic
	// updates, we'll do one now.
	onInput();
}

function onConvertTextButtonClicked() {
	// hack: force the converter to run
	lastText = "";

	convertText();
	inputPane.focus();
}

function onPaneSettingChanged() {
	previewPane.style.display = "none";
	outputPane.style.display = "none";
	syntaxPane.style.display = "none";

	// now make the selected one visible
	top[paneSetting.value].style.display = "block";

	lastRoomLeft = 0;  // hack: force resize of new pane
	setPaneHeights();

	if (paneSetting.value == "outputPane") {
		// Update output pane
		outputPane.value = lastOutput;
	} else if (paneSetting.value == "previewPane") {
		// Update preview pane
		previewPane.innerHTML = lastOutput;
	}
}

function onInput() {
// In "delayed" mode, we do the conversion at pauses in input.
// The pause is equal to the last runtime, so that slow
// updates happen less frequently.
//
// Use a timer to schedule updates.  Each keystroke
// resets the timer.

	// if we already have convertText scheduled, cancel it
	if (convertTextTimer) {
		window.clearTimeout(convertTextTimer);
		convertTextTimer = undefined;
	}

	if (convertTextSetting.value != "manual") {
		var timeUntilConvertText = 0;
		if (convertTextSetting.value == "delayed") {
			// make timer adaptive
			timeUntilConvertText = processingTime;
		}

		if (timeUntilConvertText > maxDelay)
			timeUntilConvertText = maxDelay;

		// Schedule convertText().
		// Even if we're updating every keystroke, use a timer at 0.
		// This gives the browser time to handle other events.
		convertTextTimer = window.setTimeout(convertText,timeUntilConvertText);
	}
}

//
// code highlight
//
function codeHighlight(){
	$('pre code').each(function(i, block) {
            // console.log(block.className);
            if(block.className === ""){
                hljs.highlightBlock(block);
                // console.log(block);
            }
		});	
}

//
// Smart scrollbar adjustment
//
// We need to make sure the user can't type off the bottom
// of the preview and output pages.  We'll do this by saving
// the proportional scroll positions before the update, and
// restoring them afterwards.
//

var previewScrollPos;
var outputScrollPos;

function getScrollPos(element) {
	// favor the bottom when the text first overflows the window
	if (element.scrollHeight <= element.clientHeight)
		return 1.0;
	return element.scrollTop/(element.scrollHeight-element.clientHeight);
}

function setScrollPos(element,pos) {
	element.scrollTop = (element.scrollHeight - element.clientHeight) * pos;
}

function saveScrollPositions() {
	previewScrollPos = getScrollPos(previewPane);
	outputScrollPos = getScrollPos(outputPane);
}

function restoreScrollPositions() {
	// hack for IE: setting scrollTop ensures scrollHeight
	// has been updated after a change in contents
	previewPane.scrollTop = previewPane.scrollTop;

	setScrollPos(previewPane,previewScrollPos);
	setScrollPos(outputPane,outputScrollPos);
}

//
// Textarea resizing
//
// Some browsers (i.e. IE) refuse to set textarea
// percentage heights in standards mode. (But other units?
// No problem.  Percentage widths? No problem.)
//
// So we'll do it in javascript.  If IE's behavior ever
// changes, we should remove this crap and do 100% textarea
// heights in CSS, because it makes resizing much smoother
// on other browsers.
//

function getTop(element) {
	var sum = element.offsetTop;
	while(element = element.offsetParent)
		sum += element.offsetTop;
	return sum;
}

function getElementHeight(element) {
	var height = element.clientHeight;
	if (!height) height = element.scrollHeight;
	return height;
}

function getWindowHeight(element) {
	if (window.innerHeight)
		return window.innerHeight;
	else if (document.documentElement && document.documentElement.clientHeight)
		return document.documentElement.clientHeight;
	else if (document.body)
		return document.body.clientHeight;
}

function setPaneHeights() {
    var textarea  = inputPane;
	var footer = document.getElementById("footer");

	var windowHeight = getWindowHeight();
	var footerHeight = getElementHeight(footer);
	var textareaTop = getTop(textarea);

	// figure out how much room the panes should fill
	var roomLeft = windowHeight - footerHeight - textareaTop;

	if (roomLeft < 0) roomLeft = 0;

	// if it hasn't changed, return
	if (roomLeft == lastRoomLeft) {
		return;
	}
	lastRoomLeft = roomLeft;

	// resize all panes
	inputPane.style.height = roomLeft + "px";
	previewPane.style.height = roomLeft + "px";
	outputPane.style.height = roomLeft + "px";
	syntaxPane.style.height = roomLeft + "px";
}


/**
*
*  Base64 encode / decode
*
*  @author haitao.tu
*  @date   2010-04-26
*  @email  tuhaitao@foxmail.com
*
*/
 
function Base64() {
 
	// private property
	_keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
 
	// public method for encoding
	this.encode = function (input) {
		var output = "";
		var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
		var i = 0;
		input = _utf8_encode(input);
		while (i < input.length) {
			chr1 = input.charCodeAt(i++);
			chr2 = input.charCodeAt(i++);
			chr3 = input.charCodeAt(i++);
			enc1 = chr1 >> 2;
			enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
			enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
			enc4 = chr3 & 63;
			if (isNaN(chr2)) {
				enc3 = enc4 = 64;
			} else if (isNaN(chr3)) {
				enc4 = 64;
			}
			output = output +
			_keyStr.charAt(enc1) + _keyStr.charAt(enc2) +
			_keyStr.charAt(enc3) + _keyStr.charAt(enc4);
		}
		return output;
	}
 
	// public method for decoding
	this.decode = function (input) {
		var output = "";
		var chr1, chr2, chr3;
		var enc1, enc2, enc3, enc4;
		var i = 0;
		input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");
		while (i < input.length) {
			enc1 = _keyStr.indexOf(input.charAt(i++));
			enc2 = _keyStr.indexOf(input.charAt(i++));
			enc3 = _keyStr.indexOf(input.charAt(i++));
			enc4 = _keyStr.indexOf(input.charAt(i++));
			chr1 = (enc1 << 2) | (enc2 >> 4);
			chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
			chr3 = ((enc3 & 3) << 6) | enc4;
			output = output + String.fromCharCode(chr1);
			if (enc3 != 64) {
				output = output + String.fromCharCode(chr2);
			}
			if (enc4 != 64) {
				output = output + String.fromCharCode(chr3);
			}
		}
		output = _utf8_decode(output);
		return output;
	}
 
	// private method for UTF-8 encoding
	_utf8_encode = function (string) {
		string = string.replace(/\r\n/g,"\n");
		var utftext = "";
		for (var n = 0; n < string.length; n++) {
			var c = string.charCodeAt(n);
			if (c < 128) {
				utftext += String.fromCharCode(c);
			} else if((c > 127) && (c < 2048)) {
				utftext += String.fromCharCode((c >> 6) | 192);
				utftext += String.fromCharCode((c & 63) | 128);
			} else {
				utftext += String.fromCharCode((c >> 12) | 224);
				utftext += String.fromCharCode(((c >> 6) & 63) | 128);
				utftext += String.fromCharCode((c & 63) | 128);
			}
 
		}
		return utftext;
	}
 
	// private method for UTF-8 decoding
	_utf8_decode = function (utftext) {
		var string = "";
		var i = 0;
		var c = c1 = c2 = 0;
		while ( i < utftext.length ) {
			c = utftext.charCodeAt(i);
			if (c < 128) {
				string += String.fromCharCode(c);
				i++;
			} else if((c > 191) && (c < 224)) {
				c2 = utftext.charCodeAt(i+1);
				string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
				i += 2;
			} else {
				c2 = utftext.charCodeAt(i+1);
				c3 = utftext.charCodeAt(i+2);
				string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
				i += 3;
			}
		}
		return string;
	}
}
