
// using strict mode: better compatibility
"use strict";



//------------------------------------------------------------------------------
// preprocess DDL demo, filling some properties:
//   input.max_pixels if string
//   input.max_weight if string
// default values for:
//   general.crop_maxsize
//   general.thumbnail_size
// set array of strings if single string for
//   general.input_description
//   general.param_description
// default value for 
//    params_layout
// 
function PreprocessDemo(demo) {
    //
//     console.info("PreprocessDemo")
//     console.info(demo)
    if (demo != undefined) {
        for (var idx=0; idx<demo.inputs.length;idx++) {
            // do some pre-processing
            if ($.type(demo.inputs[idx].max_pixels) === "string") {
                demo.inputs[idx].max_pixels = eval(demo.inputs[idx].max_pixels);
            }
            if ($.type(demo.inputs[idx].max_weight) === "string") {
                demo.inputs[idx].max_weight = eval(demo.inputs[idx].max_weight);
            }
        }
    }
    //

    if (demo.general.crop_maxsize == undefined) {
        // setting the crop_maxsize string to a non integer value with 
        // disable its behavior, so no limit by default
        demo.general.crop_maxsize = "NaN";
    }

    if (demo.general.thumbnail_size == undefined) {
        demo.general.thumbnail_size = 128;
    }

    if ($.type(demo.general.input_description) === "string") {
        demo.general.input_description = [demo.general.input_description];
    }
    if ($.type(demo.general.param_description) === "string") {
        demo.general.param_description = [demo.general.param_description];
    }

    // create default params_layout property if it is not defined
    if (demo.params&&(demo.params_layout == undefined)) {
        if (demo.params!=undefined) {
            demo.params_layout = [
                ["Parameters:", range(demo.params.length)]
            ];
        }
    }
};






//------------------------------------------------------------------------------
function OnDemoList(demolist)
{
    
    //--------------------------------------------------------------------------
    this.InfoMessage = function( ) {
        if (this.verbose) {
            var args = [].slice.call( arguments ); //Convert to array
            args.unshift("---- OnDemoList ----");
            console.info.apply(console,args);
        }
    }
    this.verbose=false;
    
    var dl = demolist;
    if (dl.status == "OK") {
        var str = JSON.stringify(dl.demo_list, undefined, 4);
//         $("#tabs-demos pre").html(syntaxHighlight(str))
        this.InfoMessage("demo list is ",dl);
    }


    // get url parameters (found on http://stackoverflow.com/questions/901115/how-can-i-get-query-string-values-in-javascript/21152762#21152762)
    var url_params = {};
    this.InfoMessage("*** OnDemoList location.search=",location.search);
    location.search.substr(1).split("&").forEach(function(item) {
        var s = item.split("="),
            k = s[0],
            v = s[1] && decodeURIComponent(s[1]);
        (k in url_params) ? url_params[k].push(v) : url_params[k] = [v]
    })
    this.InfoMessage("url parameters = ",url_params);
    
    
    if (url_params["id"]!=undefined) {
        var demo_id = url_params["id"][0];
        this.InfoMessage("demo_id = ", demo_id);
    }
    
    // create a demo selection
    var html_selection = "<select id='demo_selection'>";
    var demo_pos = -1;
    for (var i=0; i<dl.demo_list.length; i++) {
        if (dl.demo_list[i].editorsdemoid==demo_id) {
            this.InfoMessage("found demo id at position ", i);
            demo_pos=i;
        }
        html_selection += '<option value = "'+i+'">'
        html_selection += dl.demo_list[i].editorsdemoid + 
                          '  '+ dl.demo_list[i].title
        
        html_selection += '</option>'
    }
    html_selection += "</select>";
    $("#demo-select").html(html_selection);
    
    if (demo_pos!=-1) {
        $("#demo_selection").val(demo_pos);
        InputController(dl.demo_list[demo_pos].editorsdemoid,
                        dl.demo_list[demo_pos].id,
                        demo_origin.url
                       );
    }

    
    $("#demo-select").data("demo_list",dl.demo_list);
    $("#demo-select").change(
        function() {
            var pos =$( "#demo-select option:selected" ).val();
            InputController(dl.demo_list[pos].editorsdemoid,
                            dl.demo_list[pos].id,
                            demo_origin.select_widget
                           );
        });
    

};

