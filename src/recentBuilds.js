import {$} from "jquery";

import {addLoadingTask, removeLoadingTask} from "./main.js";

function timeSince(date) {
    var seconds = Math.floor((new Date() - date) / 1000);
    var interval = seconds / 31536000;

    if (interval > 1) {
        return Math.floor(interval) + " years";
    }
    interval = seconds / 2592000;
    if (interval > 1) {
        return Math.floor(interval) + " months";
    }
    interval = seconds / 86400;
    if (interval > 1) {
        return Math.floor(interval) + " days";
    }
    interval = seconds / 3600;
    if (interval > 1) {
        return Math.floor(interval) + " hours";
    }
    interval = seconds / 60;
    if (interval > 1) {
        return Math.floor(interval) + " minutes";
    }
    return Math.floor(seconds) + " seconds";
}

async function onClickGeneratePrice(build_id) {
    try {
        addLoadingTask("generate-price_" + build_id);
        await $.ajax(`/price/${build_id}`)
    } catch(err) {
        console.log(err);
        alert("Failed to price build: " + err.responseText);
    }

    await fetchRecentBuildsPage();
    $(`.build-entry[build-id=${build_id}]`).find("input[type=radio]").prop("checked", true);
    removeLoadingTask("generate-price_" + build_id);
}

async function onClickSetPrice(build_id) {
    addLoadingTask("set-price_" + build_id);
    let price = parseFloat($(`.build-entry[build-id=${build_id}]`).find("#entry-set-price-field").val());
    let dto = {
        'price': price,
    }

    await $.ajax(`/price/${build_id}`, {
        'method': "POST",
        'data': JSON.stringify(dto),
        'dataType': "json",
    });

    await fetchRecentBuildsPage();
    $(`.build-entry[build-id=${build_id}]`).find("input[type=radio]").prop("checked", true);
    removeLoadingTask("set-price_" + build_id);
}

function onClickPrintBuildsheet(build_id) {
    var printWindow = window.open(`/build/${build_id}/sheet`);
    printWindow.addEventListener('load', async function() {
        printWindow.print();
        await setTimeout(500);
        printWindow.close();
    });
}

async function onClickDuplicateBuild(build_id) {
    if (confirm("Are you sure you want to duplicate this build?") !== true) {
        return;
    }

    addLoadingTask("duplicate-build_" + build_id);
    await $.ajax(`/build/${build_id}/duplicate`);
    await fetchRecentBuildsPage();
    removeLoadingTask("duplicate-build_" + build_id);
}

async function onClickDeleteBuild(build_id) {
    if (confirm("Are you sure you want to delete this build?") !== true) {
        return;
    }

    addLoadingTask("delete-build_" + build_id);
    await $.ajax(`/build/${build_id}`, {"method": "DELETE"});
    await fetchRecentBuildsPage();
    removeLoadingTask("delete-build_" + build_id);
}

async function fetchRecentBuildsPage() {
    $("#recent-builds-list").children().remove();

    let builds = await $.ajax("/build");

    let entryList = $("#recent-builds-list");
    let entryTemplate = $($("#recent-build-entry-template").html());
    for (let i = 0; i < builds.length; i++) {
        let build = builds[i];
        let entry = entryTemplate.clone();

        entry.find("input[type=radio]").prop("checked", i == 0);

        entry.attr("build-id", build.id);

        entry.find("#entry-title").text(`${build.manufacturer} ${build.model}`);
        let created_at = Date.parse(build.created_at);
        entry.find("#entry-subtitle").text(`Created ${timeSince(created_at)} ago`);

        entry.find("#entry-price").text(`$${build.price}`);

        for (let cpu of build.processors) {
            entry.find("#entry-processors").append(`<p>${cpu.model}</p>`);
        }

        for (let mem of build.memory) {
            entry.find("#entry-memory").append(`<p>${mem.size / 1000} GB (DDR${mem.type} @ ${mem.clock})</p>`);
        }

        for (let disk of build.storage) {
            entry.find("#entry-storage").append(`<p>${disk.size / 1000} GB ${disk.form} ${disk.interface} ${disk.type}</p>`);
        }

        for (let gpu of build.graphics) {
            entry.find("#entry-graphics").append(`<p>${gpu.model}</p>`);
        }

        entry.find("a").prop("href", function(i, val) {
            return val.replace(/%ID%/g, build.id);
        });

        entry.find("#entry-set-price-button").click(() => onClickSetPrice(build.id));
        entry.find("#entry-generate-price-button").click(() => onClickGeneratePrice(build.id));
        entry.find("#entry-print-button").click(() => onClickPrintBuildsheet(build.id));
        entry.find("#entry-duplicate-button").click(() => onClickDuplicateBuild(build.id));
        entry.find("#entry-delete-button").click(() => onClickDeleteBuild(build.id));

        entryList.append(entry);
    }

    const urlParams = new URLSearchParams(window.location.search);
    let selectId = urlParams.get('select');
    if (selectId) {
        $(`.build-entry[build-id=${selectId}]`).find("input[type=radio]").prop("checked", true);
    }
}

window.addEventListener("load", function() {
    try {
        addLoadingTask("fetch-recent-builds");
        fetchRecentBuildsPage();
    } finally {
        removeLoadingTask("fetch-recent-builds");
    }
});