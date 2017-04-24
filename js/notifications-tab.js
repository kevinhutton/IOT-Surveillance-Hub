$(function setupNotificationsTabBehavior() {
    $(".create-notification-record-form").on("submit", function submitHandler(evt) {
        evt.preventDefault();
        createNewNotificationRecord();
    });

    var mockRecords = [{id: 1, email: "foo@bar.com"}];
    function getDateObject(pickerElem) {
        var $pickerElem = $(pickerElem);
        // Detect empty input field.
        if (!($pickerElem.find("input").val() || "").trim().length) {
            return null;
        }

        // return the moment date obj.
        return $pickerElem.data("DateTimePicker").date();
    }

    function formatDateObject(momentDate) {
        return momentDate && momentDate.toISOString();
    }

    function getFormData() {
        var email = $("[name=email]").val();
        var throttleMinutes = $("[name=throttleMinutes]").val();
        var startDate = getDateObject($("#inputStartDateWrapper"));
        var endDate = getDateObject($("#inputEndDateWrapper"));
        var dailyStartTime = getDateObject($("#inputDailyStartTimeWrapper"));
        var dailyEndTime = getDateObject($("#inputDailyEndTimeWrapper"));

        return {
            email: email,
            throttleMinutes: throttleMinutes,
            startDate: formatDateObject(startDate),
            endDate: formatDateObject(endDate),
            dailyStartTime: formatDateObject(dailyStartTime),
            dailyEndTime: formatDateObject(dailyEndTime)
        };
    }

    function createNewNotificationRecord() {
        var data = getFormData();
        $.post({
            url: "/api/notification-records",
            data: data
        }).then(function() {
            window.location.reload();
        });
    }

//            function getExistingNotificationRecords() {
//                return $.get({
//                    url: "/admin/notification-records",
//                    dataType: "json"
//                });
//            }

    function getExistingNotificationRecords() {
        return new Promise(function(resolve, reject) {
            setTimeout(function() {
                resolve(mockRecords);
            }, 250);
        });
    }

    function renderExistingNotificationRecords(records) {
        var rowTpl = _.template($("#existing-notification-record-row-tpl").text());
        var html = records.map(function(record) {
            return rowTpl({
                id: record.id,
                email: record.email,
                throttleMinutes: 22,
                startDateTime: 22,
                endDateTime: 22,
                dailyStartTime: 22,
                dailyEndTime: 22,
                dailyEndTime: 22,
                stfuState: "on"
            });
        });

        $(".existing-notification-records tbody").html(html);
    }

    getExistingNotificationRecords().then(renderExistingNotificationRecords);
});