/**
 * utl_files -- module of functions for utl_files lookup page
 *
 * @copyright 2016 BH Media Group, Inc.
 * @author A. Lloyd Flanagan
 *
 */


$(function() {
    $("#div_id_site ul.dropdown-menu li").on("click", function(evt) {
        var the_site = evt.target.textContent;
        $("#selected_site").value = the_site;
        $("#id_global_skin li").detach();
        $.getJSON("api/global_skins_for_site/" + the_site + "/",
            function(data) {
                var new_option;
                data.forEach(function(datum) {
                    new_option = $('<li>' + datum + '</li>');
                    $("#id_global_skin").append(new_option);
                });
            }
        );
        $("#id_app_skin li").detach();
        $.getJSON("api/app_skins_for_site/" + the_site + "/",
            function(data) {
                var new_option;
                data.forEach(function(datum) {
                    new_option = $('<li>' + datum + '</li>');
                    $("#id_app_skin").append(new_option);
                });
            }
        );
    });
});
