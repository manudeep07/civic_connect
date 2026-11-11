// CivicConnect Interactive Scripts
document.addEventListener('DOMContentLoaded', function () {
  // Initialize Bootstrap Tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Auto-dismiss Django Messages after 6 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = new bootstrap.Alert(alert);
      try {
        bsAlert.close();
      } catch (e) {}
    }, 6000);
  });

  // Confirm delete on buttons with class .confirm-delete
  const deleteButtons = document.querySelectorAll('.confirm-delete');
  deleteButtons.forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      const targetName = this.getAttribute('data-item-name') || 'this item';
      if (!confirm(`Are you sure you want to permanently delete ${targetName}? This action cannot be undone.`)) {
        e.preventDefault();
      }
    });
  });

  // Animate counters if present
  const statCounters = document.querySelectorAll('.stat-counter');
  statCounters.forEach(function (counter) {
    const target = +counter.getAttribute('data-target');
    if (!isNaN(target) && target > 0) {
      let count = 0;
      const speed = Math.max(10, Math.floor(target / 40));
      const updateCount = () => {
        count += speed;
        if (count < target) {
          counter.innerText = count;
          setTimeout(updateCount, 30);
        } else {
          counter.innerText = target;
        }
      };
      updateCount();
    }
  });
});

