/**
 * utl_files -- module of functions for utl_files lookup page
 *
 * @copyright 2016 BH Media Group, Inc.
 * @author A. Lloyd Flanagan
 *
 */


$(function() {

    /**
     * Click event handler for global_skin selection control.
     *
     * @param {Object} evt The object describing the event which we
     * are responding to.
     */
    var global_skin_onclick = function(evt) {
        var new_text = evt.target.textContent;
        $("#id_global_skin_label").prop("innerText", new_text);
    };

    /**
     * Click event handler for app_skin selection control.
     *
     * @param {Object} evt The object describing the event which we
     * are responding to.
     */
    var app_skin_onclick = function(evt) {
        var new_text = evt.target.textContent;
        $("#id_app_skin_label").prop("innerText", new_text);
    };


    $("#tree-view").jstree();

    /**
     * Enable a control if there is data in an array, disable otherwise.
     *
     * @param {Array} data The data to check.
     * @param {Object} control The control(s) to be enabled, a JQuery
     * selector.
     */
    var enable_if_data = function(data, control) {
        if (data.length > 0) {
            control.removeAttr("disabled");
        } else {
            control.attr("disabled", "");
        }
    };


    /**
     * for each item in `data`, adds an <li> element to `parent`. The
     * <li> text is the data item, and `click_handler` (if present) is
     * assigned as the item's onclick event handler.
     *
     * @param {Array} data The content to be assigned for each <li>.
     * @param {Object} parent The element(s) to which tags will be
     * added, a Jquery selector.
     * @param {function} click_handler Optional handler for the
     * created elements' onclick event.
     */
    var add_li_from_data = function(data, parent, click_handler) {
        data.forEach(function(datum) {
            var new_elem;
            new_elem = $('<li>' + datum + '</li>');
            if (click_handler != undefined) {
                new_elem.on("click", click_handler);
            };
            parent.append(new_elem);
        });
    };

    // note our dropdown menus have form
    //  <div id="div_id_MODEL">
    //    <button id="id_MODEL_label"></button>
    //    <ul id="id_MODEL">...
    $("#id_site li").on("click", function(evt) {
        var the_site = evt.target.textContent;
        var the_label = $("#id_site_label")[0];

        the_label.innerText = the_site;

        $("#id_global_skin li").detach();
        $("#id_global_skin_label").html("Global Skin<span class=\"caret\">");
        $("#id_app_skin li").detach();
        $("#id_app_skin_label").html("App Skin<span class=\"caret\">");

        $.getJSON("api/global_skins_for_site/" + the_site + "/").done(
            function(data) {
                enable_if_data(data, $("#id_global_skin_label"));
                add_li_from_data(data, $("#id_global_skin"), global_skin_onclick);
            }
        ).fail(function() {
            console.log("ERROR in api call to global_skins_for_site.");
            for (var i = 0; i < arguments.length; i++) {
                console.log(arguments[i]);
            }
        });

        $.getJSON("api/app_skins_for_site/" + the_site + "/").done(
            function(data) {
                enable_if_data(data, $("#id_app_skin_label"));
                add_li_from_data(data, $("#id_app_skin"), app_skin_onclick);
            }
        ).fail(function() {
            console.log("ERROR in api call to app_skins_for_site.");
            for (var i = 0; i < arguments.length; i++) {
                console.log(arguments[i]);
            }
        });
    });
});
