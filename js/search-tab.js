$(function setupSearchTabBehavior() {
    function getQueryParamsMap() {
        var query = location.search.substr(1);
        var map = {};
        query.split("&").forEach(function(part) {
            var pair = part.split("=");
            map[pair[0]] = decodeURIComponent((pair[1] || "").replace(/\+/g, "%20"));
        });
        return map;
    }

    $(function extractParamsFromUrlThenSearch() {
        var map = getQueryParamsMap();

        $("[name=tag]").val(map.tag);
        $("[name=searchStartDate]").val(map.searchStartDate);
        $("[name=searchEndDate]").val(map.searchEndDate);

        if (map.submit) {
            searchPictures(map.tag, map.searchStartDate, map.searchEndDate);
        }
    });

    // Only load the image if they click the row.
    $(document).on("click", ".search-results-table tr", function loadImage(evt) {
        if ($("img", this).length) {
            // Already loaded.
            return;
        }
        var imgUrl = $("a", this).attr("href");
        var $a = $("<a target='_blank'></a>");
        var $img = $("<img>");
        $img.attr("src", imgUrl);
        $a.attr("href", imgUrl);
        $(".img-col", this).append($img);
        $a.append($img);
        $(".img-col", this).append($a);
    });

    function searchPictures(tag, start, end) {
        $.get({
            url: piCam.fileStoreHost + "/file-store/search.php",
            data: {
                limit: 100,
                minDateTime: start,
                maxDateTime: end,
                filter: tag
            }
        }).then(function getSearchResultSuccess(files) {
            if (!files || !files.length) {
                $(".no-search-results").show();
                return;
            }

            renderResults(files);
        });
    }


    function renderResults(imageRecords) {
        $(".search-results").show();
        var rowTpl = _.template($("#picture-search-results-row-tpl").text());
        var html = imageRecords.map(function(record) {
            var peices = record.url.split("/");
            return rowTpl({
                url: record.url,
                fileName: peices[peices.length - 1]
            });
        });

        $(".search-results-table tbody").html(html);
    }
});

$(function initDatePickers() {
    $(".datetime-picker").datetimepicker();
    $(".time-picker").datetimepicker({
        format: 'LT'
    });
});