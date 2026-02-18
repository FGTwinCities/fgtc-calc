import {$} from "jquery";

import {onProcessorSearchKeyup, onGraphicsSearchKeyup} from "./search.js";
import {addLoadingTask, removeLoadingTask} from "../main.js";

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

function onBatteryPercentChange(event) {
    let batteryFieldset = $(event.target).parentsUntil(".build-list-item").parent();
    let value = Math.max(Math.min(event.target.value, 100.0), 0.0);
    batteryFieldset.find("#battery-remainingcapacity").val(Math.floor(1000 * (value / 100.0)));
    batteryFieldset.find("#battery-designcapacity").val(1000);
}

function onBatteryCapacityChange(event) {
    let batteryFieldset = $(event.target).parentsUntil(".build-list-item").parent();
    let design = batteryFieldset.find("#battery-designcapacity").val();
    let remain = batteryFieldset.find("#battery-remainingcapacity").val();
    batteryFieldset.find("#battery-percent").val((remain / design) * 100.0);
}

function addTemplateListItem(templateElementId, listElementId) {
    let template = $($("#"+templateElementId).html()).clone();

    template.find("#remove-button").click(() => template.remove());
    template.find("#processor-search").keyup(onProcessorSearchKeyup);
    template.find("#gpu-search").keyup(onGraphicsSearchKeyup);
    template.find("#battery-percent").change(onBatteryPercentChange);
    template.find("#battery-designcapacity").change(onBatteryCapacityChange);
    template.find("#battery-remainingcapacity").change(onBatteryCapacityChange);

    let form = new FormData($("#create-form").get(0));
    template.find("#processor-upgradable").prop("checked", form.get("type") !== "laptop");
    template.find("#gpu-upgradable").prop("checked", form.get("type") !== "laptop");

    $("#"+listElementId).append(template);
    return template
}

export function convertFormToDto() {
    let form = document.getElementById("create-form");
    let formData = new FormData(form);
    let dto = {};

    // Collect values that can be pulled directly from the form into the build object
    dto["type"] = formData.get("type") == "" ? null : formData.get("type");
    dto["manufacturer"] = formData.get("manufacturer") == "" ? null : formData.get("manufacturer");
    dto["model"] = formData.get("model") == "" ? null : formData.get("model");
    dto["operating_system"] = formData.get("operating-system") == "" ? null : formData.get("operating-system");
    dto["notes"] = formData.get("notes") == "" ? null : formData.get("notes");

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
    dto["display"] = null;
    if (dto["type"] === "laptop" || dto["type"] === "other") {
        let display = {};
        display["size"] = parseFloat(formData.get("display-size"));
        display["resolution"] = {
            "x": parseInt(formData.get("display-resolution-horizontal")),
            "y": parseInt(formData.get("display-resolution-vertical")),
        };
        display["refresh_rate"] = parseInt(formData.get("display-refreshrate"));
        display["touchscreen"] = Boolean(formData.get("display-touch"));
        dto["display"] = display;
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

        dto["webcam"] = Boolean(formData.get("webcam"));
        dto["microphone"] = Boolean(formData.get("microphone"));
    }

    // Collect networking information
    var wired = formData.get("networking-wired");
    dto["wired_networking"] = wired === "none" ? null : parseInt(wired);
    var wireless = formData.get("networking-wireless");
    dto["wireless_networking"] = wireless === "none" ? null : wireless;
    dto["bluetooth"] = Boolean(formData.get("bluetooth"));

    console.log("Converted build DTO:");
    console.log(JSON.stringify(dto));

    return dto;
}

