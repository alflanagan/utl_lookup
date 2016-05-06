/**
 * common -- functions used for multiple pages in utl_files app
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
   $
 */

$(function () {
  "use strict";

  /**
   * @const A namespace for the common utl_files objects
   */
  window.utl_files = {

      tab_ids: [],
      panel_ids: [],

      /**
       * On click of a tab, make the tab active and show its panel, while hiding others.
       *
       * Note the assumptions made about <var>tab_ids</var> and
       * <var>panel_ids</var>; they must be the same length, with the ID
       * of the panel for a tab at the same index as the tab ID.
       *
       * @param {Event} evt
       */
      on_tab_click: evt => {
        for (let i = 0; i < this.tab_ids.length; i++) {
          if (this.tab_ids[i] === evt.target.id || this.tab_ids[i] === evt.tartget.parentNode.id) {
            $(this.panel_ids[i]).show()
            $(this.tab_ids[i]).addClass("active")
          } else {
            $(this.panel_ids[i]).hide()
            $(this.tab_ids[i]).removeClass("active")
          }
        } // for
      }, // on_tab_click()

      set_tab_ids: (tab_ids, panel_ids) => {
        this.tab_ids = tab_ids
        this.panel_ids = panel_ids

        for (let tab_id of this.tab_ids) {
          $(tab_id).on("click", this.on_tab_click)
        }
      }, //set_tab_ids()

      /**
       * @classdesc An object that represents a bootstrap dropdown control
       * on the page.
       *
       * A bootstrap control is made up of a &lt;div&gt; containing a
       * &lt;button&gt; and an &lt;ul&gt; list. This object handles the
       * initial appearance, click handling, and updating the button text
       * with the value of the selected item.
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
      DropDownControl: function (ul_id, label_id, label_text, select_handler) {
        if (this === this.utl_files) {
          throw new Error("DropDownControl must called with new keyword")
        }
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
         * element will trigger this DropDownControl's
         * <code>onclick()</code> handler.
         *
         * If there are no items in <var>data</var>, disables the
         * control.
         *
         * If there is exactly 1 item in <var>data</var>,
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
        this.reset = new_label => {
          $(this.ul_id + " li").detach()
          if (new_label !== undefined) {
            this.label_text = new_label
          }
          this.text(this.label_text)
          this.disable()
          this.picked = false
        }

        /**
         * Fill the drop-down with results of an API call.
         *
         * IMPORTANT: caller should reset control first
         *
         * @param {string} api_name The name of the API, such that the
         * first part of the URL is <code>"api/" + api_name</code>
         *
         * @param {...} url_args The data passed to the API, will be
         * appended to the end separated by "/"
         *
         */
        this.fill_from_api = (api_name, ...url_args) => {
            let api_call = "api/" + api_name + "/" + url_args.join("/")

            $.getJSON(api_call)
              .done(
                data => {
                  this.add_li_from_data(data)
                })
              .fail(
                (jqXHR, textStatus, errorThrown) => {
                  console.error("ERROR in api call to " + api_call)
                  if (textStatus === "error") {
                    //don't report textStatus, it's useless
                    console.log("Error is: " + errorThrown)
                  } else {
                    console.log("status is " + textStatus + ", error is " + errorThrown)
                  }
                })
          } // fill_from_api()

      }, // DropDownControl

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
      pkg_to_string: function (pkg) {
        let full_name = "";
        if (pkg.app !== "global") {
          full_name = pkg.app + "::"
        }
        full_name += pkg.name
        if (pkg.is_certified === "y") {
          full_name += "*"
        }
        return full_name
      }, // pkg_to_string()

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
      string_to_pkg: function (pkg_str) {
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
      }, // string_to_pkg()

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
      handle_jstree_error: function (info) {
        console.error("ERROR signaled by jstree: error '" + info.error + "' occurred in element #" +
          info.id + " (plugin " + info.plugin + " ): " + info.reason)
        console.log("Extra data associated with the above error:")
        let parsed = JSON.parse(info.data)
        for (let key of parsed) {
          console.log("    " + key + ": " + parsed[key])
        }
      },

      SelectSiteSkinsForm: function (site_control, global_control, skin_control) {
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

      }, // SelectSiteSkinsForm

      get_macros_for: function (domainname, global_skin, app_skin, handler) {
          let parts = app_skin.split("::"),
            app_name, skin_name

          if (parts.length === 2) {
            app_name = parts[0],
              skin_name = parts[1]
          } else {
            throw new Error("Name of app skin must be in form app::skin. Got '" + app_skin + "' instead.")
          }

          let api_call = "/files/api/macros_for_site_with_skins/" + domainname +
            "/" + global_skin + "/" + app_name + "/" + skin_name + "/"

          $.getJSON(api_call)
            .done(
              data => {
                handler(data)
              })
            .fail(
              (jqXHR, textStatus, errorThrown) => {
                if (textStatus === "error") {
                  //don't report textStatus, it's useless
                  console.log("Error is: " + errorThrown)
                } else {
                  console.log("status is " + textStatus + ", error is " + errorThrown)
                }
              })
        } // get_macros_for()

    } // namespace utl_files
})

// Local Variables:
// js-indent-level: 2
// js2-strict-missing-semi-warning: nil
// js2-additional-externs: (quote ("$"))
// End:
