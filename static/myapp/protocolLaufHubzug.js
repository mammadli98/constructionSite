document.addEventListener("DOMContentLoaded", () => {
    const selectElements = document.querySelectorAll("select");
    const korrekturInput = document.getElementById("korrektur");
    const nacharbeitInput = document.getElementById("nacharbeit");
    const protocolCloseButton = document.querySelector(".btn-save-export"); // Button for "Protokol abschließen"

    selectElements.forEach((select) => {
        // Update the column and check NAE status initially
        const parentRow = select.closest("tr");
        const newColumn = document.createElement("td");
        newColumn.className = "status-indicator";
        parentRow.appendChild(newColumn);

        updateStatusIndicator(select, newColumn);
        updateKorrekturValue();
        updateProtocolCloseButton(); // Check button status initially

        // Add an event listener for changes
        select.addEventListener("change", () => {
            updateStatusIndicator(select, newColumn);
            updateKorrekturValue();
            updateProtocolCloseButton(); // Check button status on change
        });
    });

    /**
     * Updates the status indicator based on the selected value.
     * @param {HTMLSelectElement} select - The select element being modified.
     * @param {HTMLElement} column - The column where the indicator is updated.
     */
    function updateStatusIndicator(select, column) {
        column.innerHTML = "";

        if (select.value === "NAE") {
            const circle = document.createElement("div");
            circle.style.width = "20px";
            circle.style.height = "20px";
            circle.style.borderRadius = "50%";
            circle.style.backgroundColor = "orange";
            circle.style.margin = "auto";

            column.appendChild(circle);
        }

        if (select.value === "OK") {
            const circle = document.createElement("div");
            circle.style.width = "20px";
            circle.style.height = "20px";
            circle.style.borderRadius = "50%";
            circle.style.backgroundColor = "green";
            circle.style.margin = "auto";

            column.appendChild(circle);
        }

        if (select.value === "NOK") {
            const circle = document.createElement("div");
            circle.style.width = "20px";
            circle.style.height = "20px";
            circle.style.borderRadius = "50%";
            circle.style.backgroundColor = "red";
            circle.style.margin = "auto";

            column.appendChild(circle);
        }
    }

    /**
     * Updates the value of the hidden input fields "korrektur" and "nacharbeit".
     */
    function updateKorrekturValue() {
        const hasNAE = Array.from(selectElements).some(select => select.value === "NAE");
        nacharbeitInput.value = hasNAE ? "True" : "False";

        const hasNOK = Array.from(selectElements).some(select => select.value === "NOK");
        korrekturInput.value = hasNOK ? "True" : "False";
    }

    /**
     * Updates the status of the "Protokol abschließen" button.
     */
    function updateProtocolCloseButton() {
        const allOkOrNae = Array.from(selectElements).every(select => select.value === "OK" || select.value === "NAE");
        protocolCloseButton.disabled = !allOkOrNae; // Enable if all are OK or NAE
    }
});
