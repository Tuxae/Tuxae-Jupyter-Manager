function verify_passwords(){
  if ($("#exampleInputPassword").val() != $("#exampleRepeatPassword").val()) {
    flash_sweetalert2('Passwords do not match.', 'Information', 'error')
  }
  else {
    document.forms['customForm'].submit(); 
    return false;
  }
}

function flash_sweetalert2(text, title, category) {
  Swal.fire({
    type: category,
    title: title,
    html: he.decode(text),
  })
}

function sweetalert2_docker_logs(container_id, title, category) {
    const logsAPI = 'containers/' + container_id + '/logs';
    const inputValue = fetch(logsAPI, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    },
    ).then(response => {
      if (response.ok) {
        response.json().then(json => {
          Swal.fire({
            width: 1000,
            type: category,
            title: title,
            html: he.decode(json.html),
          });
        });
      }
    });
}
