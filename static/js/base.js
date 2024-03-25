// Check if the HSStaticMethods object exists on the window object
if (typeof window.HSStaticMethods === 'object' && window.HSStaticMethods !== null) {
  // Add the event listener for htmx:afterSwap
  document.addEventListener("htmx:afterSwap", () => {
    // Add a small delay to ensure the DOM has been updated
    setTimeout(() => {
      window.HSStaticMethods.autoInit();
    },150);
  });
} else {
  console.error('HSStaticMethods is not defined on the window object');
}