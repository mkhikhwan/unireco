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
    fetch("/api/recommendation")  // change to your API endpoint URL
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to fetch recommendations.");
            }
            return response.json();
        })
        .then(data => {
            document.getElementById("loading").style.display = "none";

            const programResults = document.getElementById("program-results");
            data.programs.forEach(program => {
                const programCard = `
                    <div class="col-md-12 mb-4 recommendation-block">
                        <div class="card shadow-sm">
                            <div class="row g-0">
                                <div class="col-md-3">
                                    <img src="${program.image_url}" width="400" height="400" class="img-fluid rounded-start object-fit-cover" alt="${program.university} Logo">
                                </div>
                                <div class="col-md-9">
                                    <div class="card-body">
                                        <h5 class="card-title fw-bold">${program.program_name}</h5>
                                        <p class="card-subtitle mb-2 text-muted"><strong>${program.university}</strong></p>
                                        <p class="card-text">${program.description}</p>
                                        <div class="mb-3">
                                            <h6 class="fw-bold text-primary">Why we recommend this:</h6>
                                            <p class="text-muted">${program.reason}</p>
                                        </div>
                                        <div class="d-flex justify-content-between align-items-center">
                                            <div>
                                                <span class="badge bg-success">${program.suitability}</span>
                                            </div>
                                            <a href="/view-program/${program.program_id}/" class="btn btn-primary btn-sm">View Program</a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                programResults.insertAdjacentHTML('beforeend', programCard);
            });

            setTimeout(() => {
                fadeInRecommendations();
            }, 500);

            document.getElementById("footer-links").style.display = "block";
        })
        .catch(error => {
            console.error(error);
            document.getElementById("loading").innerHTML = "<div class='text-danger fw-bold'>Failed to load recommendations. Please try again later.</div>";
        });
}