//------------------------------------------------------------------------------
// List all demos and select one
//
function ListDemosController() {
    
//     console.info("get demo list from server");
    var dl;

    ModuleService(
        'demoinfo',
        'demo_list',
        '',
        OnDemoList
    );
    
    
};



var demo_origin =  {  select_widget:0, url:1, browser_history:2};


//------------------------------------------------------------------------------
// set the demo page based on the archive experiment information
function SetArchiveExperiment(ddl_json, experiment) {
    
    // do as if data is being uploaded
    // fill upload areas with image sources
    // look for input files 
    var archive_input_description = [];
    var archive_input_url         = [];
    var found_inputs=0;
    var nb_inputs = ddl_json.inputs.length;
    
    for(var i=0;i<nb_inputs;i++) {
        // check input_XX.ext
        // check filename to look for in archive description
        var filename = "input_"+i+ddl_json.inputs[i].ext;
        archive_input_url[i] = ArchiveDisplay.find_archive_url(
            filename, ddl_json.archive.files, experiment.files);
        // check input_XX.orig.ext
        if (!archive_input_url[i]) {
            // check filename to look for in archive description
            var filename = "input_"+i+'.orig.png';
            archive_input_url[i] = ArchiveDisplay.find_archive_url(
                filename, ddl_json.archive.files, experiment.files);
        }
        // check input_XX.sel.ext
        // TODO: if we choose .sel then the possible crop is already applied ...
        if (!archive_input_url[i]) {
            // check filename to look for in archive description
            var filename = "input_"+i+'.sel.png';
            archive_input_url[i] = ArchiveDisplay.find_archive_url(
                filename, ddl_json.archive.files, experiment.files);
        }
        if (archive_input_url[i]||(ddl_json.inputs[i].required===false)) {
            // count it as found this it is not required
            found_inputs++;
        }
    }
    
    // on everything loaded, set the inputs
    function SetInputs() {
        var di = new DrawInputs(ddl_json);
        console.info("apply_local_data ", ddl_json);
        di.SetBlobSet(null);
        di.CreateHTML();
        //di.CreateCropper();
        di.LoadDataFromLocalFiles();
        di.SetRunEvent();
    }
    
    
    if (found_inputs==nb_inputs) {
        var total_loaded_images = 0;
        // set uploaded files
        for(var i=0;i<nb_inputs;i++) {
            if (archive_input_url[i]) {
                var im = new Image();
                im.crossOrigin = "Anonymous";
                im.onload = function() { 
                    total_loaded_images++;
                    if (total_loaded_images==nb_inputs) {
                        SetInputs();
                    }
                };
                im.src = archive_input_url[i];
                $('#localdata_preview_'+i).attr("src", im.src);
            } else {
                // optional inputs, counted as loaded
                total_loaded_images++;
                if (total_loaded_images==nb_inputs) {
                    SetInputs();
                }
            }
        }
    }
        
    // Set parameter values
    SetParamValues(experiment.results.params);
    
    // Draw results
    //if ($("#DrawInputs").data("draw_inputs")) {
    //    $("#DrawInputs").data("draw_inputs").ResultProgress(res);
    //}
    var dr = new DrawResults( experiment.results, ddl_json.results );
    // Telling the DrawResults object that we are drawing results from 
    // an experiment so it can search the urls from archive
    dr.SetExperiment(experiment,ddl_json.archive);
    dr.Create();
}

