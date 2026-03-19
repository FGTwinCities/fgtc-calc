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
        let pricingData = await $.ajax(`/price/${build_id}`);
        showPricingBreakdown(pricingData, build_id);
    } catch(err) {
        console.log(err);
        alert("Failed to price build: " + err.responseText);
    }

    await fetchRecentBuildsPage();
    $(`.build-entry[build-id=${build_id}]`).find("input[type=radio]").prop("checked", true);
    removeLoadingTask("generate-price_" + build_id);
}

async function setBuildPrice(build_id, price) {
    addLoadingTask("set-price_" + build_id);
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

async function onClickSetPrice(build_id) {
    let price = parseFloat($(`.build-entry[build-id=${build_id}]`).find("#entry-set-price-field").val());
    await setBuildPrice(build_id, price);
}

async function onClickBreakdownSetPrice(event) {
    let field = $(event.target);
    let dialog = field.parents("dialog");
    let buildId = dialog.attr("build-id");
    let price = parseFloat(dialog.find("#pricing-breakdown-price").val());
    await setBuildPrice(buildId, price);
    dialog.get(0).close();

    setTimeout(function () {
        dialog.remove();
    }, 1000);
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

async function onFilterChanged() {
    addLoadingTask("refresh");
    await fetchRecentBuildsPage();
    removeLoadingTask("refresh");
}

function formatMacType(type) {
    if (type === "macbook") { return "Macbook"; }
    if (type === "macbook_air") { return "Macbook Air"; }
    if (type === "macbook_pro") { return "Macbook Pro"; }
    if (type === "macbook_neo") { return "Macbook Neo"; }
    if (type === "imac") { return "iMac"; }
    if (type === "imac_pro") { return "iMac Pro"; }
    if (type === "mac_pro") { return "Mac Pro"; }
    if (type === "mac_mini") { return "Mac Mini"; }
    if (type === "mac_studio") { return "Mac Studio"; }
    return type;
}

function formatComponentLabel(component) {
    if ('item' in component) {
        let item = component['item'];
        if ('model' in item) {
            return `${item['model']}`;
        } else if ('ecc' in item) {
            return `${item['size'] / 1000.0}GB DDR${item['type']}-${item['clock']}`;
        } else if ('form' in item) {
            return `${item['size'] / 1000.0}GB ${item['form']} ${item['interface']} ${item['type']}`;
        } else if ('resolution' in item) {
            return `${item['size']}" ${item['resolution']['x']}x${item['resolution']['y']}@${item['refresh_rate']}Hz Display`;
        } else if ('remaining_capacity' in item) {
            let capacity = item['remaining_capacity'] / item['design_capacity'] * 100;
            return `Battery (${capacity.toFixed(1)}% Capacity)`
        } else {
            return "Other build component";
        }
    } else if ('comment' in component) {
        return component['comment'];
    }
    return "";
}

function formatPrice(price) {
    return `$${price.toFixed(2)}`;
}

function formatPriceDelta(delta) {
    if (delta > 0) {
        return `<span class="text-success">+ ${formatPrice(delta)}</span>`;
    } else if (delta < 0) {
        return `<span class="text-error">- ${formatPrice(Math.abs(delta))}</span>`;
    } else {
        return formatPrice(delta);
    }
}

function showPricingBreakdown(data, buildId) {
    let modal = $($("#pricing-breakdown-template").html()).clone();

    modal.attr('build-id', buildId);

    let rowTemplate = $(modal.find("#row-template").html());
    let components = data["component_pricing"];
    var price = 0.0;
    for (let i = 0; i < components.length; i++) {
        let row = rowTemplate.clone();
        row.find("#label").text(formatComponentLabel(components[i]));

        if ('price' in components[i]) {
            let compPrice = components[i]['price'];
            row.find("#price-delta").html(formatPriceDelta(compPrice));
            price += compPrice;
        }

        row.find("#price-total").html(formatPrice(price));

        modal.find("#table").append(row);
    }

    modal.find("#pricing-breakdown-price").val(data['price']);
    modal.find("#pricing-breakdown-setprice-btn").click(onClickBreakdownSetPrice);

    $("body").append(modal);
    modal.get(0).showModal();
}

async function fetchRecentBuildsPage() {
    $("#recent-builds-list").children().remove();

    let modern = $("input[name=recents-modern]").prop("checked");
    let mac = $("input[name=recents-mac]").prop("checked");

    var url = "/build";
    if (!modern && mac) {
        url = "/build/mac"
    } else if (modern && !mac) {
        url = "/build/modern"
    } else if (!modern && !mac) {
        return;
    }

    let builds = await $.ajax(url);

    let entryList = $("#recent-builds-list");
    let entryTemplate = $($("#recent-build-entry-template").html());
    for (let i = 0; i < builds.length; i++) {
        let build = builds[i];
        let entry = entryTemplate.clone();

        entry.find("input[type=radio]").prop("checked", i == 0);

        entry.attr("build-id", build.id);

        if (build.class_type == "modern") {
            entry.find("#entry-title").text(`${build.manufacturer} ${build.model}`);
        } else if (build.class_type == "mac") {
            entry.find("#entry-title").text(`${build.year} ${formatMacType(build.mac_type)}`);
        }

        entry.find("#entry-subtitle").text(build.id.substring(0, 8));

        let created_at = Date.parse(build.created_at);
        entry.find("#entry-timestamp").text(`Created ${timeSince(created_at)} ago`);

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
            val = val.replace(/%ID%/g, build.id);
            val = val.replace(/%BUILDCLASS%/g, build.class_type);
            return val;
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
    $("#recents-filter").find("input").on("change", onFilterChanged)
    try {
        addLoadingTask("fetch-recent-builds");
        fetchRecentBuildsPage();
    } finally {
        removeLoadingTask("fetch-recent-builds");
    }
});