$(document).ready(function(){
    // Load the default tab content
    loadTabContent($('.nav-link.active').data('url'));

    // Handle tab click
    $('.nav-link').on('click', function(e){
        e.preventDefault();
        var url = $(this).data('url');
        loadTabContent(url);
    });

    function loadTabContent(url){
        $.ajax({
            url: url,
            method: 'GET',
            success: function(data){
                $('#tab-content-container').html(data);
                
                // Reinitialize the update and delete button event handlers
                initializeMatchButtons();
            },
            error: function(xhr, status, error){
                $('#tab-content-container').html('<p>Error loading content.</p>');
            }
        });
    }

    function initializeMatchButtons() {
        $('.update-match-btn, .delete-match-btn').off('click').on('click', function() {
            var matchId = $(this).data('match-id');
            var action = $(this).hasClass('update-match-btn') ? 'update' : 'delete';
            var url = action === 'update' ? "{% url 'update_match' 0 %}".replace("0", matchId) : "{% url 'delete_match' 0 %}".replace("0", matchId);
            var formData = action === 'update' ? $('#updateMatchForm').serialize() : {csrfmiddlewaretoken: "{{ csrf_token }}"};
            
            // Send AJAX request
            $.ajax({
                url: url,
                type: 'POST',
                data: formData,
                success: function(response) {
                    if (response.success) {
                        // Handle success based on action
                        if (action === 'update') {
                            // Match updated successfully, update UI (if needed)
                            // Example:
                            location.reload();  // Reload the page to reflect changes
                        } else if (action === 'delete') {
                            // Match deleted successfully, update UI (e.g., remove row from table)
                            // Example:
                            $('#row_' + matchId).remove();  // Assuming each row has an ID like 'row_<matchId>'
                        }
                    } else {
                        // Handle failure (optional)
                    }
                },
                error: function(xhr, status, error) {
                    // Handle error (optional)
                }
            });
        });
    }

    // Initial call to bind event handlers
    initializeMatchButtons();
});
