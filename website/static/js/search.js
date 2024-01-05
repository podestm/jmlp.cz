var selectElement = document.getElementById('racers');
var searchInput = document.getElementById('searchInput');
// Add an event listener to the search input for filtering options
searchInput.addEventListener('input', function () {
        var searchValue = this.value.toLowerCase();
    // Iterate through options and show/hide based on the search value
    Array.from(selectElement.options).forEach(function (option) {
        var optionText = option.textContent.toLowerCase();
        var shouldShow = optionText.includes(searchValue);
        option.style.display = shouldShow ? '' : 'none';
    });
});


function toggleNewTeamInput() {
    var teamSelect = document.getElementById('racer_teamName');
    var newTeamInput = document.getElementById('newTeamInput');
    var newTeamField = document.getElementById('racer_newTeam');

    if (teamSelect.value === 'AddNewTeam') {
        newTeamInput.style.display = 'block';
        newTeamField.required = true;
    } else {
        newTeamInput.style.display = 'none';
        newTeamField.required = false;
        newTeamField.value = '';
    }
}