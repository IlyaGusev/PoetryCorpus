$(function() {
    function getParameterByName(name, url) {
        if (!url) {
          url = window.location.href;
        }
        name = name.replace(/[\[\]]/g, "\\$&");
        var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
            results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    }
    $(document).ready(function(){
        if (getParameterByName("rhyme_schema") != null) {
            $("#id_rhyme_schema").val(getParameterByName("rhyme_schema"))
        }
        if (getParameterByName("metre_schema") != null) {
            $("#id_metre_schema").val(getParameterByName("metre_schema"))
        }
        if (getParameterByName("syllables_count") != null) {
            $("#id_syllables_count").val(getParameterByName("syllables_count"))
        }
        if (getParameterByName("line") != null) {
            $("#id_line").val(getParameterByName("line"))
        }
    });
});