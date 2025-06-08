document.addEventListener("DOMContentLoaded", function () {
    const chipButtons = document.querySelectorAll('[data-step="0"] .btn');
    const hiddenInput = document.getElementById('theoretical_practical');

    chipButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        chipButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        hiddenInput.value = btn.getAttribute('data-value');
    });
    });
}