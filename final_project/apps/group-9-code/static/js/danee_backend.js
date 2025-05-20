"user strict";

// Handle form submission
document.getElementById("task-creation-form").addEventListener("submit", function(event) {
    // Prevent default form submission
    event.preventDefault();
    // Extract task data from form fields
    var taskData = {
        title: document.getElementById("title").value,
        description: document.getElementById("description").value,
        deadline: parseInt(document.getElementById("deadline").value), // directly assign the deadline value
    };

    // Send POST request to server
    fetch("/group-9-code/index", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(taskData)
    })
    .then(response => response.json())
    .then(data => {
        // Fetch and display the updated list of tasks
        fetchTasks();
    });
});

// Fetch and display tasks
function fetchTasks() {
    // Send GET request to server
    fetch("/group-9-code/index")
        .then(response => {
            // Check if the response is ok
            if (!response.ok) {
                // Throw an error if the response is not ok
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            // Parse the response as JSON
            return response.json();
        })
        .then(data => {
            // Get the task list section
            var taskListSection = document.getElementById("task-list-section");

            // Clear the task list section
            taskListSection.innerHTML = '';

            // Add a heading to the task list section
            taskListSection.innerHTML += '<h2>Your Tasks</h2>';

            // Create a document fragment to improve performance
            var fragment = document.createDocumentFragment();

            // Loop through the tasks
            data.tasks.forEach(task => {
                // Create a new div for each task
                var taskDiv = document.createElement('div');
                taskDiv.className = 'task';

                var taskTitle = document.createElement('h3');
                taskTitle.textContent = task.title;
                taskDiv.appendChild(taskTitle);

                var taskDescription = document.createElement('p');
                taskDescription.textContent = task.description;
                taskDiv.appendChild(taskDescription);

                var taskDeadline = document.createElement('p');
                taskDeadline.textContent = `Deadline: ${task.deadline} days`;
                taskDiv.appendChild(taskDeadline);

                // Append the task div to the fragment
                fragment.appendChild(taskDiv);
            });

            // Append the fragment to the task list section
            taskListSection.appendChild(fragment);
        })
        .catch(error => {
            // Log any errors that occur during the fetch operation
            console.error('There was a problem with the fetch operation:', error);

            // Provide user feedback on the UI
            var taskListSection = document.getElementById("task-list-section");
            taskListSection.innerHTML = '<p>Failed to load tasks. Please try again later.</p>';
            alert(error.message);
        });
}


// Fetch and display tasks when the page loads
fetchTasks();    