function hideAvatar() {
    $('#user_avatar').hide();
}
function updateAvatar(selected_user) {
    $.getJSON("/api/v1/user_avatar/"+selected_user, function(result) {
    	$('#user_avatar img').attr('src', result);
    	$('#user_avatar').show();
    });
}