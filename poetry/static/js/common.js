$(function() {
    $("body").on("click", ".delete-view", function (ev) {
        ev.preventDefault();
        var button = $(this);
        var URL = button.attr('href');
        $.ajax({type: "POST", url: URL, data: {}, dataType: "JSON"});
        window.location.replace("/corpus/poem_list")
    });
});