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
  const TREE_VIEW = "#tree-view",
    FILES_TREE = "#files-tree",
    INNER_TEXT = "innerText";

  /**
   * @summary An object that represents a bootstrap dropdown control
   * on the page.
   *
   * @description A bootstrap control is made up of a &lt;div&gt;
   * containing a &lt;button&gt; and an &lt;ul&gt; list. This object
   * handles the initial appearance, click handling, and updating the
   * button text with the value of the selected item.
   *
   * @constructor
   * @global
   *
   * @param {string} ul_id The id attribute of the &lt;ul&gt; element used
   * for dropdown
   * @param {string} label_id The id attribute of the &lt;button&gt;
   * element acting as a label/trigger
   * @param {string} label_text The text to show on the control when
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
      console.log('Creating DropDownControl("' + ul_id + '", "' + label_id + "...")

      /**
       * @summary Event handler for click on list item.
       *
       * @description An event handler triggered when one of the
       * dropdown items is clicked. Sets label to text of selected
       * item, sets <var>picked</var> to <code>true</code>, then calls
       * user-supplied handler, if any.
       *
       * @param {Object} evt the Event object.
       *
       * @param {string} evt.target The list item that was clicked.
       */
      this.onclick = evt => {
        this.text(evt.target.textContent)
        this.picked = true
        this.handler(this)
      }

      // ensure existing list items have click handler
      $(ul_id + " li").on("click", this.onclick)

      /**
       * Get or set the label text.
       *
       * @param {string} arg Set the label text for this control to
       * the value of <var>arg</var> (plus a caret decoration). If
       * <var>arg</var> is <code>undefined</code>, the text is
       * unchanged (but still returned).
       *
       * @return {string} The text of the currently selected item
       */
      this.text = arg => {
        if (arg === undefined) {
          return $(this.label_id).prop("innerText")
        } else {
          this.label_text = arg
          $(this.label_id).html(this.label_text + "<span class=\"caret\"></span>")
          return arg
        }
      }

      /**
       * Disable the control
       */
      this.disable = () => {
        $(this.label_id).attr("disabled", "")
      }

      /**
       * Enable the control
       */
      this.enable = () => {
        $(this.label_id).removeAttr("disabled")
      }

      /**
       * @summary Fills dropdown with string values
       *
       * @description Clears the current list, then creates a list
       * item for each element in <var>data</var>. Clicking the
       * element will trigger this object's <code>onclick()</code>
       * handler. If there are no items in <var>data</var>, disables
       * the control. If there is exactly 1 item in <var>data</var>,
       * automatically selects it (triggering click event).
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
              this.disable()
              break;
            case 1:
              this.disable()
                // automatically select for user
              $(this.ul_id).children("li").click()
              break;
            default:
              this.enable()
          }
        } //add_li_from_data

      /**
       * Resets dropdown to empty, disabled state
       *
       * @param {string} new_label If present, text displayed on
       * button is changed to this value
       */
      this.reset = (new_label) => {
        $(this.ul_id + " li").detach()
        if (new_label !== undefined) {
          this.label_text = new_label
        }
        this.text(this.label_text)
        this.disable()
        this.picked = false
      }

      /**
       * @summary Fill the drop-down with results of an API call.
       *
       * IMPORTANT: caller should reset control first
       *
       * @param {string} api_name The API name (the fixed part of the
       * URL that follows 'api/')
       *
       * @param {string} site_name The name of the site selected
       *
       */
      this.fill_from_api = (api_name, site_name) => {
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
   * @description An object to manage the list of files in a tab on
   * the right-hand side of the screen.
   *
   * @constructor
   * @global
   * 
   * @param {string} root_id The ID of the HTML element that acts as
   * the root of the created tree
   *
   * @returns {FilesView} The new object
   */
  const FilesView = function (fileview_id) {
    this.view_id = fileview_id

    console.log('Creating FilesView("' + fileview_id + '")')
    $(this.view_id).jstree({
      error: function () {
        console.log("$('" + this.view_id + "').jstree() Error: ", arguments)
      },
      themes: {
        icons: true,
        responsive: true
      }
    })
    this.jst = $(this.view_id).jstree()
    this.root_id = this.jst.create_node(null, "/")
    this.root_node = this.jst.get_node(this.root_id, true)

    /**
     * @summary Add a file to the tree.
     *
     * @param {string} utlfile The name of the file to be added.
     *
     */
    this.add_a_file = utlfile => {
      this.jst.create_node(this.root_node, utlfile.path)
    } // add_a_file()

    return this
  }

  /**
   * @summary A node in the Tree View listing packages.
   *
   * @description An object that represents a node in the Tree
   * View. Depending on the selections made in the search area, a node
   * may have children which are the names of packages.
   *
   * @constructor
   * @global
   *
   * @param {string} list_id the ID of the HTML element that acts as a
   * root node
   *
   * @param {DropDownControl} site_control the dropdown used to select
   * a Townnews site
   *
   * @param {DropDownControl} skin_control the dropdown used to select
   * an application skin
   *
   * @param {FilesView} files_view The file listing display object
   *
   */
  const TreeViewPackageList = function (list_id, site_control, skin_control) {
      this.list_id = list_id
      this.site_control = site_control
      this.skin_control = skin_control
      this.jst = $(TREE_VIEW).jstree()

      /**
       * @description Reset tree control by deleting child nodes.
       */
      this.reset = () => {
          let del_kid = (an_id) => this.jst.delete_node(an_id);
          while (this.jst.get_node(this.list_id).children.length > 0) {
            this.jst.get_node(this.list_id).children.forEach(del_kid)
          }
        } // reset()

      /**
       * @summary Add a package to the tree view.
       *
       * @param {Object} A package data object from the JSON return
       * from API
       */
      this.add_pkg = (pkg) => {
        this.jst.create_node(this.list_id, pkg_to_string(pkg))
      }
    } // TreeViewPackageList

  /**
   * @summary Convert package spec to a display name.
   *
   * @global
   *
   * @description Given a package spec JSON object, returns a string
   * which contains the same information, suitable for display but
   * easily converted back to the JSON representation. (see {@link
   * string_to_pkg})
   *
   * @param {Object} pkg Package specification (from python
   * <code>Package.to_dict()</code>)
   *
   * @returns {string} String with format
   * "<var>application</var>::<var>package</var>[*]", where the
   * presence of "*" indicates the package is certified
   *
   */
  const pkg_to_string = function (pkg) {
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
   * @summary Convert a string with a package description to a
   * (partial) package specification
   *
   * @global
   *
   * @param {string} pkg_str The package string in format created by
   * <code>{@link pkg_to_string}()</code>.
   *
   * @returns {Object} Object with keys "app", "name", "is_certified"
   *
   */
  const string_to_pkg = function (pkg_str) {
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
   * @summary Controls the four package list objects in the main tree
   * view.
   *
   * @constructor
   * @global
   */
  const TreeView = function () {
      const GLOBAL_LIST = "#pkgs_global_list",
        SKIN_LIST = "#pkgs_skin_list",
        BLOCK_LIST = "#pkgs_blocks_list",
        COMP_LIST = "#pkgs_components_list";

      console.log("creating TreeView())")
      this.site_control = new DropDownControl("#id_site", "#id_site_label", "Site")
      this.global_control = new DropDownControl("#id_global_skin", "#id_global_skin_label", "Global Skin")
      this.skin_control = new DropDownControl("#id_app_skin", "#id_app_skin_label", "App Skin")
      this.files_view = new FilesView("#files-tree-root")

      this.global_node = new TreeViewPackageList(GLOBAL_LIST, this.site_control, this.skin_control)
      this.skin_node = new TreeViewPackageList(SKIN_LIST, this.site_control, this.skin_control)
      this.block_node = new TreeViewPackageList(BLOCK_LIST, this.site_control, this.skin_control)
      this.comp_node = new TreeViewPackageList(COMP_LIST, this.site_control, this.skin_control)

      /**
       * @summary Handler for selection of a node item.
       *
       * @description Makes an AJAX call to the <span
       * class="file-path">package_files</span> API to retrieve a list
       * of the files associated with the selected package. Adds each
       * file name to <var>this.filesView</var>.
       *
       * @param {Object} node JSTree object (not used)
       *
       * @param {Object} selected The selection object
       *
       * @param {Object} selected.node DOM node for the selected item.
       *
       * @param {Object} selected.event A "click" event object.
       *
       * @param {Object} selected.instance I think this is the JSTree
       *     object (like result of <code>$(TREEVIEW).jstree()</code>)
       *
       * @param {Object} selected.selected An array of strings, the
       *     IDs of the selected nodes.
       */
      this.onselect_node = (node, selected) => {
          const API_PATH = "/files/api/package_files/"
          let pkg = string_to_pkg(selected.event.target.textContent),
            api_call = "",
            full_name = pkg.name

          if (pkg.app !== "global") {
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
                data.forEach(datum => {
                  this.files_view.add_a_file(datum)
                })
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
       * @summary Fill the secondary controls whenever a site is
       * selected.
       *
       * @private
       *
       * @description Gets site from site control, calls
       * <code>api/global_skins_for_site</code> to fill the global
       * skin control, then <code>api/app_skins_for_site</code> to
       * fill the skin control.
       *
       */
      this.site_control.handler = () => {
          if (this.site_control.text() !== "certified") {
            this.global_control.reset("Global Skin")
            this.global_control.fill_from_api("global_skins_for_site", this.site_control.text())
            this.skin_control.reset("App Skin")
            this.skin_control.fill_from_api("app_skins_for_site", this.site_control.text())
            this.reset_nodes()
          } else {
            this.global_control.reset("N/A")
            this.skin_control.reset("N/A")
            this.make_api_call("certified", "ignored", "ignored", "ignored")
          }
        } // site_control.handler()

      /**
       * @summary Get packages based on search controls
       *
       * @description Calls the API <span
       * class="file-path">/files/api/packages_for_site_with_skins/</span>
       * to get the list of packages consistent with the search
       * controls, then fills the tree nodes from the results
       *
       * @param {string} site_name The site domain name ("richmond.com", "omaha.com", etc.)
       *
       * @param {string} global_skin The selected global skin for the site.
       *
       * @param {string} app_name The name of the applicaton for the selected skin.
       *
       * @param {string} skin_name The name of the selected skin.
       *
       */
      this.make_api_call = (site_name, global_skin, app_name, skin_name) => {
          $.getJSON("/files/api/packages_for_site_with_skins/" + site_name +
              "/" + global_skin + "/" + app_name + "/" + skin_name + "/")
            .done(
              data => {
                this.reset_nodes()

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

      /**
       * @summary Reset search nodes back to original state.
       */
      this.reset_nodes = () => {
        this.global_node.reset()
        this.skin_node.reset()
        this.block_node.reset()
        this.comp_node.reset()
      }

      /**
       * @summary Populate the contents of the tree view.
       *
       * @description Does nothing unless all three selections have
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
       * @summary Fill the Tree View when search form is completed.
       *
       * @private
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

  // technically, so far, we don't have to have TreeView as a constructor
  const the_tree = new TreeView()
})

// Local Variables:
// js-indent-level: 2
// js2-strict-missing-semi-warning: nil
// End:
