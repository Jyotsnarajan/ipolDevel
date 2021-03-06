var helpers = clientApp.helpers || {};

$.fn.gallery = function (result, index) {
  if (result.visible) {
    var visible = eval(result.visible);
    if (!visible) return;
  }

  var contentKeys = Object.keys(result.contents);

  if (result.label) $(this).appendLabel(result.label);
  var gallerySelector = "gallery-" + index;
  $(this).append('<div class="' + gallerySelector + ' gallery-container" ></div>');

  var blobsArray = getGalleryImages(result.contents);

  var leftItems = "gallery-left-items-" + index;
  var rightItems = "gallery-right-items-" + index;
  renderGalleryBlobList(index, contentKeys, result, leftItems, 'left', blobsArray);

  var blobsContainerSelector = "gallery-blobs-container-" + index;
  $("." + gallerySelector).append('<div class="' + blobsContainerSelector + ' blobs-wrapper"></div>');

  renderGalleryBlobList(index, contentKeys, result, rightItems, 'right', blobsArray);
  $("." + rightItems).addClass("gallery-item-list-right di-none");

  var imgContainerLeft = "gallery-blobs-left-" + index;
  var imgContainerRight = "gallery-blobs-right-" + index;
  $("." + blobsContainerSelector).append('<div id="' + imgContainerLeft + '" class=gallery-blob-container></div>');
  $("." + blobsContainerSelector).append('<div id="' + imgContainerRight + '" class="gallery-blob-container di-none"></div>');

  var firstVisibleBlobSet = blobsArray[0];
  for (var i = 0; i < firstVisibleBlobSet.length; i++) {
    $("#" + imgContainerRight).append(firstVisibleBlobSet[i].clone());
    $("#" + imgContainerLeft).append(firstVisibleBlobSet[i].clone());
  }

  var allSrc = getAllSrc(blobsArray);
  $("." + gallerySelector).setGalleryMinHeight(allSrc);
  $(this).append("<div id=gallery-" + index + "-zoom-container></div>");
  $("#gallery-" + index + "-zoom-container").appendZoom(index, leftItems);
  if (blobsArray.length > 1) $("." + leftItems).appendCompare(index, rightItems, imgContainerRight);
}

function getGalleryImages(contentArray) {
  var allSrc = [];
  var keys = Object.keys(contentArray);
  for (var i = 0; i < keys.length; i++) {
    var blobSetContent = contentArray[keys[i]];
    var visibleField = blobSetContent.hasOwnProperty('visible');
    if (!visibleField || (visibleField && eval(blobSetContent.visible))) {
      var imgField = blobSetContent.img;
      var repeat = blobSetContent.repeat !== undefined ? checkRepeat(blobSetContent.repeat) : 1;
      var blobs = [];
      for (var idx = 0; idx < repeat; idx++) {
        blobs = [];
        if (typeof (imgField) === 'string') {
          var img = '<img src=' + getFileURL(imgField.indexOf("'") == -1 ? imgField : eval(imgField)) + ' class=gallery-img draggable=false></img>';
          blobs.push($(img));
        } else if (typeof (imgField) === 'object') {
          for (var k = 0; k < imgField.length; k++) {
            var img = '<img src=' + getFileURL(imgField[k].indexOf("'") == -1 ? imgField[k] : eval(imgField[k])) + ' class=gallery-img draggable=false></img>';
            blobs.push($(img));
          }
        }
        allSrc.push(blobs);
      }
    }
  }
  return allSrc;
}

function getAllSrc(blobsArray) {
  let allSrc = [];
  for (var i = 0; i < blobsArray.length; i++) {
    for (var j = 0; j < blobsArray[i].length; j++) {
      allSrc.push(blobsArray[i][j].attr('src'));
    }
  }
  return allSrc;
}

function checkRepeat(expression) {
  if (expression.indexOf('+') === -1) return parseInt(eval(expression));
  var expressionArray = expression.split('+');
  var repeat = 0;
  for (var i = 0; i < expressionArray.length; i++) {
    repeat += parseInt(eval(expressionArray[i]));
  }
  return repeat;
}

