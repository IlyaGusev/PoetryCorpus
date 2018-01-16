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

    var fields = ['author', 'name'];
    var ajax_fields = ['author', 'name'];

    function transfer_class(attr, elem2, elem1){
        $(elem1).addClass(attr);
		$(elem2).removeClass(attr);
    }

    function post_poem(dict){
        var reload = false;
        for (var key in dict) {
             if (($.inArray(key, ajax_fields)) === -1) {
                 reload = true;
             }
        }
        $.ajax({
            type: 'POST',
            url: window.location.href,
            data: dict,
            success: function(response) {
                if (reload) {
                    window.location.reload();
                    return;
                }
                for (var field in dict){
                    var isAjax = $.inArray(field, ajax_fields) !== -1;
                    if (isAjax) {
                        var elem = $('#'+field+'-current')
                        elem.text($('#'+field+'-field').val())
                        elem.html(elem.html().replace(/\r\n|\r|\n/g,'<br>'))
                    }
                }
            },
            error: function(request, status, error) {
                console.log(error)
            }
        });
    }

    $(document).on('click', '#save-button', function(){
        $("#edit-button").removeClass("hidden");
        $(".plain-text").removeClass("hidden");
        $(".edit-plain-text").addClass("hidden");
        var dict = {};
        dict['text'] = $('#edit-text-field').val();
        post_poem(dict);
    });

    $.each(fields, function (index, key) {
        var field = '#' + key;
	    $(field+'-pencil').click(function() {
            transfer_class('hidden', field+'-edit', field);
            $(field+'-field').focus();
        });

        $(field+'-field').blur(function() {
            transfer_class('hidden', field, field+'-edit');
            var dict = {};
            dict[key] = $(field+'-field').val();
            post_poem(dict);
        });
	});

    $("body").on("click", ".delete-view", function(ev) {
        ev.preventDefault();
        var button = $(this);
        var URL = button.attr('href');
        $.ajax({type: "POST", url: URL, data: {}, dataType: "JSON"});
        window.location.replace("/corpus/poem_list")
    });

    $(document).on('click', '#poem-make-standard', function(){
        console.log(this.href)
        $.ajax({
            type: 'POST',
            url: this.href,
            data: {
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