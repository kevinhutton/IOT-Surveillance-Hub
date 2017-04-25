$(function setupNotificationsTabBehavior() {
    $(".create-notification-record-form").on("submit", function submitHandler(evt) {
        evt.preventDefault();
        createNewNotificationRecord();
    });

    $("body").on("click", ".delete-record", function deleteButtonHandler() {
        var rowId = $(this).data("record-id");
        deleteNotificationRecord(rowId);
    });

    $("body").on("change", "[name^='stfu-']", _.debounce(function stfuButtonHandler() {
        var rowId = $(this).data("record-id");
        var disabled = $(this).is(":checked") && $(this).is(".stfu-enabled-button") ? 0 : 1;
        updateNotificationRecord(rowId, disabled);
    }, 20));

    function getDateObject(pickerElem) {
        var $pickerElem = $(pickerElem);
        // Detect empty input field.
        if (!($pickerElem.find("input").val() || "").trim().length) {
            return null;
        }

        // return the moment date obj.
        return $pickerElem.data("DateTimePicker").date();
    }

    function formatDateObjectToSqliteDateFormat(momentDate) {
        return momentDate && momentDate.format("YYYY-MM-DD HH:mm:ss");
    }

    function formatDateObjectTo24Time(momentDate) {
        if (!momentDate) {
            return null;
        }

        return momentDate.format("HH:mm");
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
            startDate: formatDateObjectToSqliteDateFormat(startDate),
            endDate: formatDateObjectToSqliteDateFormat(endDate),
            dailyStartTime: formatDateObjectTo24Time(dailyStartTime),
            dailyEndTime: formatDateObjectTo24Time(dailyEndTime)
        };
    }

    function createNewNotificationRecord() {
        var data = getFormData();
        $.post({
            url: piCam.piHost + "/api/notification-records",
            data: data
        }).then(function() {
            window.location.reload();
        });
    }

    function updateNotificationRecord(id, disabled) {
        $.ajax({
            url: piCam.piHost + "/api/notification-records/" + encodeURIComponent(id),
            method: "PUT",
            data: {disabled: disabled}
        }).then(function() {
            window.location.reload();
        });
    }

    function deleteNotificationRecord(id) {
        $.ajax({
            url: piCam.piHost + "/api/notification-records/" + encodeURIComponent(id),
            method: "DELETE"
        }).then(function() {
            window.location.reload();
        });
    }

    function getExistingNotificationRecords() {
       return $.get({
           url: piCam.piHost + "/api/notification-records",
           dataType: "json"
       });
    }

    function toLocalDateTime(dateStr) {
        if (!dateStr) {
            return "";
        }
        return moment(dateStr).format("YYYY-MM-DD HH:mm:ss");
    }

    function to12HourTime(timeStr) {
        if (!timeStr) {
            return "";
        }
        var match = timeStr.match(/(\d{2}):(\d{2})/);
        var hrs24 = match[1];
        var minutes = match[2];
        var hrs12 = hrs24 % 12;
        var amPm = hrs24 > 12 ? " pm" : "  am";
        return hrs12 + ":" + minutes + amPm;
    }

    function renderExistingNotificationRecords(records) {
        var rowTpl = _.template($("#existing-notification-record-row-tpl").text());
        var html = records.map(function(record) {
            return rowTpl({
                id: record.rowid,
                email: record.email,
                throttleMinutes: record.throttleMinutes,
                startDate: toLocalDateTime(record.startDate),
                endDate: toLocalDateTime(record.endDate) || "\u221E",
                dailyStartTime: to12HourTime(record.dailyStartTime),
                dailyEndTime: to12HourTime(record.dailyEndTime),
                stfuBtnClass: record.disabled === 1 ? "btn-warning" : "btn-success",
                stfuEnabled: record.disabled === 0 ? "active" : "",
                stfuDisabled: record.disabled === 1 ? "active" : "",
            });
        });

        $(".existing-notification-records tbody").html(html);
    }

    getExistingNotificationRecords().then(renderExistingNotificationRecords);
});

$(function initDatePickers() {
    $(".datetime-picker").datetimepicker();
    $(".time-picker").datetimepicker({
        format: 'LT'
    });
});