function renderGalleryBlobList(index, contentKeys, result, itemSelector, side, blobsArray) {
  $(".gallery-" + index).append('<div class="' + itemSelector + '"></div>');
  $("." + itemSelector).append('<div id=gallery-' + index + '-blobList-' + side + ' class="gallery-blobList-left gallery-item-list"></div>');
  var contents = result.contents;
  var firstVisibleBlob = true;
  var itemIndex = 0;
  for (let i = 0; i < contentKeys.length; i++) {
    var visibleField = contents[contentKeys[i]].hasOwnProperty('visible');
    if (!visibleField || (visibleField && eval(contents[contentKeys[i]].visible))) {
      var content = result.contents[contentKeys[i]].img;
      if (typeof (content) === 'string') {
        content = [content];
      }
      if (firstVisibleBlob) {
        helpers.addToStorage('gallery-' + index + '-' + side, itemIndex);
        firstVisibleBlob = false;
      }
      var line = contents[contentKeys[i]];
      var repeat = line.repeat != undefined ? checkRepeat(line.repeat) : 1;
      for (var idx = 0; idx < repeat; idx++) {
        var text = getEvalText(contentKeys[i]);
        var spanId = 'gallery-' + index + '-item-' + side + '-' + i + '-' + idx;
        try {
          title = eval(text)
        } catch (err) {
          title = text
        }
        $('#gallery-' + index + '-blobList-' + side).append('<span id=' + spanId + ' class=gallery-item-selector>' + title + '</span>');
        $('#' + spanId).addHoverFeatures(index, side, blobsArray[itemIndex], itemIndex);
        itemIndex++;
      }
    }
  }
  $(this).addMouseOut(index, side, blobsArray);
  $("." + itemSelector + " span:first-child").addClass("gallery-item-selected");
}

$.fn.addMouseOut = function (galleryIndex, side, blobsArray) {
  var selector = '#gallery-blobs-' + side + '-' + galleryIndex;
  $("#gallery-" + galleryIndex + "-blobList-" + side).mouseout(function (event) {
    e = event.toElement || event.relatedTarget;
    if (e != null && (e.parentNode == this || e == this)) {
      return;
    }
    var selectedSrc = helpers.getFromStorage("gallery-" + galleryIndex + "-" + side);
    $(selector).empty();
    var blobs = blobsArray[selectedSrc];
    for (var i = 0; i < blobs.length; i++) {
      $(selector).append(blobs[i].clone());
    }
    $("#gallery-" + galleryIndex + "-zoom > input").adjustSize(galleryIndex);
    $(selector + " > img").addClass('gallery-' + galleryIndex + '-blob-' + side);
    setInterpolation(galleryIndex);
  });
}

function getEvalText(str) {
  if (str.indexOf('+') != -1) {
    return str;
  } else {
    return "\'" + str + "\'";
  }
}

$.fn.addHoverFeatures = function (galleryIndex, side, src, itemIndex) {
  var imgSelector = '.gallery-' + galleryIndex + '-blob-' + side;
  var selector = '#gallery-blobs-' + side + '-' + galleryIndex;
  $(this).mouseover(function () {
    $(selector).empty();
    for (var i = 0; i < src.length; i++) {
      $(selector).append($(src[i]));
    }
    $(selector + " > img").addClass('gallery-' + galleryIndex + '-blob-' + side);
    var zoomValue = $("#gallery-" + galleryIndex + "-zoom > #editor-zoom").val();
    $("#gallery-" + galleryIndex + "-zoom > input").adjustSize(galleryIndex);
    setInterpolation(galleryIndex);
  });
  $(this).on('click', function () {
    var listSelector = ".gallery-" + side + "-items-" + galleryIndex;
    $("#gallery-" + galleryIndex + "-blobList-" + side + " > .gallery-item-selected").toggleClass("gallery-item-selected");
    $(this).toggleClass("gallery-item-selected");
    helpers.addToStorage("gallery-" + galleryIndex + "-" + side, itemIndex);
  });
}

function setInterpolation(galleryIndex) {
  var zoomValue = $("#gallery-" + galleryIndex + "-zoom > #editor-zoom").val();
  helpers.checkInterpolation(zoomValue, ".gallery-" + galleryIndex + " img");
}

$.fn.appendZoom = function (index, leftItems) {
  var zoom = $("#zoom-container").clone();
  zoom.find('input').val('1.0');
  zoom.find('span').html('1x');
  var newZoomID = "gallery-" + index + "-zoom";
  zoom.attr("id", newZoomID).appendTo($(this));
  zoom.removeClass("di-none");
  zoom.show();

  getImagesWidth($("#gallery-blobs-left-" + index).children()).then(imagesTotalWidth => {
    imagesTotalWidth = imagesTotalWidth.reduce((total, num) => total += num);
    imagesContainerWidth = $("#gallery-blobs-left-" + index).width()
    // Fit images size in the container if it's necessary
    if (imagesTotalWidth > imagesContainerWidth) {
      zoomAdjustedValue = ((imagesContainerWidth - $("#gallery-blobs-left-" + index).children().length * 10) / imagesTotalWidth).toFixed(2);
      zoomAdjustedValue = zoomAdjustedValue < 0.25 ? 0.25 : zoomAdjustedValue;
      updateZoomValue(zoom, zoomAdjustedValue);
      $("#" + newZoomID + " > input").adjustSize(index);
    }
  });

  $("#" + newZoomID + " > .zoom-info > #editor-image-size").remove();
  $("#" + newZoomID + " > input").on('input', function () {
    var zoomLevel = $(this).val();
    let selector = ".gallery-" + index + " img";
    helpers.checkInterpolation(zoomLevel, selector);
    $(".gallery-" + index).css({ height: (parseInt($(".gallery-" + index).css('min-height')) || parseInt($(".gallery-" + index).css('height'))) * zoomLevel + "px" });
    $(this).adjustSize(index);
    $("#" + newZoomID + " > .zoom-info > #editor-zoom-value").html(zoomLevel + "x");
  });
  scrollSync(index);
}

