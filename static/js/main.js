document.addEventListener('DOMContentLoaded', function () {
  const viewBtn = document.getElementById('viewBtn');
  const spinner = document.getElementById('viewSpinner');
  const label = document.getElementById('viewLabel');
  const select = document.getElementById('categorySelect');

  function startLoading() {
    viewBtn.disabled = true;
    spinner.style.display = 'inline-block';
    label.textContent = 'Loading...';
  }

  function stopLoading() {
    viewBtn.disabled = false;
    spinner.style.display = 'none';
    label.textContent = 'View Top Channels';
  }

  viewBtn.addEventListener('click', function () {
    const cat = select.value;
    if (!cat) return;
    startLoading();
    // Navigate after a brief delay to show the spinner (simulates async fetch)
    setTimeout(function () {
      window.location.href = '/view/' + encodeURIComponent(cat);
    }, 300);
  });
});
