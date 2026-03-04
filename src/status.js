import {$} from "jquery";

async function getAndShowServerMessages() {
    let messages = await $.ajax("/status/messages");

    for (let i = 0; i < messages.length; ++i) {
        showMessage(messages[i]["message"]);
    }
}

function showMessage(message) {
    let alert = $($("#alert-template").html()).clone();
    alert.find("#message").text(message);
    $("#alert-list").append(alert);
}

window.addEventListener("load", async function() {
    await getAndShowServerMessages();
});