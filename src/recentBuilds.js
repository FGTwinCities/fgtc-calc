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
        await $.ajax(`/price/${build_id}`)
    } catch(err) {
        console.log(err);
        alert("Failed to price build. Details are in log.")
    }

    await fetchRecentBuildsPage();
    $(`.build-entry[build-id=${build_id}]`).find("input[type=radio]").prop("checked", true);
}

async function onClickSetPrice(build_id) {
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
}

function onClickPrintBuildsheet(build_id) {
    var printWindow = window.open(`/build/${build_id}/sheet`);
    printWindow.addEventListener('load', async function() {
        printWindow.print();
        await setTimeout(500);
        printWindow.close();
    });
}

async function onClickDeleteBuild(build_id) {
    if (confirm("Are you sure you want to delete this build?") != true) {
        return;
    }

    await $.ajax(`/build/${build_id}`, {"method": "DELETE"});
    fetchRecentBuildsPage();
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
        entry.find("#entry-delete-button").click(() => onClickDeleteBuild(build.id));

        entryList.append(entry);
    }

    const urlParams = new URLSearchParams(window.location.search);
    let selectId = urlParams.get('select');
    if (selectId) {
        $(`.build-entry[build-id=${selectId}]`).find("input[type=radio]").prop("checked", true);
    }
}

window.onload = function() {
    fetchRecentBuildsPage();
};