//------------------------------------------------------------------------------
// Starts everything needed for demo input tab
// origin is of enum type demo_origin
//
function InputController(demo_id,internal_demoid,origin,func) {
    
    if (origin===undefined) {
        origin=demo_origin.select_widget;
    }

//     console.info("internal demo id = ", internal_demoid);
    if (internal_demoid > 0) {
        ModuleService(
            'demoinfo',
            'read_last_demodescription_from_demo',
            'demo_id=' + internal_demoid + '&returnjsons=True',
            function(demo_ddl) {
                //console.info("read demo ddl status = ", demo_ddl.status);
                
                // empty inputs
                $("#DrawInputs").empty();
                $("#DrawInputs").removeData();
                
                // empty results
                $("#ResultsDisplay").empty();
                $("#ResultsDisplay").removeData();
                
                if (demo_ddl.status == "OK") {
                    var ddl_json = DeserializeJSON(demo_ddl.last_demodescription.json);
                    var str = JSON.stringify(ddl_json, undefined, 4);
                    $("#tabs-ddl pre").html(syntaxHighlight(str));
                } else {
                    console.error(" --- failed to read DDL");
                }
                
                // update document title
                //$(document).attr("title","IPOL Journal &middot; "+ddl_json.general.demo_title);
                $('title').html("IPOL Journal &middot; "+ddl_json.general.demo_title);

                // for convenience, add demo_id field to the json DDL 
                ddl_json['demo_id'] = demo_id
                PreprocessDemo(ddl_json);
                
                // hide parameters if none
                if ((ddl_json.params===undefined)||
                    (!(ddl_json.params.length>0))) {
                    $("#parameters_fieldset").hide();
                } else {
                    $("#parameters_fieldset").show();
                }
                //console.info("pd = ",ddl_json.general.param_description);
                if ((ddl_json.general.param_description != undefined) &&
                    (ddl_json.general.param_description != "")&&
                    (ddl_json.general.param_description != [""]))
                {
                    $("#description_params").show();
                } else {
                    $("#description_params").hide();
                }

                var has_inputs = (ddl_json.inputs!==undefined)&&(ddl_json.inputs.length>0);
                if (has_inputs) {
                    // ensure inputs fieldsets are shown 
                    $("#selectinputs_fieldset").show();
                    $("#inputs_fieldset"      ).show();
                    
                    // disable run
                    $( "#run_button" ).unbind("click").prop("disabled",true);
                    $(".progress-label").text( "Waiting for input selection" );
                    if (ddl_json.general.thumbnail_size!==undefined) {
                        $("#ThumbnailSize").val(ddl_json.general.thumbnail_size);
                    } else {
                        $("#ThumbnailSize").val(128);
                    }
                    if ((ddl_json.general.input_description != undefined) &&
                        (ddl_json.general.input_description != "")&&
                        (ddl_json.general.input_description != [""]))
                    {
                        $("#InputDescription").html(joinHtml(ddl_json.general.input_description));
                        $("#description_input").show();
                    } else {
                        $("#description_input").hide();
                    }
                    // Create local data selection to upload 
                    CreateLocalData(ddl_json);

                } else {
                    $( "#run_button" ).unbind("click").prop("disabled",true);
                    $(".progress-label").text( "Run" );
                    $("#selectinputs_fieldset").hide();
                    $("#inputs_fieldset"      ).hide();

                    var di = new DrawInputs(ddl_json);
                    di.input_origin = "noinputs";
                    di.SetRunEvent();
                }
                
                // Create Parameters tab
                CreateParams(ddl_json);

                // Get demo blobs
                ModuleService(
                    "blobs",
                    "get_blobs_of_demo_by_name_ws",
                    "demo_name=" + demo_id,
                    OnDemoBlobs(ddl_json));
                
                // Display archive information
                var ar = new ArchiveDisplay();
                ar.get_archive(demo_id,1);

                if (demo_ddl.status == "OK") {
                    switch(origin) {
                        case demo_origin.select_widget:
                            // !from_url mean the event is from changing the demo id
                            try {
                                // change url hash
                                History.pushState({demo_id:demo_id,state:1}, 
                                "IPOL Journal - "+ddl_json.general.demo_title,
                                //"IPOLDemos "+demo_id+" inputs", 
                                "?id="+demo_id+"&state=1");
                            } catch(err) {
                                console.error("error:", err.message);
                            }
                            break;
                        case demo_origin.url:
                            // check if result to display
                            var url_params = {};
                            location.search.substr(1).split("&").forEach(function(item) {
                                var s = item.split("="),
                                    k = s[0],
                                    v = s[1] && decodeURIComponent(s[1]);
                                (k in url_params) ? url_params[k].push(v) : url_params[k] = [v]
                            });
                            // set results as url parameters
                            if (url_params["res"]!==undefined) {
                                var res = JSON.parse(url_params["res"]);
                                console.info("***** demo results obtained from url parameters");
                                // Set parameter values
                                SetParamValues(res.params);
                                // Draw results
                                if ($("#DrawInputs").data("draw_inputs")) {
                                    $("#DrawInputs").data("draw_inputs").ResultProgress(res);
                                }
                                var dr = new DrawResults( res, ddl_json.results );
                                dr.Create();
                                //$("#progressbar").get(0).scrollIntoView();
                            }
                            // set experiment id as url parameter
                            if (url_params["exp"]!=undefined) {
                                var exp_id = url_params["exp"][0];
                                console.info("demo experiment = ", exp_id);
                                // ask archive about this experiment
                                var url_params =    'demo_id='    + demo_id + '&id_experiment='+exp_id;
                                ModuleService("archive","get_experiment",url_params,
                                    function(res) {
                                        console.info("archive get_experiment result : ",res);
                                        if (res['status']==='OK') {
                                            SetArchiveExperiment(ddl_json, res.experiment);
                                        }
                                    }.bind(this));
                            }
                            
                            break;
                        case demo_origin.browser_history:
                            if (func!=undefined) {
                                func();
                            }
                            break;
                    }
                }
                
            });


    }
    

}
    
    

