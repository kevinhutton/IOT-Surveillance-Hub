
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