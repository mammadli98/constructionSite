function hideConfirmation() {
    const confirmationBox = document.getElementById('confirmation-box');
    const fahrzeugId = confirmationBox.getAttribute('data-fahrzeug-id');
    
    // Hide the confirmation box
    confirmationBox.style.display = 'none';
    
    // Redirect to the specified URL
    window.location.href = `/hubzug/?fahrzeugId=${fahrzeugId}`;
}

function submitExportForm(button) {
    const url = button.getAttribute('data-url');

    // Logging for debugging
    console.log('Submitting export form to URL:', url);

    // Fetch request to submit the form data
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json().catch(() => {
            throw new Error('Invalid JSON response');
        });
    })
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        // Show the confirmation message with the file path
        console.log('Export successful, file path:', data.path);
        document.getElementById('file-path').textContent = data.path;
        const confirmationBox = document.getElementById('confirmation-box');
        confirmationBox.style.display = 'block';
        console.log('Confirmation box displayed');

        // Disable form inputs
        disableFormInputs(true);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function disableFormInputs(disable) {
    const formElements = document.querySelectorAll('#protokol-form input, #protokol-form textarea, #protokol-form button');
    formElements.forEach(element => {
        element.disabled = disable;
    });
}

document.getElementById('protokol-form').addEventListener('submit', function(event) {
    const inputs = document.querySelectorAll('input[data-min][data-max]');
    let isValid = true;

    inputs.forEach(input => {
        const value = parseFloat(input.value);
        const min = parseFloat(input.getAttribute('data-min'));
        const max = parseFloat(input.getAttribute('data-max'));

        if (isNaN(value) || value < min || value > max) {
            isValid = false;
            input.setCustomValidity(`Please enter a value between ${min} and ${max}.`);
            input.reportValidity();
        } else {
            input.setCustomValidity(''); // Clear any previous custom validity message
        }
    });

    if (!isValid) {
        event.preventDefault();
    }
});

// Add an event listener for input changes to clear the custom validity message
document.querySelectorAll('input[data-min][data-max]').forEach(input => {
    input.addEventListener('input', function() {
        const value = parseFloat(this.value);
        const min = parseFloat(this.getAttribute('data-min'));
        const max = parseFloat(this.getAttribute('data-max'));

        if (!isNaN(value) && value >= min && value <= max) {
            this.setCustomValidity('');
        }
    });
});