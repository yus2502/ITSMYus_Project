
  let isFormSubmitted = false;

  // Function to check if required fields are selected
  function checkForm() {
      const yesNoValue = document.querySelector('input[name="helpful"]:checked');
      const dropdownValue = document.getElementById("knowledge_article_id").value;

      if (!yesNoValue || dropdownValue === "") {
          return false;
      }

      // Show popup if "No" is selected
      if (yesNoValue.value === 'no') {
          alert("Your issue is registered. Help desk will contact you soon.");
      }
      return true;
  }

  // Trigger when the user attempts to leave the page
  window.addEventListener('beforeunload', function (e) {
      if (!isFormSubmitted && !checkForm()) {
          const confirmationMessage = 'You have unsaved changes. Please select "Yes" or "No" and a dropdown value.';
          e.returnValue = confirmationMessage;
          return confirmationMessage;
      }
  });

  // Form submission sets the isFormSubmitted flag
  document.getElementById("myForm").addEventListener('submit', function(event) {
      if (!checkForm()) {
          event.preventDefault(); // Prevent submission if form is incomplete
      } else {
          isFormSubmitted = true;
      }
  });
