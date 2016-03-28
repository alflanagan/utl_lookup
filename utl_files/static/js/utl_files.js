/**
 * utl_files -- module of functions for utl_files lookup page
 *
 * @copyright 2016 BH Media Group, Inc.
 * @author A. Lloyd Flanagan
 *
 */


$(function() {
    console.log("setting selectedIndex to -1");
    $("#id_site").prop("selectedIndex") = -1;
    $("#id_site").on("change", function(evt) {
        var selected_site = evt.target.value;
        $("#id_global_skin option").detach();
        $.getJSON("api/global_skins_for_site/" + selected_site + "/",
            function(data) {
                var new_option;
                $("#id_global_skin").append('<option>Select One:</option>');
                data.forEach(function(datum) {
                    new_option = $('<option value="' + encodeURIComponent(datum) + '">' + datum + '</option>');
                    $("#id_global_skin").append(new_option);
                });
            }
        );
    });
});
