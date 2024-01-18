document.addEventListener('DOMContentLoaded', function () {
    const updateEventButtons = document.querySelectorAll('[id^="update_event_"]');
    
    updateEventButtons.forEach((button) => {
      button.addEventListener('click', function () {
        const eventId = button.id.split('_').pop(); // Extract eventId from button ID
        updateEvent(eventId);
        });
    });
});


function updateEvent(eventId) {
    fetch("/admin/open-event", {
      method: "POST",
      body: JSON.stringify({ eventId: eventId }),
    }).then((_res) => {
      window.location.href = "/admin/new-event";
    });
  }