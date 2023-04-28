// Load the JSON data
$(document).ready(function() {
    // Your JavaScript code goes here
    $.getJSON('../data/stations.json', function(data) {
        var jsonData = data;
        console.log(jsonData)
    
        // Attach an event listener to the search input
        $('#search-input').on('input', function() {
            var searchQuery = $(this).val().toLowerCase();
            var filteredData = [];
    
            // Filter the JSON data based on the search query
            if (searchQuery) {
                filteredData = jsonData.filter(function(item) {
                    return item.name.toLowerCase().indexOf(searchQuery) !== -1;
                });
            }
    
            // Update the dropdown list with the filtered results
            var resultsList = $('#search-results');
            resultsList.empty();
            $.each(filteredData, function(index, result) {
                resultsList.append('<li><a href="' + result.url + '">' + result.name + '</a></li>');
            });
        });
    });
});

