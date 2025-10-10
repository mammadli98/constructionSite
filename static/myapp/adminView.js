// adminView.js

(function () {
    // --- CSRF helpers (Django recommended: cookie-based) ---
    function getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
      return null;
    }
    function getCsrfToken() {
      // Prefer cookie; fallback to meta (works on SSR pages)
      return getCookie('csrftoken') || document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
    const CSRF_TOKEN = getCsrfToken();
  
    // Cache DOM once
    let selectedBaustelleId = null;
    const baustellenTable = document.getElementById('baustellenTable');
    const fahrzeugTableBody = document.querySelector('#fahrzeugTable tbody');
    const addFahrzeugBtn = document.getElementById('addFahrzeugBtn');
    const selectedBaustelleInput = document.getElementById('selectedBaustelleId');
  
    // Initially hide all fahrzeug rows (lazy-reveal when a Baustelle is selected)
    document.addEventListener('DOMContentLoaded', function () {
      if (!fahrzeugTableBody) return;
      for (const row of fahrzeugTableBody.rows) {
        row.style.display = 'none';
      }
    });
  
    // Select Baustelle via event delegation (works for clicks + keyboard)
    if (baustellenTable) {
      baustellenTable.addEventListener('click', onBaustelleActivate);
      baustellenTable.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          const row = e.target.closest('tr[data-baustelle-id]');
          if (row) {
            e.preventDefault();
            onBaustelleActivate({ target: row });
          }
        }
      });
    }
  
    function onBaustelleActivate(evt) {
      const row = (evt.target && evt.target.closest) ? evt.target.closest('tr[data-baustelle-id]') : evt.target;
      if (!row) return;
  
      selectedBaustelleId = row.getAttribute('data-baustelle-id');
      if (!selectedBaustelleId) return;
  
      // Enable add button + set hidden input
      if (addFahrzeugBtn) addFahrzeugBtn.disabled = false;
      if (selectedBaustelleInput) selectedBaustelleInput.value = selectedBaustelleId;
  
      // Highlight
      baustellenTable.querySelectorAll('tbody tr').forEach(r => r.classList.remove('selected'));
      row.classList.add('selected');
  
      // Filter Fahrzeuge
      if (fahrzeugTableBody) {
        for (const r of fahrzeugTableBody.rows) {
          r.style.display = (r.getAttribute('data-baustelle-id') === selectedBaustelleId) ? '' : 'none';
        }
      }
    }
  
    // Visibility toggles via event delegation
    if (fahrzeugTableBody) {
      fahrzeugTableBody.addEventListener('change', function (e) {
        const checkbox = e.target.closest('.visibility-toggle');
        if (!checkbox) return;
  
        const fahrzeugId = checkbox.getAttribute('data-fahrzeug-id');
        const isVisible = checkbox.checked;
  
        fetch(`/update_fahrzeug_visibility/${fahrzeugId}/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN
          },
          body: JSON.stringify({ isVisible })
        }).then(res => {
          if (!res.ok) {
            checkbox.checked = !isVisible; // revert
            alert('Failed to update visibility');
          }
        }).catch(() => {
          checkbox.checked = !isVisible; // revert
          alert('Network error while updating visibility');
        });
      });
    }
  })();
  