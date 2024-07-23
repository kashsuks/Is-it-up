document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("automation-form");
    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const urls = document.getElementById("urls").value.split("\n").map(url => url.trim()).filter(url => url);
        const scheduleTime = document.getElementById("schedule_time").value;

        if (urls.length > 0 && scheduleTime) {
            const automationData = { urls, scheduleTime };
            localStorage.setItem("automationData", JSON.stringify(automationData));
            alert("Automation scheduled successfully!");

            scheduleChecks();
        } else {
            alert("Please fill in all fields.");
        }
    });

    function scheduleChecks() {
        const automationData = JSON.parse(localStorage.getItem("automationData"));
        if (automationData) {
            const { urls, scheduleTime } = automationData;
            const [hours, minutes] = scheduleTime.split(":").map(Number);

            const now = new Date();
            let scheduledTime = new Date();
            scheduledTime.setHours(hours, minutes, 0, 0);

            if (scheduledTime < now) {
                scheduledTime.setDate(scheduledTime.getDate() + 1); // schedule for the next day if time has passed for today
            }

            const timeUntilCheck = scheduledTime - now;

            setTimeout(() => {
                urls.forEach(url => {
                    fetch(`/check_url?url=${encodeURIComponent(url)}`)
                        .then(response => response.json())
                        .then(data => {
                            alert(`Website: ${url}\nStatus: ${data.status}`);
                        })
                        .catch(error => {
                            alert(`Failed to check website: ${url}`);
                        });
                });

                // Reschedule the next check for the same time the next day
                scheduleChecks();
            }, timeUntilCheck);
        }
    }

    // Schedule checks if automation data is present in local storage
    if (localStorage.getItem("automationData")) {
        scheduleChecks();
    }
});
