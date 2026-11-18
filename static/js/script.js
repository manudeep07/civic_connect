// CivicConnect Client Scripts
document.addEventListener('DOMContentLoaded', function () {
  // Initialize Bootstrap Tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.forEach(function (tooltipTriggerEl) {
    new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Auto-dismiss Django Messages after 6 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach(function (alert) {
    setTimeout(function () {
      try {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      } catch (e) {}
    }, 6000);
  });

  // Confirm delete on buttons with class .confirm-delete
  const deleteButtons = document.querySelectorAll('.confirm-delete');
  deleteButtons.forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      const targetName = this.getAttribute('data-item-name') || 'this item';
      if (!confirm(`Are you sure you want to delete ${targetName}? This action cannot be undone.`)) {
        e.preventDefault();
      }
    });
  });

  // Stat counters (respecting prefers-reduced-motion)
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const statCounters = document.querySelectorAll('.stat-counter');
  statCounters.forEach(function (counter) {
    const target = +counter.getAttribute('data-target');
    if (!isNaN(target)) {
      if (prefersReducedMotion) {
        counter.innerText = target;
      } else {
        let count = 0;
        const speed = Math.max(1, Math.floor(target / 25));
        const updateCount = () => {
          count += speed;
          if (count < target) {
            counter.innerText = count;
            setTimeout(updateCount, 25);
          } else {
            counter.innerText = target;
          }
        };
        updateCount();
      }
    }
  });
});
