var form_fill = {};
var count = 0;

var casper = require('casper').create({
    clientScripts: ['jquery.min.js'],
    pageSettings:{
        loadImages: false,
        loadPlugins: false,
        loadPlugins: false,
        localToRemoteUrlAccessEnabled: true
    },
    // onAlert: function(msg){
    //     console.log(msg);
    // },
    onResourceRequested: function(){
        count = count + 1;
        console.log(arguments[1]['method'] + ": " + arguments[1]['url']);
    },
    verbose: true,
    // logLevel: 'debug',
    safeLogs: false
});
var rootUrl = casper.cli.raw.get('root_url');

casper.start(rootUrl);
casper.then(function() {    //get forms' info(include all input name and value)
    var forms = [];
    forms = this.evaluate(getForms);
    for (var i=0; i<forms.length; i++){
        var form_id = forms[i];
        var input_info = this.evaluate(function(form_id) {
            var selectorString = "#" + form_id;
            var inputFields = $(selectorString).find("input");  //get input which in form
            var input_dicts = {};
            
            for (var i=0;i<inputFields.length;i++){
                if(inputFields[i].getAttribute('name')){
                    if(inputFields[i].getAttribute('value')){
                        input_dicts[inputFields[i].getAttribute('name')] = inputFields[i].getAttribute('value');
                    }
                    else{
                        input_dicts[inputFields[i].getAttribute('name')] = "";
                    }
                }
            }//get and set inputs' value 

            return input_dicts;
        }, form_id);
        form_fill[form_id] = input_info;
    }
    for(i in form_fill){
        console.log(i + ":");
         for(item in form_fill[i]){
            console.log("    " + item + ":" + form_fill[i][item]);
         }
    }
});


casper.then(function() { //get link
    var links = [];
    links = this.evaluate(getLinks);
    for(var i=0; i<links.length; i++){
        if(links[i]){
            console.log("New Link: " + links[i]);
        }
    }
    var iframes = [];
    iframes = this.evaluate(getIframes);
    for(var i=0; i<iframes.length; i++){
        if(iframes[i]){
            console.log("New Iframe: " + iframes[i]);
        }
    }
});


casper.then(function() {  // send form 
    console.log("sending start");
    for(form_item in form_fill){
        if(form_item){
            var arg1 = "form#" + form_item;
            console.log(arg1);
            for(item in form_fill[form_item]){
                console.log("    " + item + ":" + form_fill[form_item][item]);
            }
            console.log(JSON.stringify(form_fill[form_item]));
            this.fill(arg1, {"commend":"all",
                            "initiative_id":"tbindexz_20150512",
                            "q":"",
                            "search_type":"item",
                            "sourceId":"tb.index",
                            "spm":"1.7274553.1997520841.1",
                            "ssid":"s5-e"
                    }, true);
        }
    }
    console.log("sending end");
});

casper.then(function() {
    this.evaluateOrDie(function() {
        return /message sent/.test(document.body.innerText);
    }, 'sending message failed');
});

casper.run(function() {
    this.echo('received ' + count + " request");
    this.echo('message sent').exit();
});


function getForms() {
    var forms = document.querySelectorAll('form');
    return Array.prototype.map.call(forms, function(e) {
        return e.getAttribute('id');
    });
}

function getLinks() {
    var links = document.querySelectorAll('a');
    return Array.prototype.map.call(links, function(e) {
        return e.getAttribute('href');
    });
}

function getIframes() {
    var iframes = document.querySelectorAll('iframe');
    return Array.prototype.map.call(iframes, function(e) {
        return e.getAttribute('src');
    });
}

// casper.on('remote.message', function(msg) {
//     this.echo("evaluete message:" + msg);
// });

