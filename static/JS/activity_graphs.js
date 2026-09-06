// ######################################################
//     Activity Graphs Data Point Shapes and Colors
// ######################################################

const activityCategories = {
    Running: {
        color: "#636efa",
        symbol: "circle"
    },
    Walking: {
        color: "#EF553B",
        symbol: "square"
    },
    Cycling: {
        color: "#00cc96",
        symbol: "cross"
    },
    Weightlifting: {
        color: "#f829ff",
        symbol: "diamond"
    }
};

// ######################################################
//              Activity Durations Graph
// ######################################################

async function showActivityDurationsGraph() {

    const activityDurationsRange = document.getElementById("activityDurationsRange").value;

    const activityDurationsDate = document.getElementById("activityDurationsDatePicker").value;

    const activityDurationsCategory = document.getElementById("activityDurationsCategory").value;

    let url = `/activity/activity-durations-graph?` +
        `range=${activityDurationsRange}` +
        `&category=${activityDurationsCategory}`;

    if (activityDurationsRange !== "all") {

        if (!activityDurationsDate) {
            alert("Please select a date");
            return;
        }

        url += `&date=${activityDurationsDate}`;
    }

    const response = await fetch(url, {
        headers: authHeaders()
    });

    if (!response.ok) {
        if (response.status === 404) {
            alert("No activity data for this period");
        } else {
            alert("Could not load graph");
        }
        return;
    }

    const result = await response.json();

    const durations = result.durations;
    const range = result.range;
    const date = result.date;

    function chooseDurationTick(seconds) {
        if (seconds <= 3600) {
            return 600;
        }
        if (seconds <= 7200) {
            return 1200;
        }
        if (seconds <= 14400) {
            return 1800;
        }
        if (seconds <= 28800) {
            return 3600;
        }
        return 7200;
    }

    const y = durations.map(item => item.duration);

    const maxDuration = Math.max(...y);

    const preliminaryMax = Math.ceil(maxDuration);

    const tickSpacing = chooseDurationTick(preliminaryMax);

    const yMax =
        Math.ceil(preliminaryMax / tickSpacing) * tickSpacing;

    const tickvals = [];

    for (
        let seconds = 0;
        seconds <= yMax;
        seconds += tickSpacing
    ) {
        tickvals.push(seconds);
    }

    const ticktext =
        tickvals.map(formatTimeToHHMMSS);

    let traces;

    if (activityDurationsCategory === "all") {

        traces = Object.keys(activityCategories).map(category => {

            const categoryData =
                durations.filter(
                    item => item.category === category
                );

            return {
                x: categoryData.map(item => item.date),
                y: categoryData.map(item => item.duration),

                mode: "markers",
                type: "scatter",

                name: category,

                marker: {
                    size: 10,
                    color: activityCategories[category].color,
                    symbol: activityCategories[category].symbol
                },

                customdata: categoryData.map(item => [
                    formatTimeToHHMMSS(item.duration),
                    item.category
                ]),

                hovertemplate:
                    "Date: %{x}<br>" +
                    "Duration: %{customdata[0]}<br>" +
                    "Category: %{customdata[1]}" +
                    "<extra></extra>"
            };
        });

    } else {

        traces = [{
            x: durations.map(item => item.date),
            y: durations.map(item => item.duration),

            mode: "markers",
            type: "scatter",

            name: activityDurationsCategory,

            marker: {
                size: 10,
                color: activityCategories[activityDurationsCategory].color,
                symbol: activityCategories[activityDurationsCategory].symbol
            },

            customdata: durations.map(item => [
                formatTimeToHHMMSS(item.duration),
                item.category
            ]),

            hovertemplate:
                "Date: %{x}<br>" +
                "Duration: %{customdata[0]}<br>" +
                "Category: %{customdata[1]}" +
                "<extra></extra>"
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
                text: "Duration (HH:MM:SS)"
            },
            range: [0, yMax],
            tickvals: tickvals,
            ticktext: ticktext
        }
    };

    if (range === "year") {

        const year = Number(date.substring(0, 4));

        layout.xaxis.range = [
            `${year}-01-01`,
            `${year + 1}-01-01`
        ];

        layout.xaxis.dtick = "M1";
    }

    else if (range === "month") {

        const year = Number(date.substring(0, 4));
        const month = Number(date.substring(5, 7));

        let nextMonth;

        if (month === 12) {
            nextMonth =
                `${year + 1}-01-01`;
        } else {
            nextMonth =
                `${year}-${String(month + 1).padStart(2, "0")}-01`;
        }

        layout.xaxis.range = [
            `${year}-${String(month).padStart(2, "0")}-01`,
            nextMonth
        ];

        layout.xaxis.dtick = "D1";
    }

    Plotly.react(
        "activityDurationsGraph",
        traces,
        layout
    );

    document.getElementById("activityDurationsGraph")
        .on("plotly_click", function (durations) {
            const date = durations.points[0].x;
            window.location.href = `/calendar/${date}`;
        });

    document.getElementById("activityDurationsGraph").hidden = false;
}

