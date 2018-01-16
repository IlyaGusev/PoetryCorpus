function getQueryVariable(variable) {
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i=0;i<vars.length;i++) {
        var pair = vars[i].split("=");
        if (pair[0] == variable) {
            return pair[1];
        }
    }
}

$(function() {
    $(document).ready(function(){
        VOWELS = "aeiouAEIOUаоэиуыеёюяАОЭИУЫЕЁЮЯ";
        var diffs = {};
        var activeSylIndex = 0;
        var syllables = $('.syllable');
        syllables[0].style.border = "3px solid red";

        Mousetrap.bind('enter', function() {
            var syllable = $('.syllable')[activeSylIndex];
            syllable.click();
            return false;
        });

        Mousetrap.bind('right', function() {
            if( activeSylIndex < syllables.length - 1 ) {
                syllables[activeSylIndex].style.border = "none";
                activeSylIndex += 1;
                syllables[activeSylIndex].style.border = "3px solid red";
            }
            return false;
        });

        Mousetrap.bind('left', function() {
            if( activeSylIndex > 0 ) {
                syllables[activeSylIndex].style.border = "none";
                activeSylIndex -= 1;
                syllables[activeSylIndex].style.border = "3px solid red";
            }
            return false;
        });

        Mousetrap.bind('ctrl+s', function() {
            var sendButton = $('.send-markup');
            sendButton.click();
            return false;
        });

        Mousetrap.bind('backspace', function() {
            var toTextButton = document.getElementById("to-text-button");
            toTextButton.click();
            return false;
        });

        Mousetrap.bind('del', function() {
             var deleteButton = document.getElementById("delete-button");
             deleteButton.click();
        });

        addToSet = function(id) {
            if (!diffs[id]) {
                diffs[id] = true
            } else {
                delete diffs[id]
            }
        };

        $(document).on('click','.syllable',function(){
            var id = this.id;
            var word_id = id.split('-')[0] + '-' + id.split('-')[1];
            var text = $(this).text();
            var accented = $(this).hasClass('green') && $(this).hasClass('bck');
            if( !accented ) {
                var accent = -1;
                for (var i = 0; i < text.length; i++) {
                    if (VOWELS.indexOf(text[i]) != -1) {
                        accent = i;
                        break;
                    }
                }
                var accent_elems = $('#' + word_id).find('.bck.green,.bck.red');
                if (accent_elems.length) {
                    accent_elems.each(function (index) {
                        var removing_id = $(this)[0].id;
                        addToSet(removing_id);
                        $(this).removeClass('green');
                        $(this).removeClass('red');
                        $(this).addClass('default');
                    });
                }
                $(this).removeClass('default');
                $(this).addClass('green');
                addToSet(id);
            } else {
                $(this).removeClass('green');
                $(this).addClass('default');
                addToSet(id);
            }
        });

        $(".markup-selector").ready(function() {
            if( window.location.href.indexOf('markup') !== -1 ){
                var elems = window.location.href.split('/');
                $('.markup-selector option[value=' + elems[elems.length - 2] + ']').attr('selected','selected');
            } else {
                $('.markup-selector option[value=0]').attr('selected','selected');
            }
        });


        $(".markup-selector").change(function() {
            $( ".markup-selector option:selected" ).each(function() {
                var id = $(this).val();
                var href = "";
                if( id != 0 ) {
                    href = "/corpus/markups/" + id;
                } else{
                    href = "/corpus/poems/" + $(".poem")[0].id;
                }
                window.location.replace(href)
            });
        });

        $(document).on('click','.send-markup',function(){
            $.ajax({
                type: 'POST',
                url: window.location.href,
                data: {
                    'diffs[]': Object.keys(diffs),
                    'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
                },
                success: function(response) {
                    window.location.replace(response.url)
                },
                error: function(request, status, error) {
                    console.log(error)
                }
            });
        });

        $(document).on('click','.compare',function(){
            var standard_pk = $(".standard").val();
            var test_pk = $(".test").val();
            var href = "/corpus/comparison?test=" + test_pk + "&standard=" + standard_pk + "&document=" + $("#poem_pk").text();
            $.ajax({
                type: 'GET',
                url: window.location.href,
                success: function(response) {
                    window.location.replace(href)
                },
                error: function(request, status, error) {
                    console.log(error)
                }
            });
        });

        $(document).on('click', '.compare-versions', function(){
            if( $(this).hasClass("disabled") ) {
                return;
            }
            var standard_pk = selected_version[0];
            var test_pk = selected_version[1];
            var href = "/corpus/comparison?test=" + test_pk + "&standard=" + standard_pk;
            $.ajax({
                type: 'GET',
                url: window.location.href,
                success: function(response) {
                    window.location.replace(href)
                },
                error: function(request, status, error) {
                    console.log(error)
                }
            });
        });

        $(document).on('click','.compare-csv',function(){
            var standard_pk = getQueryVariable("standard");
            var test_pk = getQueryVariable("test");
            var href = "/corpus/comparison_csv?test=" + test_pk + "&standard=" + standard_pk;
            $.ajax({
                type: 'GET',
                url: window.location.href,
                success: function(response) {
                    window.location.replace(href)
                },
                error: function(request, status, error) {
                    console.log(error)
                }
            });
        });

        var selected_version = [];
        $('#versions').on('click','.version-select',function(){
            var id = $(this)[0].id;
            if ($(this)[0].checked) {
                selected_version.push(id);
            } else {
                selected_version.splice(selected_version.indexOf(id), 1);
            }
            var compareButton = $('.compare-versions');
            if( selected_version.length == 2 ) {
                compareButton.removeClass("disabled")
            } else if( !compareButton.hasClass("disabled") ){
                compareButton.addClass("disabled")
            }

            var exportButton = $('.export-versions');
            if( selected_version.length != 0 ) {
                exportButton.removeClass("disabled")
            } else if( !exportButton.hasClass("disabled") ){
                exportButton.addClass("disabled")
            }
        });

        $(document).on('click', '.export-versions', function(){
            if( $(this).hasClass("disabled") ) {
                return;
            }
            for (var i = 0; i < selected_version.length; i++) {
                var version_pk = selected_version[i];
                var href = "/corpus/export_version/" + version_pk;
                $.ajax({
                    type: 'GET',
                    url: window.location.href,
                    success: function(response) {
                        window.location.replace(href)
                    },
                    error: function(request, status, error) {
                        console.log(error)
                    }
                });
            }
        });
        $(document).on('click', '#markup-make-standard', function(){
            $.ajax({
                type: 'POST',
                url: this.href,
                data: {},
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
});