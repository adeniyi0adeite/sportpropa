


document.addEventListener('DOMContentLoaded', function() {
    // Select the toggle button
    var toggleButton = document.querySelector('.toggle-button');

    // Add click event listener to the toggle button
    toggleButton.addEventListener('click', function() {
        // Select the container that needs to be shown/hidden
        var container = document.querySelector('#remaining-results');

        // Check if the container is currently shown or hidden
        if (container.style.display === 'none') {
            // If hidden, show the container
            container.style.display = 'block';
            // Change the button text to "Show Less Results"
            toggleButton.textContent = 'Show Less Results';
        } else {
            // If shown, hide the container
            container.style.display = 'none';
            // Change the button text back to "Show More Results"
            toggleButton.textContent = 'Show More Results';
        }
    });
});
