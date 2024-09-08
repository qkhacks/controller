function displayError(parent, message) {
    parent.html(`
        <div class='alert alert-danger alert-dismissible'>
           ${message}
           <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `);
}

function displaySuccess(parent, message) {
    parent.html(`
        <div class='alert alert-success alert-dismissible'>
           ${message}
           <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `);
}

function getHeaders() {
    return {
        Authorization: `Bearer ${localStorage.getItem("token")}`
    }
}

function signUp(username, password, organizationName, success, error) {
    $.ajax({
        url: "/api/v1/users/signup",
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify({
            username: username,
            password: password,
            organization_name: organizationName,
        }),
        success: success,
        error: error
    });
}
