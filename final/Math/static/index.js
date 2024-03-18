window.onload = function() {
        alert("Welcome to the game!");
    };
    document.getElementById("start-form").addEventListener("submit", function(event) {
        event.preventDefault(); // Prevent the default form submission
        startGame();
    });

    function startGame() {
        var timeLeft = 60;
        var timer = setInterval(function() {
            timeLeft--;
            document.getElementById("time-left").textContent = timeLeft;
            if (timeLeft <= 0) {
                clearInterval(timer);
                document.getElementById("question-form").style.display = "none";
                document.getElementById("score").style.display = "block";
                // Here, you can calculate and display the score
                document.getElementById("start-button").style.display = "block";
            }
        }, 1000);
    }
