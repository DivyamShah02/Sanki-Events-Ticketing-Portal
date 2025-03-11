function setFormValues(data) {
    // Loop through each key-value pair in the dictionary (data)
    for (const key in data) {
        if (data.hasOwnProperty(key)) {
            // Find the input element(s) where name attribute matches the key
            const input = document.querySelector(`[name="${key}"]`);
            const inputs = document.querySelectorAll(`[name="${key}"]`);

            if (input) {
                if (input.type === 'radio') {
                    // If the input is a radio button group, loop through all radio buttons
                    inputs.forEach(radio => {
                        // Check for true/false values and map them to 'Yes'/'No'
                        if ((data[key] === true || data[key] === "true") && radio.value.toLowerCase() === 'yes') {
                            radio.checked = true;  // Select the "Yes" radio button
                        } else if ((data[key] === false || data[key] === "false") && radio.value.toLowerCase() === 'no') {
                            radio.checked = true;  // Select the "No" radio button
                        } else if (radio.value === data[key]) {
                            // For other radio buttons, match by value
                            radio.checked = true;
                        }
                    });
                } else if (input.type === 'checkbox') {
                    // Handle checkboxes
                    if (Array.isArray(data[key])) {
                        // If the data is an array, check each checkbox that matches
                        inputs.forEach(checkbox => {
                            checkbox.checked = data[key].includes(checkbox.value);
                        });
                    } else {
                        // If it's a single value, just check/uncheck the box
                        input.checked = data[key] === true || data[key] === "true";
                    }
                } else if (input.type === 'file') {
                    const file_input = document.querySelector(`[id="${key}"]`);
                    if (file_input) {
                        if (file_input.tagName === 'A' && data[key] !== null) {
                            let file_input_obj = document.getElementById(key)
                            file_input_obj.style.display = 'block';
                            file_input_obj.href = data[key]
                            file_input_obj.innerText = String(data[key]).split('/').pop();
                        } else {
                            let file_input_obj = document.getElementById(key)
                            file_input_obj.style.display = 'block';
                            file_input_obj.src = data[key]
                        }
                    }
                } else {
                    input.value = data[key];
                }
            }
        }
    }

}


function showModal(title, content, callback, submit_not_needed=false) {
    // Create modal HTML structure
    const modalHtml = `
      <div class="modal fade" id="dynamicConfirmationModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">${title}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              ${content}
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="button" class="btn btn-primary eh-btn-blue-primary-no-hover" id="dynamicConfirmModalButton">Continue</button>
            </div>
          </div>
        </div>
      </div>`;

    // Append the modal to the body
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Show the modal
    const modalElement = document.getElementById('dynamicConfirmationModal');
    const bootstrapModal = new bootstrap.Modal(modalElement);
    bootstrapModal.show();

    // Attach event listener to the submit button
    document.getElementById('dynamicConfirmModalButton').addEventListener('click', () => {
        callback(); // Call the provided callback function
        bootstrapModal.hide(); // Hide the modal
        modalElement.remove(); // Remove the modal from the DOM
    });

    if (submit_not_needed) {
        document.getElementById('dynamicConfirmModalButton').style.display = 'none';
    }

    // Clean up modal after hiding
    modalElement.addEventListener('hidden.bs.modal', () => {
        modalElement.remove();
    });
}

function toggle_loader(){
    console.log('loader toggled');
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    const options = { day: 'numeric', month: 'long', year: 'numeric' };

    // Format the date
    let formattedDate = date.toLocaleDateString('en-GB', options);

    // Add suffix to the day
    const day = date.getDate();
    const suffix = (day) => {
        if (day > 3 && day < 21) return 'th';
        switch (day % 10) {
            case 1: return 'st';
            case 2: return 'nd';
            case 3: return 'rd';
            default: return 'th';
        }
    };

    formattedDate = formattedDate.replace(/^\d+/, day + suffix(day));
    return formattedDate;
}
