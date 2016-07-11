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
   $, utl_files
 */

$(function () {
  "use strict";

  if (window.utl_files === undefined) {
    throw Error("Attempted to use utl_files_files module without loading util_files module.")
  }

  let utl_files = window.utl_files

  // ID selector strings, use constant to avoid mistyping
  const TREE_VIEW = "#tree-view",
    FILES_TREE = "#files-tree",
    INNER_TEXT = "innerText",
    FILES_PNL = "#files-panel",
    DEFS_PNL = "#defs-panel",
    REFS_PNL = "#refs-panel";

  /* @global */
  const on_tab_click = (evt) => {
    $(DEFS_PNL).hide()
    $("#defs-tab").removeClass("active")
    $(REFS_PNL).hide()
    $("#refs-tab").removeClass("active")
    $(FILES_PNL).hide()
    $("#files-tab").removeClass("active")
    let the_id = evt.target.id
    if (!the_id.endsWith("-tab")) {
      the_id = evt.target.parentNode.id
    }
    switch (the_id) {
      case "files-tab":
        $(FILES_PNL).show()
        $("#files-tab").addClass("active")
        break
      case "defs-tab":
        $(DEFS_PNL).show()
        $("#defs-tab").addClass("active")
        break
      case "refs-tab":
        $(REFS_PNL).show()
        $("#refs-tab").addClass("active")
    }
  }
  $("#files-tab").on("click", on_tab_click)
  $("#defs-tab").on("click", on_tab_click)
  $("#refs-tab").on("click", on_tab_click)


  /**
   * @description An object to manage the list of files in a tab on
   * the right-hand side of the screen.
   *
   * @constructor
   * @global
   * 
   * @param {string} fileview_id The ID of the HTML element that acts as
   * the root of the created tree
   *
   * @param {FileDisplay} file_display The ID of the HTML element
   * providing a display for showing file contents.
   *
   * @returns {FilesView} The new object
   */
  const FilesView = function (fileview_id, file_display) {
    this.view_id = fileview_id
    this.display = new FileDisplay(file_display)

    console.log('Creating FilesView("' + fileview_id + '")')
    $(this.view_id).jstree({
      core: {
        check_callback: true,
        multiple: false,
        error: utl_files.handle_jstree_error,
        themes: {
          icons: true,
          responsive: true
        }
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
        let parts = utlfile.path.split("/"),
          current_data = this.jst.get_node(this.root_id)

        /* for each part of the filename, check for an existing node. If
         * one does not exist, create it.
         */
        for (let i = 0; i < parts.length; i++) {
          let found_it = false
          current_data.children.forEach(child_id => {
            let child_data = this.jst.get_node(child_id)
            if (child_data.text === parts[i]) {
              current_data = child_data
              found_it = true
            }
          })
          if (found_it === false) {
            let new_node;
            if ( i === parts.length - 1) {
              new_node =this.jst.create_node(current_data.id,
                                             { "text": parts[i], "file_id": utlfile.id })
            } else {
              new_node = this.jst.create_node(current_data.id,
                                              { "text": parts[i] })
            }
            current_data = this.jst.get_node(new_node)
          }
        } // for
      } // add_a_file()

    /**
     * @description Remove all child nodes
     */
    this.reset = () => {
      this.jst.delete_node(this.root_node)
      this.root_id = this.jst.create_node(null, "/")
      this.root_node = this.jst.get_node(this.root_id, true)
    }

    /**
     * @summary Handler for selection of a file tree node item.
     *
     * @description 
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
      // here we get ID from selected node, tell the file display to
      // display contents of that file.
      // console.log("File name is " + selected.node.original["text"])
      // console.log("File ID is " + selected.node.original["file_id"])
      if (selected.node.original["file_id"]) {
        this.display.load_file(selected.node.original["file_id"])
      } else {
        this.display.clear_source();
      }
    }

    $(this.view_id).on("select_node.jstree", this.onselect_node)

    return this
  } // FilesView()

  /**
   * A node in the Tree View listing packages.
   *
   * An object that represents a node in the Tree View. Depending on
   * the selections made in the search area, a node may have children
   * which are the names of packages.
   *
   * @constructor
   * @global
   *
   * @param {string} list_id the ID of the HTML element that acts as a
   * root node
   *
   * @param {utl_files.DropDownControl} site_control the dropdown used
   * to select a Townnews site
   *
   * @param {utl_files.DropDownControl} skin_control the dropdown used
   * to select an application skin
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
        this.jst.create_node(this.list_id, utl_files.pkg_to_string(pkg))
      }
    } // TreeViewPackageList


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
      const site_control_handler = () => {
          let domain = this.site_control.text()
          if (domain !== "certified") {
            this.global_control.reset("Global Skin")
            this.global_control.fill_from_api("global_skins_for_site", domain)
            this.skin_control.reset("App Skin")
            this.skin_control.fill_from_api("app_skins_for_site", domain)
            this.reset_nodes()
          } else {
            this.global_control.reset("N/A")
            this.skin_control.reset("N/A")
            this.make_api_call("certified", "ignored", "ignored", "ignored")
          }
        } // site_control_handler()

      /**
       * @summary Populate the contents of the tree view.
       *
       * @description Does nothing unless all three selections have
       * been made.
       */
      const add_pkgs_to_tree = () => {
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

      this.site_control = new utl_files.DropDownControl("#id_site", "#id_site_label", "Site", site_control_handler)
      this.global_control = new utl_files.DropDownControl("#id_global_skin", "#id_global_skin_label", "Global Skin", add_pkgs_to_tree)
      this.skin_control = new utl_files.DropDownControl("#id_app_skin", "#id_app_skin_label", "App Skin", add_pkgs_to_tree)
      this.files_view = new FilesView("#files-tree-root", "#source-display")

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
          let pkg = utl_files.string_to_pkg(selected.event.target.textContent),
            api_call = "",
            full_name = pkg.name

          this.files_view.reset()

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

    } // this.TreeView

  /**
   * @summary Manages the display of source code from a file.
   *
   * @constructor
   * @global
   */
  const FileDisplay = function () {
    
    this.load_file = (file_id) => {
      console.log("Calling " + "/files/api/file_text_w_syntax/" + file_id + "/")
      $.getJSON("/files/api/file_text_w_syntax/" + file_id + "/")
        .done(
          data => {
            let lines = data.text.split("\n")
            this.clear_source()
            lines = lines.join("<br>")
            $("#source-display").html("<div></div>")
            $("#source-display div").html(lines)
          })
        .fail(
          function (jqhxr, level, message) {
            console.log("ERROR in api call to /files/file_text_w_syntax/.")
            console.log(level + ": " + message)
          })

    } // this.load_file()

    this.clear_source = () => {
      $("#source-display div").detach()
    }

  } // FileDisplay
  //============= immediate code =====================================
  $(TREE_VIEW).jstree({
    core: {
      check_callback: true,
      error: utl_files.handle_jstree_error,
      multiple: false,
      themes: {
        icons: false,
        responsive: true
      }

    }
    //possible: use 'data' to set up automatic ajax call to populate the node
  })

  // TODO: replace TreeView as constructor with literal object --
  // never need more than one.
  const the_tree = new TreeView()
})

// Local Variables:
// js-indent-level: 2
// js2-strict-missing-semi-warning: nil
// End:
