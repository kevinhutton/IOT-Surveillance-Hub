$(function setupLiveTabBehavior() {
    "use strict";
    var $ctx = $('#live');
    var numPics = 5;
    var millisDelayBetweenPics = 800;
    var streamName = "live-stream1";
    var intervalId;

    function startContinuousLoadingOfLatestPic() {
        intervalId = setInterval(loadLatestPic, millisDelayBetweenPics);
    }

    function stopContinuousLoadingOfLatestPic() {
        intervalId && clearInterval(intervalId);
        intervalId = undefined;
    }

    function loadLatestPic(doAnimationEffect) {
        $.get({
            url: "http://104.233.111.80/file-store/search.php",
            data: {
                limit: 1,
                streamName: streamName
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

    $('#start-live-stream').click(function() {
        startContinuousLoadingOfLatestPic();
        $.get({
            url: piCam.piHost + "/admin/start_picture_stream",
            data: {
                numPics: numPics,
                millisDelayBetweenPics: millisDelayBetweenPics,
                streamName: streamName
            }
        });
    });

    $('#stop-live-stream').click(function() {
        stopContinuousLoadingOfLatestPic();
        $.get({
            url: piCam.piHost + "/admin/stop_picture_stream",
            data: {
                streamName: streamName
            }
        });
    });
});