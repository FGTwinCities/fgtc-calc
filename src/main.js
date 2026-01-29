import './style.css';

window.addEventListener("load", function() {
    updateLoaderVisibility();
});

let loadingTasks = [];

function updateLoaderVisibility() {
    let modal = $("#page_loader_modal").get(0);

    if (loadingTasks.length > 0) {
        if (!modal.open) {
            modal.showModal();
        }
    } else {
        if (modal.open) {
            modal.close();
        }
    }
}

export function addLoadingTask(task) {
    loadingTasks.push(task);
    updateLoaderVisibility();
}

export function removeLoadingTask(task) {
    let index = loadingTasks.indexOf(task);
    if (index !== -1) {
        loadingTasks.splice(index, 1);
    }
    updateLoaderVisibility();
}
