document.addEventListener("DOMContentLoaded", function() {
    fetchRecommendations();
});

function fadeInRecommendations() {
    const recommendations = document.querySelectorAll('.recommendation-block');
    recommendations.forEach((block, index) => {
        setTimeout(() => {
            block.classList.add('active');
        }, index * 500); // Stagger the fade-in effect
    });
}

function fetchRecommendations() {
    fetch("/api/recommendation")
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to fetch recommendations.");
            }
            return response.json();
        })
        .then(data => {
            document.getElementById("loading").style.display = "none";

            const recommendationResults = document.getElementById("recommendation-results");
            recommendationResults.innerHTML = ''; // Clear previous content

            data.forEach((field, index) => {
                const blockId = 'block-' + index;
                const colDiv = document.createElement("div");
                colDiv.className = "col-12 col-md-6 col-lg-4";
                colDiv.id = blockId;

                colDiv.innerHTML = `
                    <div class="recommendation-block active card shadow-lg border border-1 border-secondary-subtle h-100">
                        <div class="card-body d-flex flex-column">
                            <div class="d-flex justify-content-between mb-2">
                                <h5 class="card-title mb-0 fw-bold">${index + 1} - ${field.name}</h5>
                                <span class="percentage-badge">${field.match_percentage}% Match</span>
                            </div>
                            <p class="card-text flex-grow-1">${field.description}</p>
                            <p class="fw-semibold">Interested? Here are programs in this field:</p>
                            <ul class="program-list">
                                ${field.programs.map(program => {
                                    const isQualified = program.qualified;
                                    const universityAbbr = getUniversityAbbreviation(program.institute);
                                    return `
                                        <li class="program-item ${isQualified ? '' : 'unqualified'}">
                                            <a href="/program/${program.id}">${program.name} - ${universityAbbr}</a>
                                            <span class="program-status ${isQualified ? 'qualified' : 'not-qualified'}">
                                                ${isQualified ? 'Qualified' : 'Not Qualified'}
                                            </span>
                                        </li>
                                    `;
                                }).join('')}
                            </ul>
                        </div>
                    </div>
                `;

                recommendationResults.appendChild(colDiv);
            });

            document.getElementById("footer-links").style.display = "block";
        })
        .catch(error => {
            console.error(error);
            document.getElementById("loading").innerHTML = "<div class='text-danger fw-bold'>Failed to load recommendations. Please try again later.</div>";
        });
}

function populateProgramList(programs) {
    let ul = document.createElement("ul");
    ul.className = "program-list";

    programs.forEach(program => {
        let listItem = document.createElement("li");
        listItem.className = "program-item";
        if (!program.qualified) {
            listItem.classList.add("unqualified");
        }

        let link = document.createElement("a");
        link.href = `/program/${program.id}`;
        link.textContent = program.name + ` - ` + getUniversityAbbreviation(program.institute);
        listItem.appendChild(link);

        let statusSpan = document.createElement("span");
        statusSpan.className = "program-status " + (program.qualified ? "qualified" : "not-qualified");
        statusSpan.textContent = program.qualified ? "Qualified" : "Not Qualified";
        listItem.appendChild(statusSpan);

        ul.appendChild(listItem);
    });

    return ul;
}

function getUniversityAbbreviation(fullName) {
    const match = fullName.match(/\(([^)]+)\)/);
    return match ? match[1] : '';
}