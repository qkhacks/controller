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

function signUp() {
    
}