var piCam = window.piCam || {};
piCam.piHost = "https://797f6e7c71.dataplicity.io";
piCam.fileStoreHost = "http://104.233.111.80";
// piCam.piHost = "http://localhost";

$(document).ready(function(){
    console.log("Page Loaded");
    $("#take-picture-button").click(function(){
        console.log("Button Clicked");
        var backendAPI = piCam.piHost + "/admin/take_picture";
        $.getJSON(backendAPI, function (data) {
            console.log(data);
            $( "<img>" ).attr( "src", data.url ).appendTo( "#most-recent-photo" );
        });
    });

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