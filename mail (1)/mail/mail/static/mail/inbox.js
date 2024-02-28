document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', () => compose_email('compose'));



  // By default, load the inbox
  load_mailbox('inbox');

  document.querySelectorAll('.email').forEach(email => {
        email.addEventListener('click', function() {
            const emailId = this.dataset.id; // Get the email ID from data attribute

            alert(emailId)
            view_email(emailId, 'inbox'); // Call view_email function with email ID and current mailbox
        });
    });
});

function compose_email() {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';

  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  // Add event listener for form submission
  document.querySelector('#compose-form').onsubmit = function(event) {
    event.preventDefault(); // Prevent default form submission

    // Get form values
    const recipients = document.querySelector('#compose-recipients').value;
    const subject = document.querySelector('#compose-subject').value;
    const body = document.querySelector('#compose-body').value;

    const jsonData = {
        recipients: recipients,
        subject: subject,
        body: body
    };
    console.log('JSON Data:', jsonData);
    // Send the email
    fetch('/emails', {
  method: 'POST',
  body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
  })
})
.then(response => response.json())
.then(result => {
    // Print result
    console.log(result);
});
  };
}

// The remaining functions (load_mailbox, view_email, reply_to_email) remain unchanged


function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Fetch emails from the server
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    // Create HTML for displaying emails
    let emailsHTML = '';
    emails.forEach(email => {
      const emailDiv = document.createElement('div');
      emailDiv.classList.add('email');
      if (!email.read) {
              emailDiv.classList.add('unread'); // Apply different style to unread emails
            }
      emailDiv.innerHTML = `
        <strong>${email.sender}</strong>: ${email.subject} - ${email.timestamp}
      `;
      emailDiv.dataset.id = email.id; // Add data-id attribute to store email ID
      emailsHTML += emailDiv.outerHTML;
    });

    // Display emails
    document.querySelector('#emails-view').innerHTML += emailsHTML;

    // Attach event listener for clicking on emails
    document.querySelectorAll('.email').forEach(email => {
      email.addEventListener('click', function() {
        const emailId = this.dataset.id; // Get the email ID from data attribute
        view_email(emailId, mailbox); // Call view_email function with email ID and current mailbox
      });
    });
  })
  .catch(error => console.error('Error fetching emails:', error));
}



function view_email(email_id, current_mailbox) {
  // Fetch the email details from the server
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
    // Show the email view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'block';

    // Clear previous email content
    document.querySelector('#email-view').innerHTML = '';

    // Mark the email as read
    if (!email.read) {
      fetch(`/emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({
          read: true
        })
      })
      .then(response => {
        if (response.ok) {
          console.log(`Email ${email_id} marked as read.`);
          document.querySelector(`.email[data-id="${email_id}"]`).classList.remove('unread');

        } else {
          console.error(`Error marking email ${email_id} as read.`);
        }
      })
      .catch(error => console.error('Error marking email as read:', error));


    }

    // Display email details
    document.querySelector('#email-view').innerHTML = `
      <h3>Subject: ${email.subject}</h3>
      <p><strong>From:</strong> ${email.sender}</p>
      <p><strong>To:</strong> ${email.recipients.join(', ')}</p>
      <p><strong>Timestamp:</strong> ${email.timestamp}</p>
      <hr>
      <p>${email.body}</p>
    `;

    if(current_mailbox!=='sent') {
      // Add buttons for archiving and unarchiving
      const archiveButton = document.createElement('button');
      archiveButton.textContent = current_mailbox === 'inbox' ? 'Archive' : 'Unarchive';
      archiveButton.addEventListener('click', () => {
        // Archive or unarchive the email
        const archiveStatus = current_mailbox === 'inbox' ? true : false; // Toggle archive status
        fetch(`/emails/${email_id}`, {
          method: 'PUT',
          body: JSON.stringify({
            archived: archiveStatus
          })
        })
            .then(response => {
              if (response.ok) {
                console.log(`Email ${email_id} ${archiveStatus ? 'archived' : 'unarchived'}.`);
                // Hide the email view
                document.querySelector('#email-view').style.display = 'none';
                // Show the email list
                document.querySelector('#emails-view').style.display = 'block';
                load_mailbox(current_mailbox); // Load inbox after archiving or unarchiving
              } else {
                console.error(`Error ${archiveStatus ? 'archiving' : 'unarchiving'} email ${email_id}.`);
              }
            })
            .catch(error => console.error(`Error ${archiveStatus ? 'archiving' : 'unarchiving'} email:`, error));
      });
      document.querySelector('#email-view').appendChild(archiveButton);
    }
    // Add Reply button
    const replyButton = document.createElement('button');
    replyButton.textContent = 'Reply';
    replyButton.addEventListener('click', () => reply_to_email(email));
    document.querySelector('#email-view').appendChild(replyButton);

    // Add back button to return to the mailbox view
    const backButton = document.createElement('button');
    backButton.textContent = 'Back';
    backButton.addEventListener('click', () => {
      // Show the email list
      document.querySelector('#emails-view').style.display = 'block';

      // Hide the email view
      document.querySelector('#email-view').style.display = 'none';

      // Reload the mailbox
      load_mailbox(current_mailbox);
    });
    document.querySelector('#email-view').appendChild(backButton);
  })
  .catch(error => console.error('Error fetching email:', error));
}

function reply_to_email(email) {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';

  // Pre-fill composition fields
  document.querySelector('#compose-recipients').value = email.sender;
  document.querySelector('#compose-subject').value = email.subject.startsWith('Re:') ? email.subject : `Re: ${email.subject}`;
  document.querySelector('#compose-body').value = `\n\nOn ${email.timestamp} ${email.sender} wrote:\n${email.body}`;
}