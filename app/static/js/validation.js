document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const emailInput = document.getElementById('id_email');
    const password1Input = document.getElementById('id_password1');
    const password2Input = document.getElementById('id_password2');

    form.addEventListener('submit', function (event) {
        [emailInput, password1Input, password2Input].forEach(input => {
            input.classList.remove('is-invalid');
        });

        let valid = true;
        let messages = [];

        // Email format check
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(emailInput.value)) {
            emailInput.classList.add('is-invalid');
            messages.push('Please enter a valid email address.');
            valid = false;
        }

        // Password length check
        if (password1Input.value.length < 8) {
            password1Input.classList.add('is-invalid');
            messages.push('Password must be at least 8 characters long.');
            valid = false;
        }

        // Password match check
        if (password1Input.value !== password2Input.value) {
            password2Input.classList.add('is-invalid');
            messages.push('Passwords do not match.');
            valid = false;
        }

        // Prevent form submission if not valid
        if (!valid) {
            event.preventDefault();
            alert(messages.join('\n'));
        }
    });
});
