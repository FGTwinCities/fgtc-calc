import {onProcessorSearchKeyup, onGraphicsSearchKeyup} from "./search.js";

function normalizeDataSizeMegabytes(quantity, unit) {
    quantity = parseInt(quantity);
    switch (unit.toLowerCase()) {
        case "kb":
            return Math.round(quantity / 1000);
        case "mb":
            return quantity;
        case "gb":
            return quantity * 1000;
        case "tb":
            return quantity * 1000 * 1000;
    }
}

function addTemplateListItem(templateElementId, listElementId) {
    let template = $($("#"+templateElementId).html()).clone();

    template.children("#remove-button").click(() => template.remove());
    template.children("#processor-search").keyup(onProcessorSearchKeyup);
    template.children("#gpu-search").keyup(onGraphicsSearchKeyup);

    $("#"+listElementId).append(template);
}

function convertFormToDto() {
    let form = document.getElementById("create-form");
    let formData = new FormData(form);
    let dto = {};

    // Collect values that can be pulled directly from the form into the build object
    dto["type"] = formData.get("type");
    dto["manufacturer"] = formData.get("manufacturer");
    dto["model"] = formData.get("model");

    // Collect processors
    dto["processors"] = [];
    let processorNames = formData.getAll("processor-name");
    let processorUpgradables = formData.getAll("processor-upgradable");
    for (let i = 0; i < processorNames.length; i++) {
        var processor = {};
        processor["model"] = processorNames[i];
        processor["upgradable"] = Boolean(processorUpgradables[i]);

        dto["processors"].push(processor);
    }

    // Collect memory modules
    dto["memory"] = [];
    let memoryType = formData.get("memory-type");
    let memoryUpgradable = Boolean(formData.get("memory-upgradable"));
    let memoryEcc = Boolean(formData.get("memory-ecc"));
    let memoryEmpties = formData.getAll("memory-emptyslot");
    let memorySizes = formData.getAll("memory-size");
    let memorySizeUnits = formData.getAll("memory-size-unit");
    let memorySpeeds = formData.getAll("memory-speed");
    for (let i = 0; i < memorySizes.length; i++) {
        var module = {};
        module["type"] = memoryType;
        module["upgradable"] = memoryUpgradable;
        module["ecc"] = memoryEcc;
        module["size"] = normalizeDataSizeMegabytes(memorySizes[i], memorySizeUnits[i]);
        module["clock"] = parseInt(memorySpeeds[i]);

        // Ignore everything if empty slot is selected
        if (memoryEmpties[i]) {
            module = null;
        }

        dto["memory"].push(module);
    }

    // Collect storage disks
    dto["storage"] = [];
    let storageTypes = formData.getAll("storage-disk-type");
    let storageUpgradables = formData.getAll("storage-disk-upgradable");
    let storageSizes = formData.getAll("storage-disk-size");
    let storageSizeUnits = formData.getAll("storage-disk-size-unit");
    let storageForms = formData.getAll("storage-disk-form");
    let storageInterfaces = formData.getAll("storage-disk-interface");
    for (let i = 0; i < storageTypes.length; i++) {
        let disk = {};
        disk["type"] = storageTypes[i];
        disk["upgradable"] = Boolean(storageUpgradables[i]);
        disk["size"] = normalizeDataSizeMegabytes(storageSizes[i], storageSizeUnits[i]);
        disk["form"] = storageForms[i];
        disk["interface"] = storageInterfaces[i];

        dto["storage"].push(disk);
    }

    // Collect graphics cards
    dto["graphics"] = [];
    let graphicsNames = formData.getAll("gpu-name");
    let graphicsUpgradables = formData.getAll("gpu-upgradable");
    for (let i = 0; i < graphicsNames.length; i++) {
        let gpu = {};
        gpu["model"] = graphicsNames[i];
        gpu["upgradable"] = Boolean(graphicsUpgradables[i]);

        dto["graphics"].push(gpu);
    }

    // Collect display information
    dto["display"] = []
    if (dto["type"] === "laptop" || dto["type"] === "other") {
        let display = {};
        display["size"] = parseFloat(formData.get("display-size"));
        display["resolution"] = {
            "x": parseInt(formData.get("display-resolution-horizontal")),
            "y": parseInt(formData.get("display-resolution-vertical")),
        };
        display["refresh_rate"] = parseInt(formData.get("display-refreshrate"));
        display["touchscreen"] = Boolean(formData.get("display-touch"));
        dto["display"] = [display];
    }

    // Collect battery information
    dto["batteries"] = []
    if (dto["type"] === "laptop" || dto["type"] === "other") {
        let design = formData.getAll("battery-designcapacity");
        let remain = formData.getAll("battery-remainingcapacity");
        for (let i = 0; i < design.length; i++) {
            let battery = {};
            battery["design_capacity"] = parseInt(design[i]);
            battery["remaining_capacity"] = parseInt(remain[i]);
            dto["batteries"].push(battery);
        }
    }

    // Collect networking information
    var wired = formData.get("networking-wired");
    dto["wired_networking"] = wired === "none" ? null : parseInt(wired);
    var wireless = formData.get("networking-wireless");
    dto["wireless_networking"] = wireless === "none" ? null : wireless;

    console.log("Converted build DTO:");
    console.log(JSON.stringify(dto));

    return dto;
}

