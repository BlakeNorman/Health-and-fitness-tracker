// ######################################################
// Calories/Water/Weight Graph
// ######################################################

async function showHealthGraph() {

    const healthGraphRange = document.getElementById("healthGraphRange").value;

    const healthGraphDate = document.getElementById("healthGraphDatePicker").value;

    const healthGraphParameter = document.getElementById("healthGraphParameter").value;

    let url = `/health/health-graph?parameter=${healthGraphParameter}&range=${healthGraphRange}`;

    if (healthGraphRange !== "all") {

        if (!healthGraphDate) {
            alert("Please select a date");
            return;
        }

        url += `&date=${healthGraphDate}`;
    }

    const response = await fetch(url, {
        headers: authHeaders()
    });

    if (!response.ok) {

        if (response.status === 404) {
            alert(`No ${healthGraphParameter} data for this period`);
        } else {
            alert("Could not load graph");
        }
        return;
    }

    const result = await response.json();

    const data = result.data;
    const parameter = result.parameter;
    const range = result.range;
    const date = result.date;

    const x = data.map(item => item.date);
    const y = data.map(item => item[parameter]);

    let units = "";

    if (parameter === "water") {
        units = " (fl oz)";
    } else if (parameter === "weight") {
        units = " (lbs)";
    }

    const trace = { x: x, y: y, mode: "markers", type: "scatter", marker: { size: 10 } };

    const layout = {
        xaxis: { title: { text: "Date" } },
        yaxis: { title: { text: parameter + units }, rangemode: "tozero" }
    };

    if (range === "year") {

        const year = Number(date.substring(0, 4));

        layout.xaxis.range = [`${year}-01-01`, `${year + 1}-01-01`];

        layout.xaxis.dtick = "M1";
    }

    else if (range === "month") {

        const year = Number(date.substring(0, 4));
        const month = Number(date.substring(5, 7));

        let nextMonth;

        if (month === 12) {
            nextMonth = `${year + 1}-01-01`;
        } else {
            nextMonth = `${year}-${String(month + 1).padStart(2, "0")}-01`;
        }

        layout.xaxis.range = [`${year}-${String(month).padStart(2, "0")}-01`, nextMonth];

        layout.xaxis.dtick = "D1";
    }

    Plotly.react("healthGraph", [trace], layout);

    document.getElementById("healthGraph").on("plotly_click", function (data) {
        const date = data.points[0].x;
        window.location.href = `/calendar/${date}`;
    });

    document.getElementById("healthGraph").hidden = false;
}

function hideHealthGraph() {

    document.getElementById("healthGraph").hidden = true;

}

// ######################################################
// Macros Graph
// ######################################################

async function showMacrosGraph() {

    const macrosGraphRange = document.getElementById("macrosGraphRange").value;

    const macrosGraphDate = document.getElementById("macrosGraphDatePicker").value;

    const macrosGraphParameter = document.getElementById("macrosGraphParameter").value;

    let url = `/health/macros-graph?&range=${macrosGraphRange}`;

    if (macrosGraphRange !== "all") {

        if (!macrosGraphDate) {
            alert("Please select a date");
            return;
        }

        url += `&date=${macrosGraphDate}`;
    }

    const response = await fetch(url, {
        headers: authHeaders()
    });

    if (!response.ok) {

        if (response.status === 404) {
            alert(`No macros data for this period`);
        } else {
            alert("Could not load graph");
        }
        return;
    }

    const result = await response.json();

    const data = result.data;
    const range = result.range;
    const date = result.date;

    const colors = { fats: "#636efa", carbs: "#EF553B", protein: "#00cc96" };

    const symbols = { fats: "circle", carbs: "square", protein: "cross" };

    const x = data.map(item => item.date);

    let traces;

    if (macrosGraphParameter === "all") {
        traces = ["fats", "carbs", "protein"].map(macro => ({
            x: x, y: data.map(item => item[macro]),
            mode: "markers", type: "scatter",
            name: macro.charAt(0).toUpperCase() + macro.slice(1),
            marker: { size: 10, color: colors[macro], symbol: symbols[macro] }
        }));
    } else {
        traces = [{
            x: x, y: data.map(item => item[macrosGraphParameter]),
            mode: "markers", type: "scatter",
            name: macrosGraphParameter.charAt(0).toUpperCase() + macrosGraphParameter.slice(1),
            marker: { size: 10, color: colors[macrosGraphParameter], symbol: symbols[macrosGraphParameter] }
        }];
    }

    const layout = {
        xaxis: {
            title: {
                text: "Date"
            }
        },
        yaxis: {
            title: {
                text: macrosGraphParameter === "all" ? "Grams" : macrosGraphParameter + " (g)"
            },
            rangemode: "tozero"
        }
    };

    if (range === "year") {

        const year = Number(date.substring(0, 4));

        layout.xaxis.range = [`${year}-01-01`, `${year + 1}-01-01`];

        layout.xaxis.dtick = "M1";
    }

    else if (range === "month") {

        const year = Number(date.substring(0, 4));
        const month = Number(date.substring(5, 7));

        let nextMonth;

        if (month === 12) {
            nextMonth = `${year + 1}-01-01`;
        } else {
            nextMonth = `${year}-${String(month + 1).padStart(2, "0")}-01`;
        }

        layout.xaxis.range = [`${year}-${String(month).padStart(2, "0")}-01`, nextMonth];

        layout.xaxis.dtick = "D1";
    }

    Plotly.react("macrosGraph", traces, layout);

    document.getElementById("macrosGraph").on("plotly_click", function (data) {
        const date = data.points[0].x;
        window.location.href = `/calendar/${date}`;
    });

    document.getElementById("macrosGraph").hidden = false;
}

