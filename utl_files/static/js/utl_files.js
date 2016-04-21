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
          /* split out application from skin name */
          const API_PATH = "/files/api/package_files/",
            pkg_name = this.skin_control.text();
          let api_call = API_PATH + this.site_control.text() + "/";

          if (pkg_name.includes("::")) {
            let split_name = pkg_name.split("::"),
              app_name = split_name[0],
              skin_name = split_name[1];
            api_call += app_name + "/" + skin_name + "/"
          } else {
            api_call += pkg_name + "/"
          }

          $.getJSON(api_call)
            .done(
              function (data) {
                data.forEach(function (datum) {
                  console.log(datum)
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

        } // this.onselect_node()
      this.jst.on("select_node.jstree", this.onselect_node)

      /**
       * Add a package to the tree view.
       *
       * @param {Object} A package data object from the JSON return from API
       */
      this.add_pkg = (pkg) => {
        this.jst.create_node(this.list_id, pkg.name)
      }
    } // TreeViewPackageList

  let site_control = new DropDownControl("#id_site", "#id_site_label", "Site"),
    global_control = new DropDownControl("#id_global_skin", "#id_global_skin_label", "Global Skin"),
    skin_control = new DropDownControl("#id_app_skin", "#id_app_skin_label", "App Skin");

  let global_node = new TreeViewPackageList(GLOBAL_LIST, site_control, skin_control),
    skin_node = new TreeViewPackageList(SKIN_LIST, site_control, skin_control),
    block_node = new TreeViewPackageList(BLOCK_LIST, site_control, skin_control),
    comp_node = new TreeViewPackageList(COMP_LIST, site_control, skin_control);

  /**
   * Fill the secondary controls whenever a site is selected.
   */
  site_control.handler = function () {
      global_control.fill_from_api("global_skins_for_site", site_control.text())
      skin_control.fill_from_api("app_skins_for_site", site_control.text())
    } // site_control.handler()

  /**
   * Populate the contents of the tree view if all three selections have
   * been made.
   */
  const add_files_to_tree = function () {

      if (!(site_control.picked && global_control.picked && skin_control.picked)) {
        global_node.reset()
        skin_node.reset()
        block_node.reset()
        comp_node.reset()

        return
      }
      /* split out application from skin name */
      let skin_name = skin_control.text().split("::");
      let app_name = skin_name[0];
      skin_name = skin_name[1];

      $.getJSON("/files/api/packages_for_site_with_skins/" + site_control.text() +
          "/" + global_control.text() + "/" + app_name + "/" + skin_name + "/")
        .done(
          function (data) {
            data.forEach(function (datum) {
              switch (datum.pkg_type) {
                case 'b':
                  // console.log('block ' + datum.name)
                  block_node.add_pkg(datum)
                  break
                case 'g':
                  // console.log('global ' + datum.name)
                  global_node.add_pkg(datum)
                  break
                case 's':
                  // console.log('skin ' + datum.name)
                  skin_node.add_pkg(datum)
                  break
                case 'c':
                  comp_node.add_pkg(datum)
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
   * Fill the Tree View when search form is completed.
   */
  global_control.handler = skin_control.handler = function () {
    add_files_to_tree()
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
