
$(document).ready(function(){
    console.log("Page Loaded");
    $("#take-picture-button").click(function(){
        console.log("Button Clicked");
        var backendAPI = "https://797f6e7c71.dataplicity.io/admin/take_picture";
        $.getJSON(backendAPI, function (data) {
            console.log(data);
            $( "<img>" ).attr( "src", data.url ).appendTo( "#most-recent-photo" );
        });
    });

});


// Add "active" class to nav link that matches current url.
$(function () {
    var pathName = window.location.pathname;
    $(".nav a").each(function () {
        if (_.includes(pathName, $(this).attr("href"))) {
            $(this).closest("li").addClass("active");
        }
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