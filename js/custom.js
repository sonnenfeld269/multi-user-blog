$(document).ready(function() {
    $(".commentbutton").click(function() {
        $(this).parent().parent().find(".commentbox").toggle();
    });
});