//------------------------------------------------------------------------------
// allow folding/unfolding of legends
//
function SetLegendFolding( selector) {
    
    // Set cursor to pointer and add click function
    $(selector).css("cursor","pointer").click(function(){
        var legend = $(this);
        var value = $(this).children("span").html();
        if(value=="[-]")
            value="[+]";
        else
            value="[-]";
       $(this).siblings().slideToggle("slow", function() { legend.children("span").html(value); } );
    });
}    
    

    
//------------------------------------------------------------------------------
// Starts processing when document is ready
//

function DocumentReady() {

    // be sure to have string function endsWith
    if (typeof String.prototype.endsWith !== 'function') {
        String.prototype.endsWith = function(suffix) {
            return this.indexOf(suffix, this.length - suffix.length) !== -1;
        };
    }

    $("#tabs").tabs({
            // update archive tab when selected
            beforeActivate: function(event, ui) {
                if (ui.newPanel.is("#tabs-archive")) {
                    var ar = new ArchiveDisplay();
                    // we need the demo_id here
                    var demo_list = $("#demo-select").data("demo_list");
                    if (demo_list) {
                        var pos =$( "#demo-select option:selected" ).val();
                        ar.get_archive(demo_list[pos].editorsdemoid,1);
                    }
                }
            }
        }

    );

    $( "#progressbar" ).progressbar({ value:100 });
    $(".progress-label").text( "Waiting for input selection" );

    SetLegendFolding("legend");
    $("#reset_params").unbind();
    $("#reset_params").click( function() {
        console.info("reset params clicked");
        ResetParamValues();
    }
    );
    
    // parameters description dialog
    var param_desc_dialog;
    param_desc_dialog = $("#ParamDescription").dialog({
        autoOpen: false,
        // height: 500,
        width: 800,
        modal: true,
    });
    
    $("#description_params").button().on("click", 
        function() 
        { 
            param_desc_dialog.dialog("open");
        });

    // input description dialog
    var input_desc_dialog;
    input_desc_dialog = $("#InputDescription").dialog({
        autoOpen: false,
        // height: 500,
        width: 800,
        modal: true,
    });
    
    $("#description_input").button().on("click", 
        function() 
        { 
            input_desc_dialog.dialog("open");
        });

    // upload modal dialog
    var dialog;
    dialog = $("#upload-dialog").dialog({
        autoOpen: false,
        height: 500,
        width: 800,
        modal: true,
        buttons: {
            Cancel: function() {
            dialog.dialog( "close" );
            }
        },
//         close: function(event, ui) {
//             $(this).empty().dialog('destroy');
//         }
    });
    
    // adjusting width of display blobs div
    var displayblobs_parent = $("#displayblobs").parent();
    var to_deduce = displayblobs_parent.outerWidth(true)-displayblobs_parent.width();
    $("#displayblobs").width($("#tabs-run").width()-to_deduce);
    
    $( window ).resize(function() {
        var displayblobs_parent = $("#displayblobs").parent();
        var to_deduce = displayblobs_parent.outerWidth(true)-displayblobs_parent.width();
        $("#displayblobs").width($("#tabs-run").width()-to_deduce);
    }
    );
    
    $("#upload-data").button().on("click", 
        function() 
        { 
            dialog.dialog("open");
        });

    ListDemosController();

    var History = window.History;
    // Bind to State Change
    History.Adapter.bind(window,'statechange',
        function(p){ // Note: We are using statechange instead of popstate
            console.info(" statechange param:",p);
            console.info("last_uploaded_files:",last_uploaded_files);
            // Log the State
            var State = History.getState(); 
            // Note: We are using History.getState() instead of event.state
            SetPageState(State.data);
        });

}
$(document).ready(DocumentReady);