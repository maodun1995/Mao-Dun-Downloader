let currentUrl = "";

async function fetchVideo() {

    const url =
        document.getElementById("url").value;

    if (!url) {

        alert(
            "Please paste a video link first."
        );

        return;
    }

    currentUrl = url;

    document.getElementById(
        "loading"
    ).style.display = "block";

    document.getElementById(
        "status"
    ).innerHTML = "";

    document.getElementById(
        "result"
    ).innerHTML = "";

    try {

        const response =
            await fetch("/fetch", {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    url: url
                })

            });

        const data =
            await response.json();

        document.getElementById(
            "loading"
        ).style.display = "none";

        if (data.success) {

            document.getElementById(
                "result"
            ).innerHTML = `

                <img
                    src="${data.thumbnail}"
                    class="preview">

                <h2>
                    ${data.title}
                </h2>

                <p>
                    Duration:
                    ${data.duration} sec
                </p>

                <button
                    onclick="downloadVideo()">

                    ⬇️ Download Video

                </button>

                <button
                    onclick="downloadMP3()">

                    🎵 Download MP3

                </button>

            `;

        } else {

            alert(
                data.error
            );

        }

    } catch (error) {

        document.getElementById(
            "loading"
        ).style.display = "none";

        alert(
            "Failed to fetch video."
        );

        console.error(error);

    }

}


async function downloadVideo() {

    const quality =
        document.getElementById(
            "quality"
        ).value;

    startProgress();

    document.getElementById(
        "status"
    ).innerHTML =
        "⏳ Downloading Video...";

    try {

        const response =
            await fetch("/download", {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({

                    url:
                        currentUrl,

                    quality:
                        quality

                })

            });

        const blob =
            await response.blob();

        const fileUrl =
            window.URL.createObjectURL(
                blob
            );

        const a =
            document.createElement(
                "a"
            );

        a.href =
            fileUrl;

        a.download =
            "video.mp4";

        document.body.appendChild(
            a
        );

        a.click();

        a.remove();

        window.URL.revokeObjectURL(
            fileUrl
        );

        finishProgress();

        document.getElementById(
            "status"
        ).innerHTML =
            "✅ Video Download Complete";

    } catch (error) {

        document.getElementById(
            "status"
        ).innerHTML =
            "❌ Video Download Failed";

        console.error(error);

    }

}


async function downloadMP3() {

    const mp3Quality =
        document.getElementById(
            "mp3_quality"
        ).value;

    startProgress();

    document.getElementById(
        "status"
    ).innerHTML =
        "🎵 Converting MP3...";

    try {

        const response =
            await fetch(
                "/download_mp3",
                {

                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({

                            url:
                                currentUrl,

                            mp3_quality:
                                mp3Quality

                        })

                }
            );

        const blob =
            await response.blob();

        const fileUrl =
            window.URL.createObjectURL(
                blob
            );

        const a =
            document.createElement(
                "a"
            );

        a.href =
            fileUrl;

        a.download =
            "audio.mp3";

        document.body.appendChild(
            a
        );

        a.click();

        a.remove();

        window.URL.revokeObjectURL(
            fileUrl
        );

        finishProgress();

        document.getElementById(
            "status"
        ).innerHTML =
            "✅ MP3 Download Complete";

    } catch (error) {

        document.getElementById(
            "status"
        ).innerHTML =
            "❌ MP3 Download Failed";

        console.error(error);

    }

}


function startProgress() {

    let width = 0;

    const bar =
        document.getElementById(
            "progressBar"
        );

    const interval =
        setInterval(() => {

            if (width >= 95) {

                clearInterval(
                    interval
                );

            } else {

                width += 5;

                bar.style.width =
                    width + "%";

            }

        }, 500);

}


function finishProgress() {

    const bar =
        document.getElementById(
            "progressBar"
        );

    bar.style.width =
        "100%";

    setTimeout(() => {

        bar.style.width =
            "0%";

    }, 1500);

}


function batchDownload() {

    const links =
        document
            .getElementById(
                "batch_urls"
            )
            .value
            .trim();

    if (!links) {

        alert(
            "Paste links first."
        );

        return;
    }

    const urlList =
        links.split("\n");

    alert(

        "Batch Download Ready\n\n" +

        "Links Found: " +

        urlList.length +

        "\n\n" +

        "Current version downloads one by one."

    );

}