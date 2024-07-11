let lightMode = true;
const baseUrl = window.location.origin;
const socket = io(baseUrl);
let isStreaming = false;


async function showBotLoadingAnimation() {
    await sleep(200);
    $(".loading-animation")[1].style.display = "inline-block";
    document.getElementById('send-button').disabled = true;
}

function hideBotLoadingAnimation() {
    $(".loading-animation")[1].style.display = "none";
    document.getElementById('send-button').disabled = false;
}

async function showUserLoadingAnimation() {
    await sleep(100);
    $(".loading-animation")[0].style.display = "flex";
}

function hideUserLoadingAnimation() {
    $(".loading-animation")[0].style.display = "none";
}

const cleanTextInput = (value) => {
    return value
        .trim()
        .replace(/[\n\t]/g, "")
        .replace(/<[^>]*>/g, "")
        .replace(/[<>&;]/g, "");
};

const sleep = (time) => new Promise((resolve) => setTimeout(resolve, time));

const scrollToBottom = () => {
    $("#chat-window").animate({
        scrollTop: $("#chat-window")[0].scrollHeight,
    });
};

const populateUserMessage = (userMessage) => {
    $("#message-input").val("");
    $("#message-list").append(
        `<div class='message-line my-text'><div class='message-box my-text${!lightMode ? " dark" : ""}'><div class='me'>${userMessage}</div></div></div>`
    );
    scrollToBottom();
};

const renderBotResponse = (data) => {
    if (!isStreaming) {
        $("#message-list").append(`<div class='message-line'><div class='message-box${!lightMode ? " dark" : ""}'></div></div>`);
        isStreaming = true;
    }

    const lastMessageBox = $("#message-list").children().last().find(".message-box");

    // Check if the last character is a space or not
    const isLastCharSpace = lastMessageBox.text().endsWith(" ") || lastMessageBox.text().length === 0;

    if (data === '.' || data === '?') {
        // Add a space if the last character is not a space (prevents multiple spaces)
        if (!isLastCharSpace) {
            lastMessageBox.append(" ");
        }
        lastMessageBox.append("\n");
    } else {
        lastMessageBox.append(isLastCharSpace ? data : " " + data); // Add space only if needed
    }

    if (data === '\n') {
        hideBotLoadingAnimation();
        isStreaming = false;
        scrollToBottom();
    } else if (data.includes("Here is the image you requested: ")) {
        // Handle image URL scenario (unchanged)
        const imageUrl = data.split("Here is the image you requested: ")[1];
        lastMessageBox.append(` <a href="${imageUrl}" target="_blank">${imageUrl}</a>`);
        hideBotLoadingAnimation();
        isStreaming = false;
    }

    scrollToBottom();
};




$(document).ready(function () {
    // Start the chat with send button disabled
    document.getElementById('send-button').disabled = false;

    // Listen for the "Enter" key being pressed in the input field
    $("#message-input").keyup(function (event) {
        let inputVal = cleanTextInput($("#message-input").val());

        if (event.keyCode === 13 && inputVal != "") {
            const message = inputVal;

            populateUserMessage(message);
            showBotLoadingAnimation();
            socket.emit('start_stream', { userMessage: message });
        }
    });

    // When the user clicks the "Send" button
    $("#send-button").click(function () {
        const message = cleanTextInput($("#message-input").val());

        populateUserMessage(message);
        showBotLoadingAnimation();
        socket.emit('start_stream', { userMessage: message });
    });

    // Reset chat
    $("#reset-button").click(function () {
        $("#message-list").empty();
        document.getElementById('send-button').disabled = true;
    });

    $("#light-dark-mode-switch").change(function () {
        $("body").toggleClass("dark-mode");
        $(".message-box").toggleClass("dark");
        $(".loading-dots").toggleClass("dark");
        $(".dot").toggleClass("dark-dot");
        $(".chat-card").toggleClass("dark-mode");
        lightMode = !lightMode;
    });


    $("#upload-button").click(function () {
        $("#file-upload").click();
    });

    const renderUploadResponse = (data) => {
        $("#message-list").append(`<div class='message-line'><div class='message-box${!lightMode ? " dark" : ""}'></div></div>`);

        const lastMessageBox = $("#message-list").children().last().find(".message-box");
        lastMessageBox.append(" " + data);
        scrollToBottom();
    };

    $("#file-upload").on("change", async function () {
        const files = this.files;
        const totalFiles = files.length;
        let uploadedFiles = 0;

        for (const file of files) {
            const formData = new FormData();
            formData.append('files', file);

            const progressBar = $(`<div class="progress mt-3">
                                <div class="progress-bar" role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
                              </div>`);
            const progressBarText = $(`<p>${file.name}</p>`);
            const progressContainer = $("<div class='progress-container'></div>").append(progressBarText, progressBar);
            $("#chat-window").append(progressContainer);

            const xhr = new XMLHttpRequest();
            xhr.open('POST', baseUrl + "/process-document", true);

            let progress = 0;
            const progressInterval = setInterval(() => {
                if (progress < 100) {
                    progress += 1;
                    progressBar.find('.progress-bar').width(progress + '%');
                    progressBar.find('.progress-bar').html(progress + '%');
                }
            }, 50);

            xhr.onload = async function () {
                clearInterval(progressInterval);
                uploadedFiles++;
                if (uploadedFiles === totalFiles) {
                    $(".progress-container").remove();
                    const response = JSON.parse(xhr.responseText);

                    // Render bot response
                    const combinedText = response.botResponse;
                    renderUploadResponse(combinedText);
                }
            };

            xhr.onerror = function () {
                console.error("Error occurred during file upload.");
            };

            xhr.send(formData);
        }
    });

    $("#profile-button").on("click", () => {
        $("#profile-upload").click();
    });

    $("#profile-upload").on("change", (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            $("#profile-image").attr("src", e.target.result);
        };
        reader.readAsDataURL(file);
    });


    socket.on('stream_response', function (msg) {
        console.log(msg.data);
        renderBotResponse(msg.data);
    });

});