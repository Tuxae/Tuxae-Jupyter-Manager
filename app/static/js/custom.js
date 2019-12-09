function verify_passwords(){
  if ($("#exampleInputPassword").val() != $("#exampleRepeatPassword").val()) {
    flash_sweetalert2('Passwords do not match.', 'Informations', 'error')
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
    html: text,
  })
}