function hideActivityDurationsGraph() {

    document.getElementById("activityDurationsGraph").hidden = true;

}

// ######################################################
//              Activity Distances graph
// ######################################################

async function showActivityDistancesGraph() {

    const activityDistancesRange = document.getElementById("activityDistancesRange").value;

    const activityDistancesDate = document.getElementById("activityDistancesDatePicker").value;

    const activityDistancesCategory = document.getElementById("activityDistancesCategory").value;

    const activityDistancesGraphType = document.getElementById("activityDistancesGraphType").value;

    let url = `/activity/activity-distances-graph?` +
        `range=${activityDistancesRange}` +
        `&category=${activityDistancesCategory}` +
        `&graph_type=${activityDistancesGraphType}`;

    if (activityDistancesRange !== "all") {

        if (!activityDistancesDate) {
            alert("Please select a date");
            return;
        }

        url += `&date=${activityDistancesDate}`;
    }

    const response = await fetch(url, {
        headers: authHeaders()
    });

    if (!response.ok) {
        if (response.status === 404) {
            alert("No activity data for this period");
        } else {
            alert("Could not load graph");
        }
        return;
    }

    const result = await response.json();

    const distances = result.distances;
    const range = result.range;
    const date = result.date;

    function chooseDistanceTick(distance) {

        if (distance <= 10) {
            return 1;
        }
        if (distance <= 25) {
            return 2.5;
        }
        if (distance <= 50) {
            return 5;
        }
        if (distance <= 100) {
            return 10;
        }
        if (distance <= 150) {
            return 15;
        }
        if (distance <= 200) {
            return 20;
        }
        if (distance <= 300) {
            return 30;
        }
        if (distance <= 400) {
            return 40;
        }
        if (distance <= 500) {
            return 50;
        }
        if (distance <= 600) {
            return 60;
        }
        if (distance <= 700) {
            return 70;
        }
        if (distance <= 800) {
            return 80;
        }
        if (distance <= 900) {
            return 90;
        }
        return 100;
    }

    const y = distances.map(item => item.distance);

    const maxDistance = Math.max(...y);

    const preliminaryMax = Math.ceil(maxDistance);

    const tickSpacing = chooseDistanceTick(preliminaryMax);

    const yMax = Math.ceil(preliminaryMax / tickSpacing) * tickSpacing + 1;

    const tickvals = [];

    for (
        let distance = 0;
        distance <= yMax;
        distance += tickSpacing
    ) {
        tickvals.push(distance);
    }

    let traces;

    const graphMode = activityDistancesGraphType === "standard" ? "markers" : "lines+markers";

    if (
        activityDistancesCategory === "all"
        && activityDistancesGraphType === "cumulative"
    ) {

        alert("Cumulative requires a specific category");

        return;

    } else if (activityDistancesCategory === "all") {

        traces = Object.keys(activityCategories)
            .filter(category =>
                distances.some(item => item.category === category)
            )
            .map(category => {

                const categoryData = distances.filter(
                    item => item.category === category
                );

                return {
                    x: categoryData.map(item => item.date),
                    y: categoryData.map(item => item.distance),

                    mode: "markers",
                    type: "scatter",

                    name: category,

                    marker: {
                        size: 10,
                        color: activityCategories[category].color,
                        symbol: activityCategories[category].symbol
                    },

                    hovertemplate:
                        "Date: %{x}<br>" +
                        "Distance: %{y} mi<br>" +
                        "Category: %{customdata}" +
                        "<extra></extra>",

                    customdata:
                        categoryData.map(item => item.category)
                };
            });

    } else {

        traces = [{

            x: distances.map(item => item.date),

            y: distances.map(item => item.distance),

            mode: graphMode,

            type: "scatter",

            name: activityDistancesCategory,

            marker: {
                size: 10,
                color: activityCategories[activityDistancesCategory].color,
                symbol: activityCategories[activityDistancesCategory].symbol
            },

            hovertemplate:
                "Date: %{x}<br>" +
                "Distance: %{y} mi<br>" +
                "Category: %{fullData.name}" +
                "<extra></extra>",

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
                text: "Distance (mi)"
            }, range: [0, yMax],
            tickvals: tickvals
        }
    };

    if (range === "year") {

        const year = Number(date.substring(0, 4));

        layout.xaxis.range = [
            `${year}-01-01`,
            `${year + 1}-01-01`
        ];

        layout.xaxis.dtick = "M1";
    }

    else if (range === "month") {

        const year = Number(date.substring(0, 4));
        const month = Number(date.substring(5, 7));

        let nextMonth;

        if (month === 12) {
            nextMonth =
                `${year + 1}-01-01`;
        } else {
            nextMonth =
                `${year}-${String(month + 1).padStart(2, "0")}-01`;
        }

        layout.xaxis.range = [
            `${year}-${String(month).padStart(2, "0")}-01`,
            nextMonth
        ];

        layout.xaxis.dtick = "D1";
    }

    Plotly.react(
        "activityDistancesGraph",
        traces,
        layout
    );

    document.getElementById("activityDistancesGraph")
        .on("plotly_click", function (distances) {
            const date = distances.points[0].x;
            window.location.href = `/calendar/${date}`;
        });

    document.getElementById("activityDistancesGraph").hidden = false;
}

