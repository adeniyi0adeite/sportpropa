document.addEventListener('DOMContentLoaded', function() {
    var hash = window.location.hash;
    if (hash) {
        var tabTrigger = document.querySelector('a[href="' + hash + '"]');
        if (tabTrigger) {
            var tab = new bootstrap.Tab(tabTrigger);
            tab.show();
        }
    }
});