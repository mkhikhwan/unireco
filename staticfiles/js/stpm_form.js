// question-form/matriculation.html
document.addEventListener('DOMContentLoaded', function() {
    // on load, add a field
    addField();
    
    document.querySelector("form").addEventListener("submit", validateForm);
});

let choices = getChoicesJson();

// Access the subject and grade options passed from Django
function getChoicesJson() {
    let choices = document.getElementById("choices");
    if (!choices) {
        return {};
    }

    let choicesJson = JSON.parse(choices.textContent);

    // delete id
    delete choices;

    return choicesJson;
}

function addField() {
    // Get Form Div to target to add a new field
    let container = document.getElementById("form-container");

    // Create new div and assign bootstrap classes
    let newFieldDiv = document.createElement("div");
    newFieldDiv.classList.add("field-group", "d-flex", "gap-2", "mb-2");

    // Create Select Box for Subjects
    let subjectOptions = "";
    for (let [id, subject] of Object.entries(choices.subjects)) {
        subjectOptions += `<option value="${id}">${subject}</option>`;
    }

    // Create Select Box for Grades
    let gradeOptions = "";
    for (let [value, grade] of Object.entries(choices.grades)) {
        gradeOptions += `<option value="${value}">${value}</option>`;
    }

    // Insert Select Box into div
    newFieldDiv.innerHTML = `
    <select class="form-select w-auto" name="subjects[]">${subjectOptions}</select>
    <select class="form-select w-auto" name="grades[]">${gradeOptions}</select>
    <button type="button" class="btn btn-danger p-0" onclick="removeField(this)">
        <i class="bi bi-trash-fill p-2"></i>
    </button>
    `;

    container.appendChild(newFieldDiv);
}

function removeField(button) {
    // Remove the parent div of the button
    button.parentElement.remove();
}

function validateForm(event) {
    let subjects = document.getElementsByName("subjects[]");
    let grades = document.getElementsByName("grades[]");

    let selectedSubjects = new Set();

    if (subjects.length === 0) {
        alert("Please add at least one subject.");
        event.preventDefault();
        return false;
    }

    for (let i = 0; i < subjects.length; i++) {
        if (!subjects[i].value || !grades[i].value) {
            alert("All subjects must have a corresponding grade.");
            event.preventDefault();
            return false;
        }

        if (selectedSubjects.has(subjects[i].value)) {
            alert("Duplicate subjects are not allowed.");
            event.preventDefault();
            return false;
        }

        selectedSubjects.add(subjects[i].value);
    }

    return true;
}