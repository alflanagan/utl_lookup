/**
 * utl_files -- module of functions for utl_files lookup page
 *
 * @copyright 2016 BH Media Group, Inc.
 * @author A. Lloyd Flanagan
 *
 */

/* jshint
      asi: true,
      bitwise: true,
      browser: true,
      curly: true,
      devel: true,
      eqeqeq: true,
      esversion: 6,
      forin: true,
      freeze: true,
      jquery: true,
      futurehostile: true,
      latedef: true,
      noarg: true,
      nocomma: true,
      nonew: true,
      strict: true,
      undef: true,
      unused: true,
      varstmt: true
*/
/* global
   $ */

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
      this.onclick = evt => {
        const new_text = evt.target.textContent
        $(this.label_id).prop(INNER_TEXT, new_text)
        this.picked = true
        this.handler(this)
      }

      // ensure existing list items have click handler
      $(ul_id + " li").on("click", this.onclick)

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
          // if only 0 or 1 option, allow tree fill
          this.picked = (data.length < 2)
          data.forEach(
            datum => {
              const new_elem = $('<li>' + datum + '</li>')
              new_elem.on("click", this.onclick)
              $(this.ul_id).append(new_elem)
            })
          switch (data.length) {
            case 0:
              $(this.label_id).attr("disabled", "")
              break;
            case 1:
              $(this.label_id).attr("disabled", "")
                // automatically select for user
              $(this.ul_id).children("li").click()
              break;
            default:
              $(this.label_id).removeAttr("disabled")
          }
        } //add_li_from_data

      /**
       * Resets dropdown to empty, disabled state
       */
      this.reset = () => {
        $(this.ul_id + " li").detach()
        $(this.label_id).html(this.label_text + "<span class=\"caret\">")
        $(this.label_id).attr("disabled", "true")
        this.picked = false
      }

      /**
       * Call an API function, and fill the drop-down from the
       * results.
       *
       * @param {String} api_name The API name (the fixed part of the
       * URL that follows 'api/')
       *
       * @param {String} site_name The name of the site selected
       *
       */
      this.fill_from_api = (api_name, site_name) => {
          this.reset()
          $.getJSON("api/" + api_name + "/" + site_name + "/")
            .done(data => {
              // console.log(data)
              this.add_li_from_data(data)
            })
            .fail(() => {
              console.log("ERROR in api call to " + api_name + "/" + site_name + ".")
              arguments.forEach(
                function (arg) {
                  console.log(arg)
                })
            })
        } // fill_from_api()

      return this;

    } // DropDownControl

  /**
   * An object that represents a node in the Tree View. Depending on
   * the selections made in the search area, a node may have
   * children which are the names of packages.
   *
   * @param {String} list_id the ID of the HTML element that acts as a
   * root node
   *
   * @param {DropDownControl} site_control the dropdown used to select
   * a Townnews site
   *
   * @param {DropDownControl} skin_control the dropdown used to select
   * an application skin
   *
   */
  const TreeViewPackageList = function (list_id, site_control, skin_control) {
      this.list_id = list_id
      this.site_control = site_control
      this.skin_control = skin_control
      this.jst = $(TREE_VIEW).jstree()

      /**
       * Reset tree control by deleting child nodes.
       */
      this.reset = () => {
          let del_kid = (an_id) => this.jst.delete_node(an_id);
          while (this.jst.get_node(this.list_id).children.length > 0) {
            this.jst.get_node(this.list_id).children.forEach(del_kid)
          }
        } // reset()

      /**
       * Handler for selection of a node item.
       *
       * WTH does this get called four times?
       *
       * @param {Object} node
       * @param {Object} selected
       */
      this.onselect_node = (node, selected) => {
          // object keys:
          //
          // node: timeStamp, isTrigger, namespace, rnamespace,
          //       result, target, delegateTarget,
          //       currentTarget, handleObj, data
          //
          // selected: node, selected, event, instance
          //
          // selected.event: originalEvent, type,
          //                 isDefaultPrevented, timeStamp,
          //                 toElement, screenY, screenX, pageY,
          //                 pageX, offsetY, offsetX, clientY,
          //                 clientX, buttons, button, which,
          //                 view, target, shiftKey,
          //                 relatedTarget, metaKey, eventPhase,
          //                 detail, currentTarget, ctrlKey,
          //                 cancelable, bubbles, altKey,
          //                 delegateTarget, handleObj, data
          //
          // selected.selected: the Array the API promised as second
          // argument
          const API_PATH = "/files/api/package_files/"
          let pkg = this.string_to_pkg(selected.event.target.textContent),
            api_call = "",
            full_name = pkg.name

          if (pkg.app) {
            full_name = pkg.app + "::" + pkg.name
          }

          if (pkg.is_certified === "y") {
            // certified
            api_call = API_PATH + "certified/" + full_name + "/"
          } else {
            api_call = API_PATH + this.site_control.text() + "/" + full_name + "/"
          }
          $.getJSON(api_call)
            .done(
              data => {
                console.log("got " + data.length + " results from " + api_call)
              })
            .fail(
              () => {
                console.log("ERROR in api call to " + API_PATH + ".");
                for (let i = 0; i < arguments.length; i++) {
                  console.log(arguments[i])
                }
              })

        } // this.onselect_node()

      $(TREE_VIEW).on("select_node.jstree", this.onselect_node)

      /**
       * Convert package spec to a display name
       *
       * @param {Object} pkg Package specification (from python
       * <code>Package.to_dict()</code>)
       *
       * @returns {String} with format "application::package[*]",
       * where the presence of "*" indicates the package is certified
       *
       */
      this.pkg_to_string = (pkg) => {
          let full_name = "";
          if (pkg.app !== "global") {
            full_name = pkg.app + "::"
          }
          full_name += pkg.name
          if (pkg.is_certified === "y") {
            full_name += "*"
          }
          return full_name
        } // pkg_to_string()

      /**
       * Convert a string with a package description to a (partial)
       * package specification
       *
       * @param {String} pkg_str The package string in format created by
       * pkg_to_string().
       *
       * @returns {Object} with keys "app", "name", "is_certified"
       */
      this.string_to_pkg = (pkg_str) => {
          let the_app = "global",
            the_pkg = pkg_str,
            is_certified = "n";
          if (pkg_str.includes('::')) {
            let parts = pkg_str.split('::')
            the_app = parts[0]
            the_pkg = parts[1]
          }
          if (the_pkg.endsWith('*')) {
            is_certified = "y";
            the_pkg = the_pkg.substring(0, the_pkg.length - 1)
          }
          return {
            "app": the_app,
            "name": the_pkg,
            "is_certified": is_certified
          }
        } // string_to_pkg()

      /**
       * Add a package to the tree view.
       *
       * @param {Object} A package data object from the JSON return from API
       */
      this.add_pkg = (pkg) => {
        this.jst.create_node(this.list_id, this.pkg_to_string(pkg))
      }
    } // TreeViewPackageList

  const TreeView = function () {
      this.site_control = new DropDownControl("#id_site", "#id_site_label", "Site"),
        this.global_control = new DropDownControl("#id_global_skin", "#id_global_skin_label", "Global Skin"),
        this.skin_control = new DropDownControl("#id_app_skin", "#id_app_skin_label", "App Skin")

      this.global_node = new TreeViewPackageList(GLOBAL_LIST, this.site_control, this.skin_control),
        this.skin_node = new TreeViewPackageList(SKIN_LIST, this.site_control, this.skin_control),
        this.block_node = new TreeViewPackageList(BLOCK_LIST, this.site_control, this.skin_control),
        this.comp_node = new TreeViewPackageList(COMP_LIST, this.site_control, this.skin_control)

      /**
       * Fill the secondary controls whenever a site is selected.
       */
      this.site_control.handler = () => {
          this.global_control.fill_from_api("global_skins_for_site", this.site_control.text())
          this.skin_control.fill_from_api("app_skins_for_site", this.site_control.text())
        } // site_control.handler()

      /**
       * Calls the API /files/api/packages_for_site_with_skins/ to get
       * the list of packages consistent with the search controls, then
       * fills the tree nodes from the results
       *
       * @param {String} site_name The site domain name ("richmond.com", "omaha.com", etc.)
       *
       * @param {String} global_skin The selected global skin for the site.
       *
       * @param {String} app_name The name of the applicaton for the selected skin.
       *
       * @param {String} skin_name The name of the selected skin.
       *
       * @returns undefined
       */
      this.make_api_call = (site_name, global_skin, app_name, skin_name) => {
          $.getJSON("/files/api/packages_for_site_with_skins/" + site_name +
              "/" + global_skin + "/" + app_name + "/" + skin_name + "/")
            .done(
              data => {
                data.forEach(datum => {
                  switch (datum.pkg_type) {
                    case 'b':
                      // console.log('block ' + datum.name)
                      this.block_node.add_pkg(datum)
                      break
                    case 'g':
                      // console.log('global ' + datum.name)
                      this.global_node.add_pkg(datum)
                      break
                    case 's':
                      // console.log('skin ' + datum.name)
                      //TODO: add node for application under "Skin", add package node under that
                      this.skin_node.add_pkg(datum)
                      break
                    case 'c':
                      this.comp_node.add_pkg(datum)
                      break
                    default:
                      console.log("WARNING: Unexpected package type: '" + datum.pkg_typej + "'")
                  }
                })
              })
            .fail(
              function () {
                console.log("ERROR in api call to /files/packages_for_site_with_skins/.");
                arguments.forEach(
                  function (arg) {
                    console.log(arg);
                  })
              })
        } // make_api_call()

      this.reset_nodes = () => {
        this.global_node.reset()
        this.skin_node.reset()
        this.block_node.reset()
        this.comp_node.reset()
      }

      /**
       * Populate the contents of the tree view if all three selections have
       * been made.
       */
      this.add_pkgs_to_tree = () => {
          if (!(this.site_control.picked && this.global_control.picked && this.skin_control.picked)) {
            this.reset_nodes()
          } else {
            /* split out application from skin name */
            let skin_name = this.skin_control.text().split("::"),
              app_name = skin_name[0];
            skin_name = skin_name[1];
            this.make_api_call(this.site_control.text(), this.global_control.text(), app_name, skin_name);
          }
        } // add_pkgs_to_tree()

      /**
       * Fill the Tree View when search form is completed.
       */
      this.global_control.handler = this.skin_control.handler = () => {
        this.add_pkgs_to_tree()
      }

    } // this.TreeView

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

  let the_tree = new TreeView()

})

// Local Variables:
// js-indent-level: 2
// js2-strict-missing-semi-warning: nil
// End:
