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

function getToken(username, password, organizationName, success, error) {
    $.ajax({
        url: "/api/v1/users/token",
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify({
            username: username,
            password: password,
            organization_name: organizationName
        }),
        success: success,
        error: error
    });
}

function getCurrentUser(success, error) {
    $.ajax({
        url: "/api/v1/users/me",
        type: "GET",
        dataType: "json",
        contentType: "application/json",
        headers: getHeaders(),
        success: success,
        error: error
    });
}

function changeCurrentUserPassword(password, success, error) {
    $.ajax({
        url: "/api/v1/users/me/password",
        type: "PUT",
        dataType: "json",
        contentType: "application/json",
        headers: getHeaders(),
        data: JSON.stringify({
            password: password
        }),
        success: success,
        error: error
    });
}

function getOrganization(success, error) {
    $.ajax({
        url: "/api/v1/organization",
        type: "GET",
        dataType: "json",
        contentType: "application/json",
        headers: getHeaders(),
        success: success,
        error: error
    })
}
