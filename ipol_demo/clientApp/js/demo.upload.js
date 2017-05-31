var clientApp = clientApp || {};
var helpers = clientApp.helpers || {};
var upload = upload || {};
var editor = editor || {};
var uploadedFiles = {};

clientApp.upload = upload;

var _URL = window.URL || window.webkitURL;
var demoInfo = helpers.getFromStorage("demoInfo");

clientApp.upload.getUploadedFiles = function() {
  return uploadedFiles;
};

// Upload dialog initialization.
$(".upload-dialog").dialog({
  autoOpen: false,
  width: 1100,
  maxHeight: 500,
  modal: true,
  // Click outside of dialog to close
  open: function() {
    $('.ui-widget-overlay').bind('click', function() {
      $('.upload-dialog').dialog('close');
    })
  },
  buttons: {
    Apply: function() {
      if (checkRequiredInputs()) {
        $(this).dialog("close");
        helpers.setOrigin("upload");
        editor.printEditor();
        parameters.printParameters();
      }
    },
    Clear: function() {
      clearUploads();
    },
    Cancel: function() {
      $(this).dialog("close");
    }
  },
    create:function () {
      $('.ui-dialog-buttonset').children().removeClass('ui-button ui-corner-all ui-widget');
      $('.ui-dialog-buttonset').children().addClass('btn');
    }
});

$(".upload-btn").click(function() {
  $(".upload-dialog").dialog("open");
});

// Print uploads dialog.
upload.printUploads = function(inputs) {
  var uploadMaxSize = 0;
  for (var i = 0; i < inputs.length; i++) {
    var input = inputs[i];
    var inputType = input.type;
    var input_weight = eval(input.max_weight) / 1024 / 1024;
    uploadMaxSize += input_weight;
    $(".upload-dialog").append("<div class=input-upload-" + i + "></div>");
    var uploadRow = $(".input-upload-" + i);
    var uploadRowArray = [];
    uploadRow.addClass("upload-row");
    uploadRowArray += "<span class=upload-description> <b>" + input.description + "</b> File type: " + inputType + "</span>";
    uploadRowArray += "<input type=file id=file-" + i + " name=upload-" + i + " class=upload-btn-" + i + " accept=";
    uploadRowArray += (inputType == "video") ? inputType + '/*,video/mp4,video/x-m4v />' : inputType + "/* />";
    uploadRowArray += "<img id=upload-thumbnail-" + i + " src=# />";
    uploadRowArray += "<span class=upload-resolution-" + i + ">" + getMaxPixels(input) + getMaxWeight(input_weight) + "</span>";
    uploadRow.html(uploadRowArray);
    $(".input-upload-" + i).children().addClass("upload-element m-x-10");
    appendRequired(input, i);
    addInputListener(i);
  }
  printUploadFooter(uploadMaxSize);
}

// Get input max pixels.
function getMaxPixels(input) {
  if (!input.max_pixels) {
    return "";
  } else {
    return "&le; " + (eval(input.max_pixels) / 1000000).toFixed(2) + " Mpx. ";
  }
}

// Get input max weight.
function getMaxWeight(weight) {
  if (!weight) {
    return "";
  } else {
    return "&le; " + Math.round(weight) + " Mb";
  }
}

// Add required or optional to input.
function appendRequired(input, index) {
  var required = $(".upload-resolution-" + index);
  if (input.required || typeof(input.required) == 'undefined') {
    required.append(document.createTextNode(" (Required)"));
  } else if (!input.required) {
    required.append(document.createTextNode(" (Optional)"));
  }
}

// Add event to upload files.
function addInputListener(index) {
  document.getElementById("file-" + index).addEventListener('change', function(event) {
    var file = $("#file-" + index)[0].files[0];

    if (file.type.split('/')[0] == "image") uploadImg(index, event);
    else upload(index, event);

  });
}

