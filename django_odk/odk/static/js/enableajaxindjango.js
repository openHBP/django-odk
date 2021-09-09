/*
 * utilitaire pour utilisation csrsafe token avec ajax
 * https://stackoverflow.com/questions/19333098/403-forbidden-error-when-making-an-ajax-post-request-in-django-framework
 */
/* for some reason, in https, the cookie is not initialised at the first page refresh
function getCookie (name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
*/
var csrftoken = $('input[name="csrfmiddlewaretoken"]').val();

function csrfSafeMethod (method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
        	console.log('ajax:'+csrftoken);
        	xhr.withCredentials = true;
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

/** ************************** JPH tools *************************** */

/**
 * function to escape specialchars in nodes id
 * 
 * @param myid
 * @returns the escaped id
 */
function jq_safe_id (myid) {

    return "#" + myid.replace(/(:|\.|\[|\]|,|=|\|)/g, "\\$1");

}
