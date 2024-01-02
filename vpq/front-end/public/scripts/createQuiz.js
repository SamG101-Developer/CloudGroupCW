function createQuiz(username) {

    let quizJSON = { author: username, questions: [] };

    let quizName = prompt("Enter the name of your quiz");
    let roundContent = document.getElementById("round-content");
    let rounds = roundContent.children;

    for (let round of rounds) {
        quizJSON.questions.push(parseRound(round, username));
    }

    window.app.createQuiz(quizJSON);
}

function parseRound(round, username) {
    let questionSetRound = [];
    let roundComponents = round.children;
    for (let roundComponent of roundComponents) {
        if (!roundComponent.classList.contains("questionTemplate")) continue;
        questionSetRound.push(parseQuestion(roundComponent, username));
    }
    return questionSetRound;
}

function parseQuestion(roundComponent, username) {
    let question = {
        author: username,
        question: "",
        answers: [],
        correct_answer: "",
        question_type: ""
    }

    // Parse the question type
    roundComponent.querySelectorAll(".checkbox-row > .checkbox-row").forEach(questionType => {
        if (questionType.querySelector("input").checked) {
            console.log(true);
            question["question_type"] = questionType.querySelector("label").innerHTML;
        }
    })

    // Parse the question text
    question["question"] = roundComponent.querySelector(".QuestionInput").value

    // Parse the answers
    if (question["question_type"] === "Multiple Choice"){
        roundComponent.querySelectorAll(".multipleChoiceOptionsContainer > .checkbox-row").forEach(option => {
            let answer = option.querySelector("input[type=text]").value;
            question["answers"].push(answer)

            let checkbox = option.querySelector("input[type=radio]");

            if (checkbox.checked){
                question["correct_answer"] = answer;
            }
        })
    }else{
        question["correct_answer"] = roundComponent.querySelector(".AnswerInput").value
    }
    return question;
}