function fillFormFromDto(dto) {
    $("input[name=type][value=" + dto["type"] + "]").prop("checked", true);
    updateVisibleFields();

    // Fill processor information
    let processorList = $("#processor-list");
    processorList.children("fieldset").remove(); // Wipe processor list
    let processorTemplate = $($("#processor-template").html());
    for (let i = 0; i < dto["processors"].length; i++) {
        let field = processorTemplate.clone();
        field.children("input[name=processor-name]").val(dto["processors"][i]["model"]);
        field.children("input[name=processor-upgradable]").val(dto["processors"][i]["upgradable"]);
        processorList.append(field);
    }

    // Fill memory information
    let memoryList = $("#memory-list");
    memoryList.children("fieldset").remove();
    let memoryTemplate = $($("#memory-template").html());
    for (let i = 0; i < dto["memory"].length; i++) {
        let field = memoryTemplate.clone();
        let megabytes = dto["memory"][i]["size"];
        field.children("input[name=memory-size]").val(megabytes);
        field.children("select[name=memory-size-unit]").val("mb"); //TODO: Pick and convert units
        field.children("input[name=memory-speed]").val(dto["memory"][i]["clock"]);

        $("input[name=memory-type][value=" + dto["memory"][0]["type"] + "]").prop("checked", true);
        $("input[name=memory-upgradable]").prop("checked", dto["memory"][0]["upgradable"]);
        $("input[name=memory-ecc]").prop("checked", dto["memory"][0]["ecc"]);
        memoryList.append(field);
    }

    // Fill storage information
    let storageList = $("#storage-list");
    storageList.children("fieldset").remove();
    let storageTemplate = $($("#storage-template").html());
    for (let i = 0; i < dto["storage"].length; i++) {
        let field = storageTemplate.clone();
        let megabytes = dto["storage"][i]["size"];
        field.children("input[name=storage-disk-size]").val(megabytes);
        field.children("select[name=storage-disk-size-unit]").val("mb"); //TODO: Pick and convert units
        field.children("input[name=storage-disk-type][value=" + dto["storage"][i]["type"] + "]").prop("checked", true);
        field.children("select[name=storage-disk-form]").val(dto["storage"][i]["form"]);
        field.children("select[name=storage-disk-interface]").val(dto["storage"][i]["interface"]);
        field.children("input[name=storage-disk-upgradable]").prop("checked", dto["storage"][i]["upgradable"]);
        storageList.append(field);
    }

    // Fill graphics information
    let graphicsList = $("#gpu-list");
    graphicsList.children("fieldset").remove();
    let graphicsTemplate = $($("#gpu-template").html());
    for (let i = 0; i < dto["graphics"].length; i++) {
        let field = graphicsTemplate.clone();
        field.children("input[name=gpu-name]").val(dto["graphics"][i]["model"]);
        field.children("input[name=gpu-upgradable]").val(dto["graphics"][i]["upgradable"]);
        graphicsList.append(field);
    }

    // Fill display information
    var display_size = NaN;
    var display_resolution_x = NaN;
    var display_resolution_y = NaN;
    var display_refreshrate = NaN;
    var display_touchscreen = false;

    if (dto["display"].length > 0) {
        display_size = dto["display"][0]["size"];
        display_resolution_x = dto["display"][0]["resolution"]["x"];
        display_resolution_y = dto["display"][0]["resolution"]["y"];
        display_refreshrate = dto["display"][0]["refresh_rate"];
        display_touchscreen = dto["display"][0]["touchscreen"];
    }

    $("input[name=display-size]").val(display_size);
    $("input[name=display-resolution-horizontal]").val(display_resolution_x);
    $("input[name=display-resolution-vertical]").val(display_resolution_y);
    $("input[name=display-refreshrate]").val(display_refreshrate);
    $("input[name=display-touch]").prop("checked",  display_touchscreen);

    // Fill battery information
    let batteryList = $("#battery-list");
    batteryList.children("fieldset").remove();
    let batteryTemplate = $($("#battery-template").html());
    for (let i = 0; i < dto["batteries"].length; i++) {
        let field = batteryTemplate.clone();
        field.children("input[name=battery-designcapacity]").val(dto["batteries"][i]["design_capacity"]);
        field.children("input[name=battery-remainingcapacity]").val(dto["batteries"][i]["remaining_capacity"]);
        batteryList.append(field);
    }

    // Fill networking information
    $("input[name=networking-wired][value=" + (dto["wired_networking"] == null ? "none" : dto["wired_networking"]) + "]").prop("checked", true);
    $("input[name=networking-wireless][value=" + (dto["wireless_networking"] == null ? "none" : dto["wireless_networking"]) + "]").prop("checked", true);
}

