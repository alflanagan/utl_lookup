/**
 * utl_files -- module of functions for utl_files lookup page
 *
 * @copyright 2016 BH Media Group, Inc.
 * @author A. Lloyd Flanagan
 *
 */

/* jshint 
      esversion: 6, unused: true, curly: true, eqeqeq: true, forin: true, noarg: true,
      nocomma: true, strict: true, undef: true, varstmt: true, jquery: true, devel: true,
      asi: true
*/

$(function () {
    "use strict";

    // ID selector strings, use constant to avoid mistyping
    const GLOBAL_LIST = "#pkgs_global_list",
        SKIN_LIST = "#pkgs_skin_list",
        BLOCK_LIST = "#pkgs_blocks_list",
        COMP_LIST = "#pkgs_components_list",
        TREE_VIEW = "#tree-view",
        INNER_TEXT = "innerText";

    /**
     * An object that represents a bootstrap dropdown control on the page.
     *
     * @param {String} ul_id The id attribute of the <ul> element used
     * for dropdown
     * @param {String} label_id The id attribute of the <button>
     * element acting as a label/trigger
     * @param {String} label_text The text to show on the control when
     * no item is selected
     * @param {Function} select_handler Function called when a
     * drop-down item is selected. Gets this object as an argument
     *
     */
    const DropDownControl = function (ul_id, label_id, label_text, select_handler) {
            this.label_id = label_id
            this.ul_id = ul_id
            this.label_text = label_text
            this.picked = false
            this.handler = select_handler

            /**
             * An event handler bound to this control, triggered when one
             * of the dropdown items is clicked. Updates control, then calls
             * user-supplied handler, if any.
             */
            let onclick = function (evt) {
                const new_text = evt.target.textContent
                $(this.label_id).prop(INNER_TEXT, new_text)
                this.picked = true
                this.handler(this)
            }
            this.onclick = onclick.bind(this)

            /** 
             * @return {String} The text of the currently selected item
             */
            this.text = () => $(this.label_id).prop("innerText")

            /**
             * Fills the dropdown with strings in items param
             *
             * Clicking one of the strings will trigger the onclick() method.
             *
             * @param {Array} data A list of items to be added.
             */
            this.add_li_from_data = data => {
                    this.picked = false
                    data.forEach(
                            function (datum) {
                                const new_elem = $('<li>' + datum + '</li>')
                                new_elem.on("click", this.onclick)
                                $(this.ul_id).append(new_elem)
                            })
                        // don't force user to select from a set of one
                    if (data.length === 1) {
                        $(this.ul_id).children("li").click()
                        this.picked = true
                    }
                    if (data.length === 0) {
                        $(this.label_id).attr("disabled", "")
                            // if we are empty, don't block filling tree
                        this.picked = true
                    } else {
                        $(this.label_id).removeAttr("disabled")
                    }
                } //add_li_from_data

            /**
             * Resets dropdown to empty, disabled state
             */
            this.reset = () => {
                $(this.ul_id + " li").detach()
                $(this.label_id).html(this.label_text + "<span class=\"caret\">")
                $(this.label_id).attr("disabled", "")
                this.picked = false
            }

            return this;

        } // DropDownControl

    let site_control = new DropDownControl("#id_site", "#id_site_label", "Site"),
        global_control = new DropDownControl("#id_global_skin", "#id_global_skin_label", "Global Skin"),
        skin_control = new DropDownControl("#id_app_skin", "#id_app_skin_label", "App Skin");

    site_control.handler = function () {
        global_control.reset()
        skin_control.reset()

        $.getJSON("api/global_skins_for_site/" + site_control.name() + "/")
            .done(function (data) {
                global_control.add_li_from_data(data)
            })
            .fail(function () {
                console.log("ERROR in api call to global_skins_for_site.")
                arguments.forEach(
                    function (arg) {
                        console.log(arg)
                    })
            })

        $.getJSON("api/app_skins_for_site/" + site_control.name() + "/")
            .done(function (data) {
                skin_control.add_li_from_data(data)
            })
            .fail(function () {
                console.log("ERROR in api call to app_skins_for_site.")
                arguments.forEach(function (arg) {
                    console.log(arg)
                })
            })

    }

    global_control.handler = skin_control.handler = function () {
        add_files_to_tree()
    }

    /**
     * Populate the contents of the tree view if all three selections have
     * been made.
     */
    const add_files_to_tree = function () {
            if (!(site_control.picked && global_control.picked && skin_control.picked)) {
                return
            }
            /* split out application from skin name */
            let skin_name = skin_control.text().split("::");
            let app_name = skin_name[0];
            skin_name = skin_name[1];

            $.getJSON("/files/api/packages_for_site_with_skins/" + site_control.name() +
                    "/" + global_control.name() + "/" + app_name + "/" + skin_name + "/")
                .done(
                    function (data) {
                        let global_li = $(GLOBAL_LIST),
                            skin_li = $(SKIN_LIST),
                            block_li = $(BLOCK_LIST),
                            comp_li = $(COMP_LIST);
                        // console.log("api_packages_for_site_with_skins succeeded! Now do something with it.")
                        data.forEach(function (datum) {
                            // console.log(datum)
                            switch (datum.pkg_type) {
                            case 'b':
                                console.log('block ' + datum.name)
                                add_pkg_data_to_li(block_li, datum)
                                break
                            case 'g':
                                console.log('global ' + datum.name)
                                add_pkg_data_to_li(global_li, datum)
                                break
                            case 's':
                                console.log('skin ' + datum.name)
                                add_pkg_data_to_li(skin_li, datum)
                                break
                            case 'c':
                                console.log('comp ' + datum.name)
                                add_pkg_data_to_li(comp_li, datum)
                                break
                            default:
                                console.log("WARNING: Unexpected package type: '" + datum.pkg_typej + "'")
                            }
                        });
                    })
                .fail(
                    function () {
                        console.log("ERROR in api call to /files/packages_for_site_with_skins/.");
                        arguments.forEach(
                            function (arg) {
                                console.log(arg);
                            });
                    });
        } // add_files_to_tree()

    /**
     * Add a package to the tree view as a child of the given <li> element.
     *
     * @param {Object} The <li> element that is parent of new node
     * @param {Object} A package data object from the JSON return from API
     */
    const add_pkg_data_to_li = function (li_element, pkg) {
        $(TREE_VIEW).jstree().create_node(li_element, pkg.name)
    }

    //============= immediate code =====================================
    $(TREE_VIEW).jstree({
        core: {
            check_callback: true,
            error: function () {
                console.log("JSTree Error: ", arguments)
            },
            multiple: false,
            themes: {
                icons: false,
                responsive: true
            }

        }
        //possible: use 'data' to set up automatic ajax call to populate the node
    })

})
