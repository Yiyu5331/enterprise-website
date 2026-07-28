(function () {
    "use strict";

    function dateOnly(value) {
        return (value || "").slice(0, 10);
    }

    function queryDate(value, isEnd) {
        if (!value) return "";
        return value + (isEnd ? " 23:59:59" : " 00:00:00");
    }

    function createDateInput(label, value) {
        var input = document.createElement("input");
        input.type = "date";
        input.className = "huali-date-picker";
        input.setAttribute("aria-label", label);
        input.title = label;
        input.value = value;
        return input;
    }

    function splitDateRanges() {
        var toolbar = document.getElementById("toolbar");
        if (!toolbar || toolbar.dataset.dateRangesReady === "true") return;

        var rangePickers = toolbar.querySelectorAll(
            ".el-date-editor--daterange, .el-date-editor--datetimerange"
        );
        if (!rangePickers.length) return;

        rangePickers.forEach(function (picker) {
            var form = picker.closest("form");
            if (!form) return;

            var hiddenInputs = form.querySelectorAll("input[type='hidden']");
            var startHidden = null;
            var endHidden = null;
            hiddenInputs.forEach(function (input) {
                if (input.name && input.name.endsWith("__gte")) startHidden = input;
                if (input.name && input.name.endsWith("__lte")) endHidden = input;
            });
            if (!startHidden || !endHidden) return;

            var wrapper = document.createElement("span");
            wrapper.className = "huali-date-range-split";
            var startInput = createDateInput("开始日期", dateOnly(startHidden.value));
            var endInput = createDateInput("截止日期", dateOnly(endHidden.value));
            var separator = document.createElement("span");
            separator.className = "huali-date-separator";
            separator.textContent = "-";
            wrapper.append(startInput, separator, endInput);
            picker.parentNode.insertBefore(wrapper, picker);
            picker.style.display = "none";

            startInput.addEventListener("change", function () {
                startHidden.value = queryDate(startInput.value, false);
            });
            endInput.addEventListener("change", function () {
                endHidden.value = queryDate(endInput.value, true);
            });

            startHidden.value = queryDate(startInput.value, false);
            endHidden.value = queryDate(endInput.value, true);
        });

        toolbar.dataset.dateRangesReady = "true";
    }

    function boot() {
        splitDateRanges();
        window.setTimeout(splitDateRanges, 100);
        window.setTimeout(splitDateRanges, 500);
        window.setTimeout(splitDateRanges, 1200);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }
}());
