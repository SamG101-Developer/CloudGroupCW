const timerElement = document.getElementById("timer");

let time = 10

const interval = setInterval(() => {
    if (time < 0) {
        clearInterval(interval);
        timerElement.innerText = "Time up!"
    }

    timerElement.innerText = (10 - time).toString();
    time -= 1;
}, 1000)