export function fillFormFromDto(dto) {
    $("input[name=type][value=" + dto["type"] + "]").prop("checked", true);
    updateVisibleFields();

    $("input[name=manufacturer]").val(dto["manufacturer"]);
    $("input[name=model]").val(dto["model"]);
    $("input[name=operating-system]").val(dto["operating_system"]);
    $("textarea[name=notes]").val(dto["notes"]);

    // Fill processor information
    for (let i = 0; i < dto["processors"].length; i++) {
        let field = addTemplateListItem('processor-template', 'processor-list');
        field.find("input[name=processor-name]").val(dto["processors"][i]["model"]);
        field.find("input[name=processor-upgradable]").prop("checked", dto["processor_associations"][i]["upgradable"]);
    }

    // Fill memory information
    for (let i = 0; i < dto["memory"].length; i++) {
        let field = addTemplateListItem('memory-template', 'memory-list');
        let megabytes = dto["memory"][i]["size"];
        field.find("input[name=memory-size]").val(megabytes);
        field.find("select[name=memory-size-unit]").val("mb"); //TODO: Pick and convert units
        field.find("input[name=memory-speed]").val(dto["memory"][i]["clock"]);

        $("input[name=memory-type][value=" + dto["memory"][0]["type"] + "]").prop("checked", true);
        $("input[name=memory-upgradable]").prop("checked", dto["memory"][0]["upgradable"]);
        $("input[name=memory-ecc]").prop("checked", dto["memory"][0]["ecc"]);
    }

    // Fill storage information
    for (let i = 0; i < dto["storage"].length; i++) {
        let field = addTemplateListItem('storage-template', 'storage-list');
        let megabytes = dto["storage"][i]["size"];
        field.find("input[name=storage-disk-size]").val(megabytes);
        field.find("select[name=storage-disk-size-unit]").val("mb"); //TODO: Pick and convert units
        field.find("select[name=storage-disk-type]").val(dto["storage"][i]["type"]);
        field.find("select[name=storage-disk-form]").val(dto["storage"][i]["form"]);
        field.find("select[name=storage-disk-interface]").val(dto["storage"][i]["interface"]);
        field.find("input[name=storage-disk-upgradable]").prop("checked", dto["storage"][i]["upgradable"]);
    }

    // Fill graphics information
    for (let i = 0; i < dto["graphics"].length; i++) {
        let field = addTemplateListItem('gpu-template', 'gpu-list');
        field.find("input[name=gpu-name]").val(dto["graphics"][i]["model"]);
        field.find("input[name=gpu-upgradable]").prop("checked", dto["graphics_associations"][i]["upgradable"]);
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
    batteryList.find("fieldset").remove();
    let batteryTemplate = $($("#battery-template").html());
    for (let i = 0; i < dto["batteries"].length; i++) {
        let field = batteryTemplate.clone();
        field.find("input[name=battery-designcapacity]").val(dto["batteries"][i]["design_capacity"]);
        field.find("input[name=battery-remainingcapacity]").val(dto["batteries"][i]["remaining_capacity"]);
        batteryList.append(field);
    }

    $("input[name=webcam]").prop("checked", dto["webcam"]);
    $("input[name=microphone]").prop("checked", dto["microphone"]);

    // Fill networking information
    $("input[name=networking-wired][value=" + (dto["wired_networking"] == null ? "none" : dto["wired_networking"]) + "]").prop("checked", true);
    $("input[name=networking-wireless][value=" + (dto["wireless_networking"] == null ? "none" : dto["wireless_networking"]) + "]").prop("checked", true);
    $("input[name=bluetooth]").prop("checked", dto["bluetooth"]);
}

function validateFormItem(item, message, errors) {
    if (item === "" || item === null) {
        errors.push(message);
        return false;
    }
    return true;
}

function validateFormList(list, message, errors) {
    for (let i = 0; i < list.length; i++) {
        if (!validateFormItem(list[i], message, errors)) { return false; }
    }

    return true;
}

function validateForm() {
    let formElement = document.getElementById("create-form");
    let form = new FormData(formElement);

    let errors = [];

    validateFormItem(form.get("type"), "Computer Type is required", errors);

    validateFormList(form.getAll("processor-name"), "Processor Model is required", errors);

    validateFormItem(form.get("memory-type"), "Memory Type is required", errors);
    validateFormList(form.getAll("memory-size"), "Memory Size is required", errors);
    validateFormList(form.getAll("memory-size-unit"), "Memory Size Unit is required", errors);
    validateFormList(form.getAll("memory-speed"), "Memory Speed is required", errors);

    validateFormList(form.getAll("storage-disk-type"), "Storage Disk Type is required", errors);
    validateFormList(form.getAll("storage-disk-form"), "Storage Disk Form is required", errors);
    validateFormList(form.getAll("storage-disk-interface"), "Storage Disk Interface is required", errors);
    validateFormList(form.getAll("storage-disk-size"), "Storage Disk Size is required", errors);
    validateFormList(form.getAll("storage-disk-size-unit"), "Storage Disk Size Unit is required", errors);

    validateFormList(form.getAll("gpu-name"), "Graphics Card Model is required");

    let type = form.get("type")
    if (type === "laptop" || type === "other") {
        validateFormItem("display-size", "Display Size is required", errors);
        validateFormItem("display-resolution-horizontal", "Display Resolution is required", errors);
        validateFormItem("display-resolution-vertical", "Display Resolution is required", errors);
        validateFormItem("display-refreshrate", "Display Refresh Rate is required", errors);

        validateFormList(form.getAll("battery-designcapacity"), "Battery Design Capacity is required", errors);
        validateFormList(form.getAll("battery-remainingcapacity"), "Battery Remaining Capacity is required", errors);
    }

    validateFormItem(form.get("networking-wired"), "Wired Networking Type is required", errors);
    validateFormItem(form.get("networking-wireless"), "Wireless Networking Type is required", errors);

    if (errors.length > 0) {
        alert(errors);
        return false;
    } else {
        return true;
    }
}

async function onCreateFormSubmit() {
    if (!validateForm()) { return; }

    let dto = convertFormToDto();

    var url = "/build";
    let settings = {
        method: "POST",
        data: JSON.stringify(dto),
        dataType: "json",
    };

    const urlParams = new URLSearchParams(window.location.search);
    let editId = urlParams.get('edit');
    if (editId) {
        url = `/build/${editId}`;
        settings.method = "PATCH";
    }

    try {
        addLoadingTask("submit-build");
        let response = await $.ajax(url, settings);
        window.location.href = `/?select=${response['id']}`;
    } catch(err) {
        console.log(err);
        alert("Failed to submit build: " + err.responseText);
    } finally {
        removeLoadingTask("submit-build");
    }
}

function updateVisibleFields() {
    let form = new FormData(document.getElementById("create-form"));
    let isOther = form.get("type") === "other";
    let isAny = !(form.get("type") === "" || form.get("type") === null);
    let isDesktop = form.get("type") === "desktop";
    let isLaptop = form.get("type") === "laptop";
    let isComputer = isDesktop || isLaptop;

    $("#fieldset-info").prop('hidden', !isAny)
    $("#fieldset-processor").prop('hidden', !(isComputer || isOther));
    $("#fieldset-memory").prop('hidden', !(isComputer || isOther));
    $("#fieldset-storage").prop('hidden', !(isComputer || isOther));
    $("#fieldset-gpu").prop('hidden', !(isComputer || isOther));
    $("#fieldset-display").prop('hidden', !(isLaptop || isOther));
    $("#fieldset-battery").prop('hidden', !(isLaptop || isOther));
    $("#fieldset-webcam").prop('hidden', !(isLaptop || isOther))
    $("#fieldset-networking").prop('hidden', !(isComputer || isOther));
    $("#fieldset-notes").prop('hidden', !isAny);

    $("#processor-upgradable").prop("checked", !isLaptop);
    $("#memory-upgradable").prop("checked", !isLaptop);
    $("#gpu-upgradable").prop("checked", !isLaptop);

}

window.addEventListener("load", async function() {
    // Bind events for page
    $("input[name=type]").change(updateVisibleFields);
    $("#add-processor-button").click(() => addTemplateListItem('processor-template', 'processor-list'));
    $("#add-memory-button").click(() => addTemplateListItem('memory-template', 'memory-list'));
    $("#add-storage-button").click(() => addTemplateListItem('storage-template', 'storage-list'));
    $("#add-gpu-button").click(() => addTemplateListItem('gpu-template', 'gpu-list'));
    $("#add-battery-button").click(() => addTemplateListItem('battery-template', 'battery-list'));
    $("#submit-button").click(onCreateFormSubmit);

    const urlParams = new URLSearchParams(window.location.search);
    let editId = urlParams.get('edit');
    if (editId) {
        addLoadingTask("load-build");
        fillFormFromDto(await $.ajax(`/build/${editId}`));
        removeLoadingTask("load-build");
    } else {
        // Automatically add a CPU, Memory Module, Disk and Battery on page load
        addTemplateListItem('processor-template', 'processor-list');
        addTemplateListItem('memory-template', 'memory-list');
        addTemplateListItem('storage-template', 'storage-list');
        addTemplateListItem('battery-template', 'battery-list');

        updateVisibleFields();
    }
});

window.convertFormToDto = convertFormToDto;
window.fillFormFromDto = fillFormFromDto;