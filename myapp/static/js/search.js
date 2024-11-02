$(document).ready(function() {
    var csrfToken = $('meta[name="csrf-token"]').attr('content');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            }
        }
    });

    $('#rd-search-form-input').on('input', function() {
        var query = $(this).val();

        if(query.length >= 3) { // Only search if at least 3 characters were typed
            $.ajax({
                url: "{% url 'search_users' %}",
                data: {
                    'q': query
                },
                success: function(data) {
                    $('#rd-search-results').html(data);
                }
            });
        } else {
            $('#rd-search-results').html(''); // Clear results if under 3 characters
        }
    });
});