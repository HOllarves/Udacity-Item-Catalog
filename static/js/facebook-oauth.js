var queryString = $("script[src*='js/facebook-oauth.js']").attr('src').split('?')[1].split("=")[1]
window.fbAsyncInit = function() {
    FB.init({
      appId      : '1897120940534038',
      cookie     : true,
      xfbml      : true,
      version    : 'v2.8'
    });
    FB.AppEvents.logPageView();
    };
    (function(d, s, id){
        var js, fjs = d.getElementsByTagName(s)[0];
        if (d.getElementById(id)) {return;}
        js = d.createElement(s); js.id = id;
        js.src = "//connect.facebook.net/en_US/sdk.js";
        fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));
    function sendTokenToServer() {
        var access_token = FB.getAuthResponse()['accessToken'];
        console.log(access_token)
        console.log('Welcome!  Fetching your information....');
        FB.api('/me', function(response) {
            console.log('Successful login for: ' + response.name);
        $.ajax({
            type: 'POST',
            url: '/fbconnect?state=' + queryString,
            processData: false,
            data: access_token,
            contentType: 'application/octet-stream; charset=utf-8',
            success: function(result) {
              console.log(result)
                // Handle or verify the server response if necessary.
                if (result) {
                    setTimeout(function() {
                        window.location.href = "/";
                    }, 1000);
                } else {
                  setTimeout(function() {
                      window.location.href = "/login?error='auth_failed";
                  }, 1000);
                }
            }
        });
    });
}
