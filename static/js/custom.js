(() => {
  $(document).ready(() => {
    var myModal = $('#login_modal')
    var loginButton = $('#sign_in_button')

    loginButton.on('click', (e) => {
      e.preventDefault()
      myModal.modal('toggle')
    })

  })
})();
