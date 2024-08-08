let selectedBaustelleId = null;
let selectedFahrzeugId = null;

function selectBaustelle(row, baustelleId) {
    selectedBaustelleId = baustelleId;

    // Highlight the selected row
    const allBaustelleRows = document.querySelectorAll('.baustellen-panel tbody tr');
    allBaustelleRows.forEach(r => r.classList.remove('selected-baustelle'));
    row.classList.add('selected-baustelle');

    // Show only the Fahrzeuge that belong to the selected Baustelle
    const allFahrzeugRows = document.querySelectorAll('#fahrzeugTable tbody tr');
    allFahrzeugRows.forEach(fahrzeugRow => {
        fahrzeugRow.style.display = fahrzeugRow.dataset.baustelleId === baustelleId.toString() ? '' : 'none';
    });

    // Clear previous Fahrzeug selection
    document.querySelectorAll('.fahrzeuge-panel tbody tr').forEach(r => r.classList.remove('selected-fahrzeug'));
    selectedFahrzeugId = null;

    // Update button states
    updateButtonStates();
}

function selectFahrzeug(row) {
    selectedFahrzeugId = row.dataset.fahrzeugId;  // Use fahrzeugId instead of baustelleId

    // Highlight the selected Fahrzeug row
    const allFahrzeugRows = document.querySelectorAll('.fahrzeuge-panel tbody tr');
    allFahrzeugRows.forEach(r => r.classList.remove('selected-fahrzeug'));
    row.classList.add('selected-fahrzeug');

    // Update button states
    updateButtonStates();
}

function updateButtonStates() {
    const buttons = document.querySelectorAll('.action-btn');
    if (selectedBaustelleId && selectedFahrzeugId) {
        buttons.forEach(button => button.classList.remove('disabled'));
    } else {
        buttons.forEach(button => button.classList.add('disabled'));
    }
}

function redirectTo(url) {
    if (selectedBaustelleId && selectedFahrzeugId) {
        window.location.href = `${url}?fahrzeugId=${selectedFahrzeugId}`;
    }
}

// Initially hide all fahrzeug rows
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#fahrzeugTable tbody tr').forEach(row => {
        row.style.display = 'none';
    });
});
