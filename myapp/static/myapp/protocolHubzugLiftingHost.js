function hideConfirmation() {
    const confirmationBox = document.getElementById('confirmation-box');
    const fahrzeugId = confirmationBox.getAttribute('data-fahrzeug-id');
    
    // Hide the confirmation box
    confirmationBox.style.display = 'none';
    
    // Redirect to the specified URL
    console.log('going toooooooo:', url);
    //window.location.href = `/prueferView/`;
    
}

function submitExportForm(button) {
    if (!validateInputsForExport()) {
        console.log('Validation failed. Export process aborted.');
        return; // Exit the function if validation fails
    }

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
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `exported_protokol.pdf`; // You can customize the filename here
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        // Show the confirmation box
        //const confirmationBox = document.getElementById('confirmation-box');
        //confirmationBox.style.display = 'block';
        console.log('Confirmation box displayed');
        window.location.href = `/prueferView/`;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function submitClosedForm(button) {
    if (!validateInputsForExport()) {
        console.log('Validation failed. Export process aborted.');
        return; // Exit the function if validation fails
    }

    // If validation passes, proceed to submit the form
    const url = button.getAttribute('data-url');
    
    // Create a form element to submit the POST request
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = url;
    
    // Add CSRF token for Django
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);
    
    // Optionally, add any other hidden inputs needed
    // const otherInput = document.createElement('input');
    // otherInput.type = 'hidden';
    // otherInput.name = 'some_name';
    // otherInput.value = 'some_value';
    // form.appendChild(otherInput);

    document.body.appendChild(form);
    form.submit(); // Submit the form
}

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function validateInputsForSave() {
    const minMaxInputs = document.querySelectorAll('input[data-min][data-max]');
    const textInputs = document.querySelectorAll('input[type="text"]');
    let isValid = true;

    /* // Validate min-max inputs (empty fields are allowed)
    for (const input of minMaxInputs) {
        const value = input.value.trim();
        const numericValue = parseFloat(value);
        const min = parseFloat(input.getAttribute('data-min'));
        const max = parseFloat(input.getAttribute('data-max'));

        if (value !== '' && (isNaN(numericValue) || numericValue < min || numericValue > max)) {
            isValid = false;
            input.setCustomValidity(`Please enter a value between ${min} and ${max}.`);
            input.reportValidity();
            return isValid;
        } else {
            input.setCustomValidity(''); // Clear any previous custom validity message
        }
    } */

    // Validate text inputs for length (empty fields are allowed)
    for (const input of textInputs) {
        const value = input.value.trim();
        const minLength = 3;
        const maxLength = 20;

        if (value !== '' && (value.length < minLength || value.length > maxLength)) {
            isValid = false;
            input.setCustomValidity(`Please enter a value between ${minLength} and ${maxLength} characters.`);
            input.reportValidity();
            break;
        } else {
            input.setCustomValidity(''); // Clear any previous custom validity message
        }
    }

    return isValid; // Return whether the form inputs are valid
}

function validateInputsForExport() {
    const minMaxInputs = document.querySelectorAll('input[data-min][data-max]');
    const textInputs = document.querySelectorAll('input[type="text"]');
    let isValid = true;

    // Validate min-max inputs (fields cannot be empty)
    for (const input of minMaxInputs) {
        const value = input.value.trim();
        const numericValue = parseFloat(value);
        const min = parseFloat(input.getAttribute('data-min'));
        const max = parseFloat(input.getAttribute('data-max'));

        if (value === '' || isNaN(numericValue) || numericValue < min || numericValue > max) {
            isValid = false;
            input.setCustomValidity(`Please enter a value between ${min} and ${max}.`);
            input.reportValidity();
            return isValid;
        } else {
            input.setCustomValidity(''); // Clear any previous custom validity message
        }
    }

    // Validate text inputs for length (fields cannot be empty)
    for (const input of textInputs) {
        const value = input.value.trim();
        const minLength = 3;
        const maxLength = 20;

        if (value.length < minLength || value.length > maxLength) {
            isValid = false;
            input.setCustomValidity(`Please enter a value between ${minLength} and ${maxLength} characters.`);
            input.reportValidity();
            break;
        } else {
            input.setCustomValidity(''); // Clear any previous custom validity message
        }
    }

    return isValid; // Return whether the form inputs are valid
}

/* // Event listener for form submission for "Save"
document.getElementById('protokol-form').addEventListener('submit', function(event) {
    if (!validateInputsForSave()) {
        event.preventDefault();
    }
});

// Real-time validation for min-max inputs
document.querySelectorAll('input[data-min][data-max]').forEach(input => {
    input.addEventListener('input', function() {
        const value = input.value.trim();
        const numericValue = parseFloat(value);
        const min = parseFloat(input.getAttribute('data-min'));
        const max = parseFloat(input.getAttribute('data-max'));

        if (value === '' || (!isNaN(numericValue) && numericValue >= min && numericValue <= max)) {
            input.setCustomValidity('');
        }
    });
});
 */
// Real-time validation for text inputs
document.querySelectorAll('input[type="text"]').forEach(input => {
    input.addEventListener('input', function() {
        const value = input.value.trim();
        const minLength = 3;
        const maxLength = 20;

        if (value === '' || (value.length >= minLength && value.length <= maxLength)) {
            input.setCustomValidity('');
        }
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const inputs = document.querySelectorAll('.textarea-control');

    inputs.forEach(input => {
        const id = input.getAttribute('id').replace('check_size_', 'status_');
        validateInput(input, id);  // Revalidate on page load
    });

    // Initial check for 'korrektur' status on page load
    checkKorrektur();
});

function validateInput(input, statusId) {
    const min = parseFloat(input.getAttribute('data-min'));
    const max = parseFloat(input.getAttribute('data-max'));
    const value = parseFloat(input.value);
    const statusCell = document.getElementById(statusId);

    // Clear the status cell
    statusCell.innerHTML = '';

    // If input is empty
    if (isNaN(value)) {
        checkKorrektur();  // Update 'korrektur' after every input change
        return;
    }

    // If input is outside the range
    if (value < min || value > max) {
        statusCell.innerHTML = '<div class="circle red"></div>';
    }

    // If input is within the range
    if (value >= min && value <= max) {
        statusCell.innerHTML = '<div class="circle green"></div>';
    }

    // Update 'korrektur' after every input change
    checkKorrektur();
}

function checkKorrektur() {
    const statusCells = document.querySelectorAll('[id^="status_"]');
    let anyRed = false;

    statusCells.forEach(cell => {
        if (cell.innerHTML.includes('red')) {
            anyRed = true;
        }
    });

    const korrekturCell = document.getElementById('korrektur');
    if (anyRed) {
        korrekturCell.setAttribute('value', 'True');
    } else {
        korrekturCell.setAttribute('value', 'False');
    }
}