function hideMacrosGraph() {

    document.getElementById("macrosGraph").hidden = true;

}

// ######################################################
// Sleep Times Graph
// ######################################################

async function showSleepGraph() {

    const sleepGraphRange = document.getElementById("sleepGraphRange").value;

    const sleepGraphDate = document.getElementById("sleepGraphDatePicker").value;

    let url = `/health/sleep-graph?range=${sleepGraphRange}`;

    if (sleepGraphRange !== "all") {

        if (!sleepGraphDate) {
            alert("Please select a date");
            return;
        }

        url += `&date=${sleepGraphDate}`;
    }

    const response = await fetch(url, {
        headers: authHeaders()
    });

    if (!response.ok) {

        if (response.status === 404) {
            alert(`No bedtime and/or wake time data for this period`);
        } else {
            alert("Could not load graph");
        }
        return;
    }

    const result = await response.json();

    const data = result.data;

    console.log("data:", data);
    console.log("first item:", data[0]);

    const sleepData = data.filter(item => item.bedtime && item.wake_time);
    const range = result.range;
    const date = result.date;

    function calculateSleepLength(bedtime, wakeTime) {
        if (!bedtime || !wakeTime) {
            return null;
        }

        const [bedtimeHour, bedtimeMinute] = bedtime.split(":").map(Number);
        const [wakeHour, wakeMinute] = wakeTime.split(":").map(Number);

        let bedtimeMinutes = bedtimeHour * 60 + bedtimeMinute;
        let wakeMinutes = wakeHour * 60 + wakeMinute;

        if (wakeMinutes <= bedtimeMinutes) {
            wakeMinutes += 24 * 60;
        }

        return wakeMinutes - bedtimeMinutes;
    }

    function formatSleepLength(minutes) {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;

        return `${hours} hrs ${mins} mins`;
    }

    function formatTimeToAMPM(timeString) {
        if (!timeString) {
            return "No data entered";
        }

        const [hour, minute] = timeString.split(":").map(Number);

        const period = hour >= 12 ? "PM" : "AM";
        const hour12 = hour % 12 || 12;

        return `${hour12}:${String(minute).padStart(2, "0")} ${period}`;
    }

    const x = sleepData.map(item => item.date);
    const y = sleepData.map(item => calculateSleepLength(item.bedtime, item.wake_time));

    const maxSleep = Math.max(...y.filter(value => value !== null));

    const yMax = Math.ceil(maxSleep / 60) * 60;

    const tickvals = [];

    for (let minutes = 0; minutes <= yMax + 60; minutes += 60) {
        tickvals.push(minutes);
    }

    const ticktext = tickvals.map(minutes => {
        const hours = minutes / 60;
        return `${hours} hr`;
    });

    const customdata = sleepData.map(item => [
        formatTimeToAMPM(item.bedtime),
        formatTimeToAMPM(item.wake_time),
        formatSleepLength(calculateSleepLength(item.bedtime, item.wake_time))
    ]);

    const trace = {
        x: x,
        y: y,
        mode: "markers",
        type: "scatter",
        marker: { size: 10 },
        customdata: customdata,
        hovertemplate: "Date: %{x}<br>" +
            "Sleep Time: %{customdata[2]}<br>" +
            "Bedtime: %{customdata[0]}<br>" +
            "Wake Time: %{customdata[1]}<br>" +
            "<extra></extra>"
    };

    const layout = {
        xaxis: { title: { text: "Date" } },
        yaxis: {
            title: { text: "Sleep Duration" },
            range: [0, yMax + 60],
            tickvals: tickvals,
            ticktext: ticktext
        }
    };

    if (range === "year") {

        const year = Number(date.substring(0, 4));

        layout.xaxis.range = [`${year}-01-01`, `${year + 1}-01-01`];

        layout.xaxis.dtick = "M1";
    }

    else if (range === "month") {

        const year = Number(date.substring(0, 4));
        const month = Number(date.substring(5, 7));

        let nextMonth;

        if (month === 12) {
            nextMonth = `${year + 1}-01-01`;
        } else {
            nextMonth = `${year}-${String(month + 1).padStart(2, "0")}-01`;
        }

        layout.xaxis.range = [`${year}-${String(month).padStart(2, "0")}-01`, nextMonth];

        layout.xaxis.dtick = "D1";
    }

    Plotly.react("sleepGraph", [trace], layout);

    document.getElementById("sleepGraph").on("plotly_click", function (data) {
        const date = data.points[0].x;
        window.location.href = `/calendar/${date}`;
    });

    document.getElementById("sleepGraph").hidden = false;
}

function hideSleepGraph() {

    document.getElementById("sleepGraph").hidden = true;

}