function hideActivityDistancesGraph() {

    document.getElementById("activityDistancesGraph").hidden = true;

}

// ######################################################
//                Activity Paces Graph
// ######################################################

async function showActivityPacesGraph() {

    const activityPacesRange = document.getElementById("activityPacesRange").value;

    const activityPacesDate = document.getElementById("activityPacesDatePicker").value;

    const activityPacesCategory = document.getElementById("activityPacesCategory").value;

    let url = `/activity/activity-paces-graph?` +
        `range=${activityPacesRange}` +
        `&category=${activityPacesCategory}`;

    if (activityPacesRange !== "all") {

        if (!activityPacesDate) {
            alert("Please select a date");
            return;
        }

        url += `&date=${activityPacesDate}`;
    }

    console.log("Request URL:", url);

    const response = await fetch(url, {
        headers: authHeaders()
    });

    if (!response.ok) {
        if (response.status === 404) {
            alert("No activity data for this period");
        } else {
            alert("Could not load graph");
        }
        return;
    }

    const result = await response.json();

    const paces = result.paces;
    const range = result.range;
    const date = result.date;

    function choosePacesTick(seconds) {
        if (seconds <= 600) {
            return 60;
        }
        if (seconds <= 1200) {
            return 120;
        }
        if (seconds <= 1800) {
            return 180;
        }
        if (seconds <= 2400) {
            return 300;
        }
        if (seconds <= 3600) {
            return 600;
        }
        return 900;
    }

    const y = paces.map(item => item.pace);

    const maxPace = Math.max(...y);

    const preliminaryMax = Math.ceil(maxPace);

    const tickSpacing = choosePacesTick(preliminaryMax);

    const yMax =
        Math.ceil(preliminaryMax / tickSpacing) * tickSpacing + 120;

    const tickvals = [];

    for (
        let seconds = 0;
        seconds <= yMax;
        seconds += tickSpacing
    ) {
        tickvals.push(seconds);
    }

    const ticktext =
        tickvals.map(formatTimeToHHMMSS);

    let traces;

    if (activityPacesCategory === "all") {

        traces = Object.keys(activityCategories)
            .filter(category =>
                paces.some(item => item.category === category)
            ).map(category => {

                const categoryData =
                    paces.filter(
                        item => item.category === category
                    );

                return {
                    x: categoryData.map(item => item.date),
                    y: categoryData.map(item => item.pace),

                    mode: "markers",
                    type: "scatter",

                    name: category,

                    marker: {
                        size: 10,
                        color: activityCategories[category].color,
                        symbol: activityCategories[category].symbol
                    },

                    customdata: categoryData.map(item => [
                        formatTimeToHHMMSS(item.pace),
                        item.category
                    ]),

                    hovertemplate:
                        "Date: %{x}<br>" +
                        "Pace: %{customdata[0]}<br>" +
                        "Category: %{customdata[1]}" +
                        "<extra></extra>"
                };
            });

    } else {

        traces = [{
            x: paces.map(item => item.date),
            y: paces.map(item => item.pace),

            mode: "markers",
            type: "scatter",

            name: activityPacesCategory,

            marker: {
                size: 10,
                color: activityCategories[activityPacesCategory].color,
                symbol: activityCategories[activityPacesCategory].symbol
            },

            customdata: paces.map(item => [
                formatTimeToHHMMSS(item.pace),
                item.category
            ]),

            hovertemplate:
                "Date: %{x}<br>" +
                "Pace: %{customdata[0]}<br>" +
                "Category: %{customdata[1]}" +
                "<extra></extra>"
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
                text: "Pace (min/mi)"
            },
            range: [0, yMax],
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
            nextMonth = `${year}-${String(month + 1)
                .padStart(2, "0")}-01`;
        }

        layout.xaxis.range = [
            `${year}-${String(month)
                .padStart(2, "0")}-01`,
            nextMonth
        ];

        layout.xaxis.dtick = "D1";
    }

    Plotly.react("activityPacesGraph", traces, layout);

    document.getElementById("activityPacesGraph")
        .on("plotly_click", function (paces) {
            const date = paces.points[0].x;
            window.location.href = `/calendar/${date}`;
        });

    document.getElementById("activityPacesGraph").hidden = false;
}

function hideActivityPacesGraph() {

    document.getElementById("activityPacesGraph").hidden = true;

}