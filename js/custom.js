$(document).ready(function() {

    // if url does not contain "comments" then hide the commentbox
    if (window.location.href.indexOf("comments") < 0) {
        $(".commentbox").hide();
    }

    $(".commentbutton").click(function() {
        $(this).parent().parent().find(".commentbox").toggle();
    });
});
