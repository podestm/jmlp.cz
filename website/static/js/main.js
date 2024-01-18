// Call the retrieveAndSetHeading function when the page loads
window.onload = retrieveAndSetEvent;
 // Add an event listener to the racers select element
 document.getElementById('racers').addEventListener('change', function () {
    // Get the selected option value
    var selectedRacer = this.value;
    // Split the value into parts (assuming space-separated values)
    var racerParts = selectedRacer.split('!');
    // Update the form fields with the corresponding values
    document.getElementById('racer_firstName').value = racerParts[0] || '!';
    document.getElementById('racer_lastName').value = racerParts[1] || '!';
    document.getElementById('racer_birthYear').value = racerParts[2] || '!';
    document.getElementById('racer_teamName').value = racerParts[3] || '!';
    document.getElementById('racer_gender').value = racerParts[4] || '!';
});


function updateFormFieldsEvent() {
    // Get the card element that contains the clicked button
    var card = event.target.closest('.card');
    // Extract values from the card
    var eventId = card.querySelector('#card_event_id').textContent.trim();
    var eventDate = card.querySelector('#card_event_date').textContent.trim();
    var eventName = card.querySelector('#card_event_name').textContent.trim();
    var eventBadge = card.querySelector('#card_event_badge').textContent.trim();
    var eventOrganizator = card.querySelector('#card_event_organizator').textContent.trim();
    var eventPlace = card.querySelector('#card_event_place').textContent.trim();
    var eventFinal = card.querySelector('#card_event_final').textContent.trim();

    console.log('eventFinalValue:', eventFinal);

    // Fill the form fields with extracted values
    document.getElementById('event_id').value = eventId;
    document.getElementById('event_date').value = eventDate;
    document.getElementById('event_title').value = eventName;
    document.getElementById('event_badge').value = eventBadge;
    document.getElementById('event_organizator').value = eventOrganizator;
    document.getElementById('event_place').value = eventPlace;
    // Add more lines to fill other form fields as needed
    // Fill the event_final checkbox based on the value (0 or 1)
    var eventFinalCheckbox = document.getElementById('event_final');
    if (eventFinal === '1') {
        eventFinalCheckbox.checked = true; // Check the checkbox
    } else {
        eventFinalCheckbox.checked = false; // Uncheck the checkbox
    }
    // You may want to scroll to the form or perform other actions after updating the form
    document.getElementById('event_title').scrollIntoView({ behavior: 'smooth' });
}

function downloadFile(fileName) {
    window.open('/download/' + fileName, '_blank');
}
