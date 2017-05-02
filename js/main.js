var piCam = window.piCam || {};
piCam.piHost = "https://797f6e7c71.dataplicity.io";
piCam.fileStoreHost = "https://cors-anywhere.herokuapp.com/http://104.233.111.80";
// piCam.piHost = "http://localhost";

$(document).ready(function(){
    var streamName = "manual";
    var $ctx = $('#take-picture');

    console.log("Page Loaded");
    $("#take-picture-button").click(function(){
        console.log("Button Clicked");
        var backendAPI = piCam.piHost + "/admin/take_picture";
        $.getJSON(backendAPI, function (data) {
            // console.log(data);
            // $("#most-recent-photo").empty();
            // $( "<img>" ).attr( "src", data.url ).appendTo( "#most-recent-photo" );
            loadLatestPic(true);
        });
    });

    function loadLatestPic(doAnimationEffect) {
        $.get({
            url: piCam.fileStoreHost + "/file-store/search.php",
            data: {
                limit: 1,
                filter: streamName
            }
        }).then(function getLatestFileNameSuccess(files) {
            if (!files || !files.length) {
                return;
            }

            // Preload the image so we don't slide it in before it's ready.
            var url = files[0].url;
            var img = new Image();
            img.onload = function () {
                // Make the img elem.
                var $img = $("<img>").attr("src", url);

                $(".most-recent-photo", $ctx).empty().append($img);

                if (doAnimationEffect) {
                    // Slide it in, and once it's done sliding, add more shadow.
                    $(".photo-wrapper", $ctx)
                        .animateCss("fadeInUp")
                        .then(function(animName, elem) {
                            $(elem).addClass("photo-wrapper-shadow");
                        });
                }
            };
            img.src = url;
        });
    }

});


$(function enableBookmarkingOfTabs() {
    // When the page loads, show the right tab (if there's a url hash for a tab).
    var hash = window.location.hash;
    $(".nav a").each(function () {
        if ($(this).attr("href") === hash) {
            $(this).click();
        }
    });

    // Update the hash in the url when a nav link is clicked.
    // This enabled bookmarking and reloading the page into the desired tab.
    $(".nav a").on("click", function() {
        location.href = $(this).attr("href");
    });
});

$.fn.extend({
    animateCss: function (animationName) {
        var animationEnd = 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend';
        var dfd = $.Deferred();
        this.addClass('animated ' + animationName).one(animationEnd, function() {
            $(this).removeClass('animated ' + animationName);
            dfd.resolve(animationName, this);
        });
        return dfd;
    }
});

$(function initTooltips() {
   $("[data-toggle=tooltip]").tooltip();
   $("[data-toggle=popover]").popover();
});