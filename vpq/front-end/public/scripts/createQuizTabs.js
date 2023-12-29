let tabCount = 0;
let currentTab = 0;
let questionTypes = ["Multiple Choice", "Numeric", "Pick the Letter", "Full Answer"];
/*
radioNumber needs to be unique for each question therefore it will be incremented each time it is used.
The number does not correspond to anything and will not be used for identification and can therefore be ignored.
 */
let radioNumber = 0;
function addTab(){

    let roundName = prompt("Please enter the name for you round:")
    // If no round name is entered then don't add a tab
    if (roundName === null || roundName === "") return;

    let quizTabs = document.getElementById("createQuizTabList");
    // 10 round maximum
    if (quizTabs.childNodes.length - 1 >= 10) return;

    tabCount++;

    // Create a new tab
    let tempDiv = document.createElement("div");
    tempDiv.innerHTML = '<li class="nav-item" onclick="switchTab(' + tabCount + ')"><a class="nav-link">' + roundName + '</a></li>';

    let newTab = tempDiv.firstChild;

    let addTabButton = quizTabs.lastElementChild;
    quizTabs.insertBefore(newTab, addTabButton);

    // Create the tab content
    let tabDiv = document.createElement("div");
    tabDiv.classList.add("tab-pane");
    tabDiv.id = "round-" + tabCount + "-content";
    tabDiv.innerHTML = '<button class="roundTabButton addQuestionButton" onclick="addQuestion(' + tabCount + ')">Add Question</button>'

    let tabContainer = document.getElementById("round-content");
    tabContainer.appendChild(tabDiv);

    //Create a delete round button
    let deleteRoundButton = document.createElement("button");
    deleteRoundButton.classList.add("roundTabButton");
    deleteRoundButton.classList.add("removeRoundButton");
    deleteRoundButton.innerText = "Remove Round";
    deleteRoundButton.onclick = function(){
        let confirmDeletion = confirm("Are you sure you want to delete this round?");
        if (confirmDeletion){
            quizTabs.removeChild(newTab);
            tabContainer.removeChild(tabDiv);
        }
    }
    tabDiv.appendChild(deleteRoundButton);
}

function switchTab(tabNumber){
    let currentTabContent = document.getElementById("round-" + currentTab.toString() + "-content");
    let newTabContent = document.getElementById("round-" + tabNumber.toString() + "-content");

    try{
        currentTabContent.classList.remove("active");
    }catch (err){
        console.log("Switching from unknown tab");
    }
    newTabContent.classList.add("active");
    currentTab = tabNumber;
}

function addQuestion(tabNumber) {
    // Get the tab we are adding the question to
    let tabContent = document.getElementById("round-" + tabNumber.toString() + "-content");

    // Set up the question div
    let questionDiv = document.createElement("div");
    questionDiv.classList.add("row");
    questionDiv.classList.add("questionTemplate");

    // Set up the question type row
    let questionTypeDiv = document.createElement("div");
    questionTypeDiv.classList.add("checkbox-row");

    // Create checkboxes
    createCheckboxes(questionTypeDiv, questionDiv);

    // Add the components to the question div
    questionDiv.appendChild(questionTypeDiv);

    // Add the question div to the page
    tabContent.appendChild(questionDiv);
}

function createCheckboxes(questionTypeDiv, questionDiv){
    // Create the checkboxes
    let checkboxNumber = 1;
    for (let questionType of questionTypes) {
        //Create a div to hold the pair
        let checkboxLabelPair = document.createElement("div");
        checkboxLabelPair.classList.add("checkbox-row");

        //Create the checkbox
        let input = document.createElement("input");
        input.type = 'radio';
        input.id = "checkbox" + checkboxNumber.toString();
        input.name = "question-" + radioNumber.toString() + "-radio"
        input.onclick = function() {loadQuestionType(questionType, questionDiv)};

        // //Check multiple choice by default
        // if (questionType === "Multiple Choice"){
        //     input.checked = true;
        // }

        //Create the label
        let label = document.createElement("label");
        label.innerHTML = questionType;

        //Add components to the divs
        checkboxLabelPair.appendChild(input);
        checkboxLabelPair.appendChild(label);
        questionTypeDiv.appendChild(checkboxLabelPair);
    }
    radioNumber++;
}

function loadQuestionType(questionType, questionDiv){
    // Create Question Input
    let questionInput = document.createElement("input");
    questionInput.type = "text";
    questionInput.placeholder = "Enter Question...";
    questionDiv.appendChild(questionInput);

    while (questionDiv.childNodes.length > 2){
        questionDiv.removeChild(questionDiv.lastElementChild);
    }

    /*
    This switch statement is slightly unusual.
    Due to three of the categories having the same needs at the current moment I have removed 'break' from them so that
    I don't duplicate the code. If in the future these need different inputs then the break statement will be introduced
    again.
     */
    switch (questionType){
        case "Multiple Choice":
        {
            let optionsContainer = document.createElement("div");
            optionsContainer.className = "multipleChoiceOptionsContainer";

            for (let i = 1; i <= 4; i++){
                //Create a div to hold the pair
                let checkboxOptionPair = document.createElement("div");
                checkboxOptionPair.classList.add("checkbox-row");

                let tickBox = document.createElement("input");
                tickBox.type = 'radio';
                tickBox.id = "checkbox" + i.toString();
                tickBox.name = "option-" + radioNumber.toString() + "-radio"

                let option = document.createElement("input");
                option.type = "text";
                option.placeholder = "Answer" + (i).toString();

                checkboxOptionPair.appendChild(tickBox);
                checkboxOptionPair.appendChild(option);
                optionsContainer.appendChild(checkboxOptionPair);
            }
            radioNumber++;
            questionDiv.appendChild(optionsContainer);
            break;
        }
        case "Numeric":
        {

        }
        case "Pick the Letter":
        {

        }
        case "Full Answer":
        {
            let answerInput = document.createElement("input");
            answerInput.type = "text";
            answerInput.placeholder = "Enter Answer...";
            questionDiv.appendChild(answerInput);
            break;
        }
        default:
        {
            alert("Unknown Question Type");
        }
    }
}