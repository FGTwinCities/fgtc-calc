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

function onClickRemoveListedItem(button) {
    button.parentNode.remove();
}

function onClickAddListedItem(templateElementId, listElementId) {
    let element = document.getElementById(templateElementId).content.cloneNode(true);
    let container = document.getElementById(listElementId);
    container.appendChild(element);
}

function onCreateFormSubmit() {
    let formData = new FormData(document.getElementById("create-form"));
    let buildObj = {};

    // Collect values that can be pulled directly from the form into the build object
    buildObj["type"] = formData.get("type");
    buildObj["manufacturer"] = formData.get("manufacturer");
    buildObj["model"] = formData.get("model");

    // Collect processors
    buildObj["processors"] = [];
    let processorNames = formData.getAll("processor-name");
    for (let i = 0; i < processorNames.length; i++) {
        let processor = {};
        processor["manufacturer"] = ""; //TODO
        processor["model"] = processorNames[i];

        buildObj["processors"].push(processor);
    }

    // Collect memory modules
    buildObj["memory"] = [];
    let memoryType = formData.get("memory-type");
    let memoryUpgradable = Boolean(formData.get("memory-upgradable"));
    let memoryEcc = Boolean(formData.get("memory-ecc"));
    let memorySizes = formData.getAll("memory-size");
    let memorySizeUnits = formData.getAll("memory-size-unit");
    let memorySpeeds = formData.getAll("memory-speed");
    for (let i = 0; i < memorySizes.length; i++) {
        let module = {};
        module["type"] = memoryType;
        module["upgradable"] = memoryUpgradable;
        module["ecc"] = memoryEcc;
        module["size"] = normalizeDataSizeMegabytes(memorySizes[i], memorySizeUnits[i]);
        module["clock"] = parseInt(memorySpeeds[i]);

        buildObj["memory"].push(module);
    }

    // Collect storage disks
    buildObj["storage"] = [];
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

        buildObj["storage"].push(disk);
    }

    // Collect graphics cards
    buildObj["graphics"] = [];
    let graphicsNames = formData.getAll("gpu-name");
    let graphicsUpgradables = formData.getAll("gpu-upgradable");
    for (let i = 0; i < graphicsNames.length; i++) {
        let gpu = {};
        gpu["model"] = graphicsNames[i];
        gpu["upgradable"] = graphicsUpgradables[i];

        buildObj["graphics"].push(gpu);
    }

    // Collect networking information
    var wired = formData.get("networking-wired");
    buildObj["wired_networking"] = wired === "" ? null : parseInt(wired);
    var wireless = formData.get("networking-wireless");
    buildObj["wireless_networking"] = wireless === "" ? null : wireless;

    console.log("Converted build DTO:");
    console.log(JSON.stringify(buildObj));
}

window.onload = function() {
    // Automatically add a CPU, Memory Module, Disk and Battery on page load
    onClickAddListedItem('processor-template', 'processor-list');
    onClickAddListedItem('memory-template', 'memory-list');
    onClickAddListedItem('storage-template', 'storage-list');
    onClickAddListedItem('battery-template', 'battery-list');
}