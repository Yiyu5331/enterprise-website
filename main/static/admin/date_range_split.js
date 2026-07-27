(function () {
    "use strict";

    function formatDate(value, endOfDay) {
        if (!value) return "";
        return value + (endOfDay ? " 23:59:59" : " 00:00:00");
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

            var startValue = (startHidden.value || "").slice(0, 10);
            var endValue = (endHidden.value || "").slice(0, 10);
            var wrapper = document.createElement("span");
            wrapper.className = "huali-date-range-split";
            wrapper.innerHTML = [
                '<el-date-picker class="huali-date-picker" v-model="start"',
                ' type="date" value-format="yyyy-MM-dd" format="yyyy-MM-dd"',
                ' placeholder="开始日期" clearable></el-date-picker>',
                '<span class="huali-date-separator">-</span>',
                '<el-date-picker class="huali-date-picker" v-model="end"',
                ' type="date" value-format="yyyy-MM-dd" format="yyyy-MM-dd"',
                ' placeholder="截止日期" clearable></el-date-picker>'
            ].join("");
            picker.parentNode.insertBefore(wrapper, picker);
            picker.style.display = "none";

            // 使用独立 Vue 实例，让两个日历选择器分别维护自己的日期。
            new Vue({
                el: wrapper,
                data: {
                    start: startValue,
                    end: endValue
                },
                watch: {
                    start: function (value) {
                        startHidden.value = formatDate(value, false);
                    },
                    end: function (value) {
                        endHidden.value = formatDate(value, true);
                    }
                }
            });

            startHidden.value = formatDate(startValue, false);
            endHidden.value = formatDate(endValue, true);
        });

        toolbar.dataset.dateRangesReady = "true";
    }

    function boot() {
        splitDateRanges();
        if (!document.getElementById("toolbar") || document.querySelector(".huali-date-range-split")) return;
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
