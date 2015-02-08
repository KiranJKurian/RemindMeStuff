Parse.initialize("tlF96VIjmcQ7noWTyCcY7q2HQsIYuYKyNW3xsa5Y", "tNoWqeQHONKINhL8ot4GJNNDNNAZqpyRC7wWPqC1");

$('#SignUp').on('submit', function(e){
e.preventDefault();

var User = Parse.Object.extend("User");
var newUser = new User();

newUser.save({
  username: $("#username").val(),
  password: $("#password").val(),
  email: $("#email").val()
},{
  success: function(newUser){
    console.log("Yo it saved");
  }
});
});


var checkUser = new Parse.Query("User");

$('#Login').on('submit', function(e){
e.preventDefault();

Parse.User.logIn($("#login-username").val(), $('#login-password').val(), {
  success: function(user) {
    $('#error').hide();
    $('#showMe').show();

  },
  error: function(user, error) {
    // The login failed. Check error to see why.
    $('#error').show();
  }
});
});

