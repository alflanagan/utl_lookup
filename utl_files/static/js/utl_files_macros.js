/**
 * macros -- module of functions for Townnews macro reference page
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
   $, Encoder 
*/

$(function () {
  "use strict";

  // ID selector strings, use constant to avoid mistyping
  const DEFS_PNL = "#defs-panel",
    REFS_PNL = "#refs-panel";

  const on_tab_click = (evt) => {
    $(DEFS_PNL).hide()
    $("#defs-tab").removeClass("active")
    $(REFS_PNL).hide()
    $("#refs-tab").removeClass("active")
    let the_id = evt.target.id
    if (!the_id.endsWith("-tab")) {
      the_id = evt.target.parentNode.id
    }
    switch (the_id) {
      case "defs-tab":
        $(DEFS_PNL).show()
        $("#defs-tab").addClass("active")
        break
      case "refs-tab":
        $(REFS_PNL).show()
        $("#refs-tab").addClass("active")
    }
  }
  $("#defs-tab").on("click", on_tab_click)
  $("#refs-tab").on("click", on_tab_click)

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
        // console.log('Creating DropDownControl("' + ul_id + '", "' + label_id + "...")

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
          $(this.ul_id + " li").detach()
            // don't prevent user from filling tree if no options or
            // just one
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
              console.error("ERROR in api call to " + api_name + "/" + site_name + ".")
              for (let i = 0; i < arguments.length; i++) {
                console.log(arguments[i])
              }
            })
        } // fill_from_api()

      return this;

    } // DropDownControl

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
   * @description Universal handling and reporting of jstree errors.
   *
   * @protected
   *
   * @param {Object} info Information about the error
   * @param {Object} info.data Extra data about the error
   * @param {string} info.error A code identifying the type of error?
   * @param {string} info.id The id of the element generating the error
   * @param {string} info.plugin The plugin where the error occurred.
   * @param {string} info.reason Human-readable error description.
   */
  const handle_jstree_error = function (info) {
    console.error("ERROR signaled by jstree: error '" + info.error + "' occurred in element #" +
      info.id + " (plugin " + info.plugin + " ): " + info.reason)
    console.log("Extra data associated with the above error:")
    let parsed = JSON.parse(info.data)
    for (let key of parsed) {
      console.log("    " + key + ": " + parsed[key])
    }
  };

  const SelectSiteSkinsForm = function (site_control, global_control, skin_control) {
      this.site_control = site_control
      this.global_control = global_control
      this.skin_control = skin_control
      this.all_picked_event = document.createEvent('Event')
      this.all_picked_event.initEvent('allPicked', true, true)

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
          } else {
            this.global_control.reset("N/A")
            this.skin_control.reset("N/A")
          }
        } // site_control.handler()

      this.skin_control.handler = this.global_control.handler = (evt) => {
        if (this.skin_control.picked && this.global_control.picked) {
          let search_bar = $("#search-bar").get()[0]
          search_bar.dispatchEvent(this.all_picked_event)
        }
      }

    } // SelectSiteSkinsForm

  this.get_macros_for = (domainname, global_skin, app_skin, handler) => {
      let parts = app_skin.split("::"),
        app_name, skin_name

      if (parts.length === 2) {
        app_name = parts[0],
          skin_name = parts[1]
      } else {
        console.error("Name of app skin must be in form app::skin. Got '" + app_skin + "' instead.")
        return
      }

      let api_call = "/files/api/macros_for_site_with_skins/" + domainname +
        "/" + global_skin + "/" + app_name + "/" + skin_name + "/"

      $.getJSON(api_call)
        .done(
          data => {
            handler(data)
          })
        .fail(
          () => {
            console.error("FAIL of API call " + api_call);
            console.log("error arguments")
            for (let i = 0; i < arguments.length; i++) {
              console.log(arguments[i])
            }
          })
    } // get_macros_for()

  //============= immediate code =====================================
  const site_control = new DropDownControl("#id_site", "#id_site_label", "Site"),
    global_control = new DropDownControl("#id_global_skin", "#id_global_skin_label", "Global Skin"),
    skin_control = new DropDownControl("#id_app_skin", "#id_app_skin_label", "App Skin"),
    select_form = new SelectSiteSkinsForm(site_control, global_control, skin_control)

  function htmlEncode(value) {
    return $('<div/>').text(value).html();
  }

  $("#search-bar").on("allPicked", (evt) => {
    //console.log("search-bar event")
    this.get_macros_for(site_control.text(), global_control.text(), skin_control.text(),
      (data) => {
        this.macro_list = data // save for later

        $("ul#macros-list li").detach()
        data.forEach((datum) => {
          // console.log("macro " + datum.name + " from " + datum.pkg + ":" + datum.pkg_version + " ('" + datum.file + "')")
          // need a better way here for user to detect when there are 2 versions of the same macro
          $("ul#macros-list").append('<li class="list-item" data-value="' + datum.id + '"><a href="#">' + datum.name + '</a></li>')
        })

        $("#macros-list .list-item a").on("click", (evt) => {
          let item_value = Number(evt.target.parentNode.dataset.value)

          this.macro_list.forEach((macro_obj) => {
            if (macro_obj.id === item_value) {
              console.log(macro_obj)
              let api_call = "/files/api/macro_def_text/" + item_value.toString() + "/"
              $.getJSON(api_call)
                .done(
                  data => {
                    let lines = data.text.split("\n")
                    $("#defs-text span").detach()
                    $("#defs-text br").detach()
                    lines.forEach((line) => {
                      // second arg of htmlEncode == true ==> &amp; gets converted to &amp;amp;
                      // will get converted back by browser
                      $("#defs-text").append("<span>" + Encoder.htmlEncode(line, true) + "</span><br>")
                    })
                  })
                .fail(
                  (jqXHR, textStatus, errorThrown) => {
                    console.error("FAIL of API call " + api_call);
                    console.error("status is " + textStatus + ": " + errorThrown)
                  })

            }
          })
        })
      }

    )
  })
})

// Local Variables:
// js-indent-level: 2
// js2-strict-missing-semi-warning: nil
// End:
