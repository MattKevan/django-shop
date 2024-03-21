
  
  // Initialize quantity forms on page load
  document.addEventListener('DOMContentLoaded', function() {

  });
  
  // Initialize quantity forms after HTMX swap
  document.addEventListener('htmx:afterSwap', function(event) {

    window.HSStaticMethods.autoInit();

  });