function updateZoomValue(zoom, value){
  zoom.find('input').val(value.toString());
  zoom.find('span').html(value.toString() + 'x');
}

// Image properties are only accessible after it's completely loaded.  
function getImageWidthAfterLoad(image) {
  return new Promise(resolve => image.onload = () => resolve(image.width));
}

async function getImagesWidth(images) {
  return Promise.all(images.map(img => getImageWidthAfterLoad(images[img])));
}

$.fn.adjustSize = function (index) {
  var zoomLevel = $(this).val();
  $("#gallery-blobs-left-" + index + ", #gallery-blobs-right-" + index).children('img').each(function (i) {
    if ($(this)[0].naturalHeight != 0 || $(this)[0].naturalWidth != 0) {
      $(this).height($(this)[0].naturalHeight * zoomLevel);
      $(this).width($(this)[0].naturalWidth * zoomLevel);
    }
  });
}

// Set gallery min-height to avoid jump loops.
$.fn.setGalleryMinHeight = function (sources) {
  var minHeight;
  var selector = $(this);
  if (!Array.isArray(sources)) {
    sources = Object.keys(sources).map(function (e) {
      return sources[e];
    });
  }
  for (let i = 0; i < sources.length; i++) {
    let tmpImg = new Image();
    tmpImg.src = sources[i];
    $(tmpImg).on("load", function () {
      minHeight = parseInt(selector.css("min-height"));
      if (minHeight < tmpImg.height) {
        minHeight = tmpImg.height < 580 ? tmpImg.height : 580;
        selector.css({ minHeight: minHeight + 20 + "px" });
      }
    });
  }
};

$.fn.appendCompare = function (galleryIndex, rightItems, imgContainerRight) {
  $(this).append("<div class=p-y-10><input type=checkbox id=compare-btn-gallery-" + galleryIndex + "><label for=compare-btn-gallery-" + galleryIndex + ">Compare</label></div>");
  $("#compare-btn-gallery-" + galleryIndex).on('click', function () {
    if ($(this).is(":checked")) {
      $("#gallery-blobs-left-" + galleryIndex).css({ "flex-basis": "50%" });
      $("#gallery-blobs-right-" + galleryIndex).css({ "flex-basis": "50%" });
      $(".gallery-blobs-container-" + galleryIndex).addClass('blobs-wrapper-compare');
    } else {
      $("#gallery-blobs-left-" + galleryIndex).css({ "flex-basis": "" });
      $("#gallery-blobs-right-" + galleryIndex).css({ "flex-basis": "" });
      $(".gallery-blobs-container-" + galleryIndex).removeClass("blobs-wrapper-compare");
    }
    $("#" + imgContainerRight).toggleClass("di-none");
    $(".gallery-" + galleryIndex).toggleClass("space-between");
    $("." + rightItems).toggleClass("di-none");
  });
}

$.fn.appendLabel = function (labelArray) {
  var html = "";
  for (var i = 0; i < labelArray.length; i++) html += labelArray[i];
  if (html.charAt(0) == "'") html = eval(html);
  $(this).html("<div class=m-b-20>" + html + "</div>");
}

function scrollSync(index) {
  var isSyncingLeftScroll = false;
  var isSyncingRightScroll = false;
  var leftDiv = document.getElementById('gallery-blobs-left-' + index);
  var rightDiv = document.getElementById('gallery-blobs-right-' + index);
  $('#gallery-blobs-left-' + index).attachDragger();
  $('#gallery-blobs-right-' + index).attachDragger();

  leftDiv.onscroll = function () {
    if (!isSyncingLeftScroll) {
      isSyncingRightScroll = true;
      rightDiv.scrollTop = this.scrollTop;
      rightDiv.scrollLeft = this.scrollLeft;
    }
    isSyncingLeftScroll = false;
  }
  rightDiv.onscroll = function () {
    if (!isSyncingRightScroll) {
      isSyncingLeftScroll = true;
      leftDiv.scrollTop = this.scrollTop;
      leftDiv.scrollLeft = this.scrollLeft;
    }
    isSyncingRightScroll = false;
  }
}