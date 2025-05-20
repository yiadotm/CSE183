// index.js

function url_signer(url, params = {}) {
    let query = Object.keys(params).map(key => `${key}=${encodeURIComponent(params[key])}`).join('&');
    return `${url}?${query}`;
}

let app = {};

let init = (app) => {
    app.data = {
        uncompleted_tasks: [],
        completed_tasks: [],
        mode: "table",
        selected_task: 0,
        task_name: "",
        task_description: "",
        task_deadline: "",
        warning: "",
        users: [],
        past_selected: [],
        display_assign: "",
        comments: [],
        role_warning: "",
        selected_user: null,
        loading_user: false,
    };

    app.enumerate = (a) => {
        let k = 0;
        a.map((e) => { e._idx = k++; });
        return a;
    };

    app.get_selected_users = function() {
        let selected = [];
        app.vue.users.forEach(user => {
            if (user.selected) {
                selected.push(user.id);
            }
        });
        return selected;
    };
    // Get selected users from the past_selected list.
    app.get_selected_past_users = function(){
        let selected = [];
        // Iterate over the past_selected list and check if the user is selected.
        app.vue.past_selected.forEach(user => {
            if (user.selected) {
                selected.push(user.user.id);
            }
        });
        return selected;
    };
    app.switch_mode = function(m, user_id = null) {
        switch (m) {
            case 1:
                app.vue.mode = "table";
                app.get_tasks();
                break;
            case 2:
                app.vue.mode = "add";
                break;
            case 3:
                app.vue.mode = "edit";
                break;
            case 4:
                app.vue.mode = "addrole";
                app.get_users();
                break;
            case 5:
                app.vue.mode = "detail";
                break;
            case 6:
                app.vue.mode = "editrole";
                app.get_users();
                break;
            case 7:
                app.vue.mode = "edituserrole";
                app.vue.loading_user = true;
                console.log(`Fetching user with ID: ${user_id}`);
                app.get_user(user_id);
                break;
            default:
                app.vue.mode = "table";
                app.get_tasks();
        }
    };

    app.show_detail = function(task) {
        app.vue.selected_task = task.id;
        app.vue.task_name = task.name;
        app.vue.task_description = task.description;
        app.vue.task_deadline = task.deadline;
        app.vue.display_assign = task.assigned.join(", ");
        app.switch_mode(5);
    };

    app.edit_mode = function(task) {
        app.vue.selected_task = task.id;
        app.vue.task_name = task.name;
        app.vue.task_description = task.description;
        app.vue.task_deadline = task.deadline;
        app.get_users(task.assigned);
        app.switch_mode(3);
    };

    app.update = function() {
        if (app.vue.mode == "edit") {
            axios.post(edit_url, {
                task_id: app.vue.selected_task,
                name: app.vue.task_name,
                description: app.vue.task_description,
                deadline: app.vue.task_deadline,
                assigned: app.get_selected_users(),
            }).then(function(response) {
                app.vue.selected_task = 0;
                app.vue.task_name = "";
                app.vue.task_description = "";
                app.vue.task_deadline = "";
                app.vue.users = [];
                app.switch_mode(1);
                app.get_tasks();
            });
        }

        if (app.vue.mode == "add") {
            if (app.vue.task_name === "") {
                app.vue.warning = "Type task name";
                return;
            }
            if (app.vue.task_description === "") {
                app.vue.warning = "Type description";
                return;
            }
            if (app.vue.task_deadline === "") {
                app.vue.warning = "Type deadline";
                return;
            }

            app.vue.warning = "";

            axios.post(add_url, {
                name: app.vue.task_name,
                description: app.vue.task_description,
                deadline: app.vue.task_deadline,
                assigned: app.get_selected_users(),
            }).then(function(response) {
                app.vue.selected_task = 0;
                app.vue.task_name = "";
                app.vue.task_description = "";
                app.vue.task_deadline = "";
                app.vue.users = [];
                app.switch_mode(1);
                app.get_tasks();
            });
        }
    };

    app.get_tasks = function() {
        axios.get(url_signer(get_tasks_url)).then(function(response) {
            app.vue.uncompleted_tasks = app.enumerate(response.data.uncompleted);
            app.vue.completed_tasks = app.enumerate(response.data.completed);
            app.ensure_comments(app.vue.uncompleted_tasks);
            app.ensure_comments(app.vue.completed_tasks);

            app.vue.uncompleted_tasks.forEach(task => {
                task.timeleft = Sugar.Date(task.timeleft).relative().raw;
            });
        });
    };

    app.completed = function(task_id) {
        axios.post(url_signer(complete_task_url), { task_id: task_id }).then(function(response) {
            app.get_tasks();
        });
    };

    app.get_users = function(selected_users = []) {
        axios.get(url_signer(get_users_url)).then(function(response) {
            console.log("User IDs from DB:", response.data.users.map(user => user.id));
            let users = response.data.users.map(user => {
                console.log("User Data:", user);  // Log each user data
                return {
                    id: user.id,
                    first_name: user.first_name,
                    last_name: user.last_name,
                    email: user.email,
                    role: user.role || 'User',
                    selected: selected_users.includes(user.id),
                    manager_id: user.manager_id || null
                };
            });
            app.vue.users = app.enumerate(users);
        });
    };

    app.assign_user = function(idx) {
        app.vue.users[idx].selected = !app.vue.users[idx].selected;
    };



    app.get_user = function(user_id) {
        console.log("Fetching user with ID:", user_id);
        let url = url_signer(get_user_url + '/' + user_id);
        console.log("Request URL:", url);
        axios.get(url)
            .then(response => {
                console.log("User data:", response.data);
                if (response.data.error) {
                    console.error(response.data.error);
                } else {
                    app.vue.selected_user = response.data.user;
                    app.vue.selected_user.role = response.data.role || 'User';
                    app.vue.selected_user.manager_id = response.data.manager_id || 1;

                    // Filter out the current user from the list of users for the manager dropdown
                    app.vue.users = app.vue.users.filter(user => user.id !== user_id);
                    app.vue.loading_user = false;
                }
            })
            .catch(error => {
                console.error("Error fetching user:", error);
                app.vue.loading_user = false;
            });
    };


    // app.update_user_role = function() {
    //     if (app.vue.selected_user.role === 'CEO' && app.vue.users.some(u => u.role === 'CEO' && u.id !== app.vue.selected_user.id)) {
    //         app.vue.role_warning = 'CEO role is already taken';
    //         return;
    //     }
    //     let url = url_signer(update_user_role_url);
    //     console.log("Request URL for update_user_role:", url);
    //     console.log("Request data:", {
    //         user_id: app.vue.selected_user.id,
    //         role: app.vue.selected_user.role,
    //         manager_id: app.vue.selected_user.manager_id
    //     });
    //     axios.post(url, {
    //         user_id: app.vue.selected_user.id,
    //         role: app.vue.selected_user.role,
    //         manager_id: app.vue.selected_user.manager_id
    //     })
    //     .then(response => {
    //         if (response.data.success === false) {
    //             console.error(response.data.message);
    //             app.vue.role_warning = response.data.message;
    //         } else {
    //             console.log(response.data.message);
    //             app.switch_mode(4); // Go back to user list
    //         }
    //     })
    //     .catch(error => {
    //         console.error("Error assigning role:", error);
    //     });
    // };
    
    

    app.update_user_role = function() {
        if (app.vue.selected_user.role === 'CEO' && app.vue.users.some(u => u.role === 'CEO' && u.id !== app.vue.selected_user.id)) {
            app.vue.role_warning = 'CEO role is already taken';
            return;
        }
        
        let url = url_signer(update_user_role_url);
        
        console.log("Request URL for update_user_role:", url);
        console.log("Request data:", {
            user_id: app.vue.selected_user.id,
            role: app.vue.selected_user.role
        });
        
        axios.post(url, {
            user_id: app.vue.selected_user.id,
            role: app.vue.selected_user.role
        }, { withCredentials: true })
        .then(response => {
            if (response.data.success === false) {
                console.error(response.data.message);
                app.vue.role_warning = response.data.message;
            } else {
                console.log(response.data.message);
                app.switch_mode(4); // Go back to user list
            }
        })
        .catch(error => {
            console.error("Error updating user role:", error);
            if (error.response) {
                console.error("Response data:", error.response.data);
                console.error("Response status:", error.response.status);
                console.error("Response headers:", error.response.headers);
                if (error.response.status === 403) {
                    app.vue.role_warning = "You do not have permission to perform this action.";
                } else {
                    app.vue.role_warning = "An error occurred while updating the role.";
                }
            } else if (error.request) {
                console.error("Request data:", error.request);
                app.vue.role_warning = "No response received from server.";
            } else {
                console.error("Error message:", error.message);
                app.vue.role_warning = "Error in setting up the request.";
            }
        });
    };
    
    
    
    
    
    
    app.update_manager_id = function() {
        let url = url_signer(update_manager_id_url);
        console.log("Request URL for update_manager_id:", url);
        console.log("Request data:", {
            user_id: app.vue.selected_user.id,
            manager_id: app.vue.selected_user.manager_id
        });
        axios.post(url, {
            user_id: app.vue.selected_user.id,
            manager_id: app.vue.selected_user.manager_id
        })
        .then(response => {
            if (response.data.success === false) {
                console.error(response.data.message);
                app.vue.role_warning = response.data.message;
            } else {
                console.log(response.data.message);
                app.switch_mode(4); // Go back to user list
            }
        })
        .catch(error => {
            console.error("Error updating manager ID:", error);
        });
    };
    
    app.test_endpoint = function() {
        let url = url_signer(test_endpoint_url);
        console.log("Request URL for test_endpoint:", url);
        axios.get(url, { withCredentials: true })
            .then(response => {
                console.log("Test endpoint response:", response.data);
            })
            .catch(error => {
                console.error("Error testing endpoint:", error);
                if (error.response) {
                    console.error("Response data:", error.response.data);
                    console.error("Response status:", error.response.status);
                    console.error("Response headers:", error.response.headers);
                } else if (error.request) {
                    console.error("No response received. Request details:", error.request);
                } else {
                    console.error("Error message:", error.message);
                }
            });
    };
    
    // Call the test endpoint
    app.test_endpoint();
    
    
    
    

    app.add_comment = function(task) {
        if (task.new_comment && task.new_comment.trim()) {
            const comment = {
                text: task.new_comment,
                user_name: 'Current User', // Replace with actual user's name
                created_on: new Date().toISOString(), // Use ISO string format for datetime
                task_id: task.id
            };
            axios.post(url_signer(save_comment_url), {
                comment: comment
            }).then(function(response) {
                if (response.data.success) {
                    task.comments.push(comment);
                    task.new_comment = '';
                    app.get_tasks(); // Refresh tasks to get the latest comments from server
                } else {
                    console.error(response.data.message);
                }
            }).catch(function(error) {
                console.error(error);
            });
        }
    };

    app.delete_comment = function(task, comment) {
        axios.post(url_signer(delete_comment_url), {
            comment_id: comment.id
        }).then(function(response) {
            if (response.data.success) {
                const index = task.comments.indexOf(comment);
                if (index !== -1) {
                    task.comments.splice(index, 1);
                }
            } else {
                console.error(response.data.message);
            }
        }).catch(function(error) {
            console.error(error);
        });
    };

    app.ensure_comments = (tasks) => {
        tasks.forEach(task => {
            if (!task.comments) {
                task.comments = [];
            }
        });
    };

    app.methods = {
        get_tasks: app.get_tasks,
        completed: app.completed,
        switch_mode: app.switch_mode,
        edit_mode: app.edit_mode,
        get_users: app.get_users,
        assign_user: app.assign_user,
        update: app.update,
        show_detail: app.show_detail,
        add_comment: app.add_comment,
        delete_comment: app.delete_comment,
        update_user_role: app.update_user_role,
        get_user: app.get_user
    };

    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {
        app.get_tasks();
        app.switch_mode(1);
        app.test_endpoint();
    };

    app.init();
};

init(app);
