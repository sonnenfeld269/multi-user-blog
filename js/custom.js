$(document).ready(function() {
    $(".commentbox").hide();
    $(".commentbutton").click(function() {
        $(this).parent().parent().find(".commentbox").toggle();
    });
});
