// userView.js
(function () {
    let selectedBaustelleId = null;
    let selectedFahrzeugId = null;
  
    const baustellenTable = document.getElementById('baustellenTable');
    const fahrzeugTableBody = document.querySelector('#fahrzeugTable tbody');
    const actionButtons = document.querySelectorAll('.action-btn');
    const passwordModalEl = document.getElementById('passwordChangeModal');
  
    // Helper: enable/disable action buttons based on selection
    function updateButtons() {
      const enabled = Boolean(selectedBaustelleId && selectedFahrzeugId);
      actionButtons.forEach(btn => {
        btn.disabled = !enabled;
        btn.setAttribute('aria-disabled', String(!enabled));
      });
    }
  
    // Helper: filter Fahrzeuge by selected Baustelle
    function filterFahrzeuge() {
      if (!fahrzeugTableBody) return;
      for (const row of fahrzeugTableBody.rows) {
        const show = row.getAttribute('data-baustelle-id') === String(selectedBaustelleId);
        row.style.display = show ? '' : 'none';
      }
    }
  
    // Initially hide all Fahrzeuge
    document.addEventListener('DOMContentLoaded', () => {
      if (fahrzeugTableBody) {
        for (const row of fahrzeugTableBody.rows) row.style.display = 'none';
      }
  
      // Auto-show password modal if backend set modal_show=True
      if (passwordModalEl && passwordModalEl.getAttribute('data-show-modal') === 'true') {
        $('#passwordChangeModal').modal('show');
      }
    });
  
    // Select Baustelle (click + keyboard)
    if (baustellenTable) {
      const onActivate = (targetRow) => {
        if (!targetRow) return;
        selectedBaustelleId = targetRow.getAttribute('data-baustelle-id');
  
        // Highlight selection
        baustellenTable.querySelectorAll('tbody tr').forEach(r => r.classList.remove('selected'));
        targetRow.classList.add('selected');
  
        // Reset Fahrzeug selection and filter
        selectedFahrzeugId = null;
        if (fahrzeugTableBody) {
          fahrzeugTableBody.querySelectorAll('tr').forEach(r => r.classList.remove('selected'));
        }
        filterFahrzeuge();
        updateButtons();
      };
  
      baustellenTable.addEventListener('click', (e) => {
        const row = e.target.closest('tr[data-baustelle-id]');
        onActivate(row);
      });
  
      baustellenTable.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          const row = e.target.closest('tr[data-baustelle-id]');
          if (row) {
            e.preventDefault();
            onActivate(row);
          }
        }
      });
    }
  
    // Select Fahrzeug (click + keyboard) via delegation
    if (fahrzeugTableBody) {
      const onActivateFahrzeug = (row) => {
        if (!row || row.style.display === 'none') return;
        selectedFahrzeugId = row.getAttribute('data-fahrzeug-id');
  
        fahrzeugTableBody.querySelectorAll('tr').forEach(r => r.classList.remove('selected'));
        row.classList.add('selected');
  
        updateButtons();
      };
  
      fahrzeugTableBody.addEventListener('click', (e) => {
        const row = e.target.closest('tr[data-fahrzeug-id]');
        onActivateFahrzeug(row);
      });
  
      fahrzeugTableBody.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          const row = e.target.closest('tr[data-fahrzeug-id]');
          if (row) {
            e.preventDefault();
            onActivateFahrzeug(row);
          }
        }
      });
    }
  
    // Actions: navigate when enabled
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.action-btn');
      if (!btn) return;
  
      if (btn.disabled) {
        e.preventDefault();
        return;
      }
  
      const url = btn.getAttribute('data-url');
      if (url && selectedFahrzeugId) {
        window.location.href = `${url}?fahrzeugId=${encodeURIComponent(selectedFahrzeugId)}`;
      }
    });
  })();
  