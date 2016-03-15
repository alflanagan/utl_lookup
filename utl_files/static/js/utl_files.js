/**
 * utl_files -- module of functions for utl_files lookup page
 *
 * @copyright 2016 BH Media Group, Inc.
 * @author A. Lloyd Flanagan
 *
 */


$(function() {

  $("#id_site").on("change", function(evt) {
    var selected_site = evt.target.value;
    $.ajax("utl_files/global_skins_for_site?site=" + selected_site);
  });

});
