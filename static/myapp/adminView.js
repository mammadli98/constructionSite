function selectBaustelle(row, baustelleId) {
    document.getElementById('addFahrzeugBtn').disabled = false; // Enable the button
    document.getElementById('selectedBaustelleId').value = baustelleId; // Set baustelleId for the form

    // Highlight the selected row
    const allBaustelleRows = document.querySelectorAll('.baustellen-panel tbody tr');
    allBaustelleRows.forEach(r => r.classList.remove('selected'));
    row.classList.add('selected');

    // Show only the Fahrzeuge that belong to the selected Baustelle
    const allRows = document.querySelectorAll('#fahrzeugTable tbody tr');
    allRows.forEach(row => {
        row.style.display = row.dataset.baustelleId === baustelleId.toString() ? '' : 'none';
    });
}

function toggleVisibility(fahrzeugId, isVisible) {
    fetch(`/update_fahrzeug_visibility/${fahrzeugId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}' // Use the CSRF token from the template context
        },
        body: JSON.stringify({ isVisible: isVisible })
    }).then(response => {
        if (!response.ok) {
            alert('Failed to update visibility');
        }
    });
}

// Initially hide all fahrzeug rows
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#fahrzeugTable tbody tr').forEach(row => {
        row.style.display = 'none';
    });
});