function onCreateFormSubmit() {
    let dto = convertFormToDto();

    fetch("/build", {
        method: "POST",
        body: JSON.stringify(dto),
        headers: {
            "Content-Type": "application/json; charset=UTF-8"
        }
    }).then(onSubmitResponse);
}

async function onSubmitResponse(response) {
    let dto = await response.json();
    if (response.ok) {
        window.location.href = "/build/" + dto["id"];
    } else {
        let p = document.createElement('p');
        p.innerText += "Error sending build: ";
        p.innerText += dto["detail"];
        document.body.append(p);
    }
}

function onFormChanged() {
    updateVisibleFields();
}

function updateVisibleFields() {
    let form = new FormData(document.getElementById("create-form"));
    let isOther = form.get("type") === "other";

    let isDesktop = form.get("type") === "desktop";
    let isLaptop = form.get("type") === "laptop";
    let isComputer = isDesktop || isLaptop;

    $("#fieldset-processor").prop('hidden', !(isComputer || isOther));
    $("#fieldset-memory").prop('hidden', !(isComputer || isOther));
    $("#fieldset-storage").prop('hidden', !(isComputer || isOther));
    $("#fieldset-gpu").prop('hidden', !(isComputer || isOther));
    $("#fieldset-display").prop('hidden', !(isLaptop || isOther));
    $("#fieldset-battery").prop('hidden', !(isLaptop || isOther));
    $("#fieldset-networking").prop('hidden', !(isComputer || isOther));
}

window.onload = function() {
    // Bind events for page
    $("#create-form").change(onFormChanged);
    $("#add-processor-button").click(() => addTemplateListItem('processor-template', 'processor-list'));
    $("#add-memory-button").click(() => addTemplateListItem('memory-template', 'memory-list'));
    $("#add-storage-button").click(() => addTemplateListItem('storage-template', 'storage-list'));
    $("#add-gpu-button").click(() => addTemplateListItem('gpu-template', 'gpu-list'));
    $("#add-battery-button").click(() => addTemplateListItem('battery-template', 'battery-list'));
    $("#submit-button").click(onCreateFormSubmit);

    // Automatically add a CPU, Memory Module, Disk and Battery on page load
    addTemplateListItem('processor-template', 'processor-list');
    addTemplateListItem('memory-template', 'memory-list');
    addTemplateListItem('storage-template', 'storage-list');
    addTemplateListItem('battery-template', 'battery-list');

    updateVisibleFields();
}