$(function() {
    Mousetrap.bind('ctrl+left', function() {
        var prevButton = document.getElementById("prev-button");
        prevButton.click();
        return false;
    });

    Mousetrap.bind('ctrl+right', function() {
        var nextButton = document.getElementById("next-button");
        nextButton.click();
        return false;
    });

    Mousetrap.bind('ctrl+enter', function() {
        var markupsButton = document.getElementById("to-markups-button");
        markupsButton.click();
        return false;
    });

    Mousetrap.bind('shift+enter', function() {
        if( $(".edit-plain-text").hasClass("hidden") ) {
            var editButton = document.getElementById("edit-button");
            editButton.click();
            document.getElementById("edit-text-field").focus();
        } else if( $(".plain-text").hasClass("hidden") ) {
            var saveButton = document.getElementById("save-button");
            saveButton.click();
        }
        return false;
    });

    $(document).on('click', '#edit-button', function(){
        $("#edit-button").addClass("hidden");
        $(".plain-text").addClass("hidden");
        $(".edit-plain-text").removeClass("hidden");
    });

    $(document).on('click', '#cancel-button', function(){
        $("#edit-button").removeClass("hidden");
        $(".plain-text").removeClass("hidden");
        $(".edit-plain-text").addClass("hidden");
        return false;
    });

    $(document).on('click', '#save-button', function(){
        $("#edit-button").removeClass("hidden");
        $(".plain-text").removeClass("hidden");
        $(".edit-plain-text").addClass("hidden");
        $.ajax({
            type: 'POST',
            url: window.location.href,
            data: {
                'text': $('#edit-text-field').val(),
                'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
            },
            success: function(response) {
                window.location.replace(response.url)
            },
            error: function(request, status, error) {
                console.log(error)
            }
        });
        return false;
    });
});