// if it's an Image, first of all it needs to convert the "file" to img to check resolution and upload it.
function uploadImg(index, event) {
  demoInfo = helpers.getFromStorage("demoInfo");
  var file = $("#file-" + index)[0].files[0];
  var inputKey = document.getElementById("file-" + index).name.split('-')[1];
  var maxPixels = eval(demoInfo.inputs[inputKey].max_pixels);
  var img = new Image();
  img.onload = function() {
    var uploadImgPixels = this.width * this.height;
    if (uploadImgPixels > maxPixels) {
      clearUploadInput(inputKey);
      alert("File upload resolution limit reached");
    } else{
      upload(index, event);
    }
  };
  img.src = _URL.createObjectURL(file);
}

// Upload the current Input
function upload(index, event) {
  demoInfo = helpers.getFromStorage("demoInfo");
  var file = $("#file-" + index)[0].files[0];
  var inputs = demoInfo.inputs;
  var inputKey = document.getElementById("file-" + index).name.split('-')[1];
  var maxWeight = demoInfo.inputs[inputKey].max_weight;
  if ($("#file-" + index)[0].files[0].size < eval(maxWeight) && file) {
    var format = file.type.split('/')[0];
    if (format == 'image') addThumbnail(event);
    blob = new Blob([file], {
      type: file.type
    });
    // onload needed since Google Chrome doesn't support addEventListener for FileReader
    var fileReader = new FileReader();
    fileReader.onload = function(evt) {
      var inputName = inputs[index].description;
      uploadedFiles[index] = {
        blob: evt.target.result,
        format: format,
        thumbnail: ""
      };
    };
    fileReader.readAsDataURL(blob);
  } else {
    clearUploadInput(inputKey);
    alert("File upload size limit reached");
  }
}

function addThumbnail(data) {
  var id = data.target.id;
  var file = id.split("-");
  id = "upload-thumbnail-" + file[1];
  if (data.target.files) {
    var FR = new FileReader();
    FR.addEventListener("load", function(e) {
      document.getElementById(id).style.display = "inline";
      document.getElementById(id).src = e.target.result;
    });
    FR.readAsDataURL(data.target.files[0]);
  }
}

// Check if all required inputs are uploaded before continue.
function checkRequiredInputs() {
  var inputs = demoInfo.inputs;
  var upload;
  for (var i = 0; i < inputs.length; i++) {
    upload = $("#file-" + i);
    var file = upload[0].files[0];
    if ((inputs[i].required || typeof(inputs[i].required) == 'undefined') && !file) {
      alert("Please upload all required files.");
      return false;
    }
  }
  return true;
}

// Print upload dialog footer.
function printUploadFooter(size) {
  var uploadDialog = $(".upload-dialog");
  uploadDialog.append("<p>Upload size is limited to <b>" + Math.round(size) + "MB</b> for the whole upload set.</p>");
  uploadDialog.append("<p>The uploaded will be publicly archived unless you switch to private mode on the result page.</p>");
  uploadDialog.append("<p>Only upload <a href=\"https://tools.ipol.im/wiki/ref/demo_input/\">suitable images</a>. See the <a href=\"https://tools.ipol.im/wiki/ref/demo_input/\">copyright and legal conditions</a> for details.</p>");
}

// Clear inputs.
function clearUploads() {
  var inputs = demoInfo.inputs;
  var imgElement;
  for (var i = 0; i < inputs.length; i++) {
    imgElement = $("#upload-thumbnail-" + i);
    imgElement.attr("src", "#");
    imgElement.css("display", "none");
    $("#file-" + i).val("");
    helpers.removeItem(inputs[i].description);
  }
  helpers.removeItem("origin");
}

// Clear inputs.
function clearUploadInput(id) {
  var inputs = demoInfo.inputs;
  var imgElement = $("#upload-thumbnail-" + id);
  imgElement.attr("src", "#");
  imgElement.css("display", "none");
  $("#file-" + id).val("");
  helpers.removeItem(inputs[id].description);
  helpers.removeItem("origin");
}
