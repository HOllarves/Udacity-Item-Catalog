var queryString = $("script[src*='js/google-oauth.js']").attr('src').split('?')[1].split("=")[1]
function signInCallback(authResult) {
  console.log("Auth code = ", authResult)
  if(authResult.code) {
    console.log("Here!")
      $.ajax({
          type: 'POST',
          url: '/gconnect?state=' + queryString,
          processData: false,
          contentType: 'application/octet-stream; charset=utf-8',
          data: authResult.code,
          success: function(result) {
              if(result) {
                  setTimeout(function(){
                      window.location.href='/'
                  }, 1000)
              } else {
                setTimeout(function() {
                    window.location.href = "/login?error='auth_failed";
                }, 1000);
              }
          }
      })
  }
}
