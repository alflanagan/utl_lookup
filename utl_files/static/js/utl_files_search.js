/**
 * search -- module of functions for Townnews macro lookup page
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
  let site_name = "";
  const SITE_BTN="#id_site_btn",
        CERTIFIED_BOX="#id_certified_check",
        CERTIFIED_LBL="#id_certified_label",
        CUSTOM_LBL="#id_custom_label",
        CUSTOM_BOX="#id_custom_check"

  /** Disable site buttton to indicate it is not relevant */
  const disable_site_button = function() {
    /* probably should set a class here, specify appearance in CSS */
    $(SITE_BTN).attr("disabled", "disabled").css("color", "lightgrey")
  }

  /** Ensure site button is enabled and default appearance */
  const enable_site_button = function() {
    $(SITE_BTN).removeAttr("disabled").css("color", "")
  }

  /** Ensure a checkbox is checked */
  const check_box = function(box_id) {
    let da_box = $(box_id)
    if (!da_box[0].checked) {
      da_box.trigger("click")
    }
  }

  /**
   * Change label on site button to currently selected site.
   */
  $("#id_site li").on("click", function (evt) {
    site_name = evt.currentTarget.innerText
    if (site_name === "[All Sites]") {
      site_name = ""
      $(SITE_BTN).html('Select a site<span class="caret"></span>')
    } else {
      $(SITE_BTN).html(site_name + '<span class="caret"></span>')
    }
  })

  /**
   * Enable/disable site button as custom checkbox is clicked, ensure
   * at least one checkbox is selected.
   */
  $(CUSTOM_BOX).on("click", function(evt) {
    draw_something()
    if (evt.currentTarget.checked) {
      enable_site_button()
    } else {
      disable_site_button();
      check_box(CERTIFIED_BOX);
    }
  }) // custom checkbox on "click"

  /**
   * If user deselects "certified" for search, enable "custom"
   * checkbox.
   */
  $(CERTIFIED_BOX).on("click", function(evt) {
    draw_something()
    if (!evt.currentTarget.checked) {
      /* ensure one box is always checked */
      check_box(CUSTOM_BOX)
    }
  })

  /**
   * Make asynch call to api_macro_defs(). Returns promise. If promise
   * is successful, it will provide an array of objects, each of which
   * is a definition spec.
   */
  const api_macro_defs_search = function (macro_name, search_certified, search_custom, search_site) {
    search_certified = search_certified === false ? "false" : "true";
    search_custom = search_custom == false ? "false" : "true";
    let api_url = "/files/api/macro_defs_search/" + encodeURIComponent(macro_name) + "/" + search_certified + "/" + search_custom + "/"
    if (search_site) {
      api_url += encodeURIComponent(search_site) + "/"
    }
    console.log("URL is " + api_url)
    return $.ajax({url: api_url, dataType: "json"})
  } // api_macro_defs_search()

  /**
   * Make async call to api_macro_refs(). Returns promise. If promise
   * is successful, it will provide an array of objects, each of which
   * is a reference location.
   */
  const api_macro_refs_search = function (macro_name) {
    let api_url = "/files/api/macro_refs/" + encodeURIComponent(macro_name) + "/"
    return $.ajax({url: api_url, dataType: "json"})
  } // api_macro_refs_search()

  /**
   * Given an object returned by /api/macro_refs/ call, constructs the
   * HTML for displaying that information on the page.
   */
  const build_macro_ref_line = function (macro_ref) {
    let list_item = '<li><span class="pkg-name">Package: '
    list_item += macro_ref.pkg_name + " (" + macro_ref.pkg_version + ")"
    list_item += '</span>  <span class="pkg-file">File: '
    list_item += macro_ref.file + ", line " + macro_ref.line
    list_item += '</span></li>'
    return list_item
  }  // build_macro_ref_line()

  /**
   * Given a macro definition, return a function which populates the
   * text of that macro into the definition pane.
   */
  const build_macro_def_on_click = function (macro_def) {
    // macro_def keys: id, file, start, line, text, name, pkg_name, pkg_version, pkg_site, pkg_download, pkg_certified
    return function(evt) {
      $.ajax({
        url: "/files/api/macro_w_syntax/" + macro_def.id + "/",
        dataType: "json"
      }).done(function (data) {
        $("#macro-code-display pre").remove()
        $("#macro-code-display").append("<pre>" + data.text.replace("\t", "  ") + "</pre>")
      }).fail(function (err){
        console.log("Call to /files/api/macro_w_syntax/ failed with error " + err.status + ": " + err.statusText)
      })
    }
  } // build_macro_def_on_click()

  const build_macro_def_line = function (macro_def) {
    let new_button = $('<button type="button" class="btn btn-default btn-sm btn-block">'
                       + macro_def.pkg_name + " (" + macro_def.pkg_version + ")" 
                       + "</button>")
    new_button.on("click", build_macro_def_on_click(macro_def))
    return $("<li></li>").append(new_button)
  } // build_macro_def_line()

  $("#id_macro_name_submit").on("click", function(evt) {
    const macro_name = $("#id_macro_name_input")[0].value,
          search_certified = $(CERTIFIED_BOX)[0].checked,
          search_custom = $(CUSTOM_BOX)[0].checked

    $("#save-macro-name").value = macro_name // save it for later
    api_macro_defs_search(macro_name, search_certified, search_custom).done(
      function(data) {
        $("#macro_defn_ul").empty()
        data.forEach(function (macro_ref) {
          $("#macro_defn_ul").append(build_macro_def_line(macro_ref))

        })
      }
    ).fail(
      function(err) {
        console.log("call to api/macro_defs failed with error " + err.status + ": " + err.statusText)
      }
    )

    api_macro_refs_search(macro_name).done(
      function(data) {
        $("#macro-ref-list").empty()
        data.forEach(function (macro_ref) {
          $("#macro-ref-list").append(build_macro_ref_line(macro_ref))
        })
      }
    ).fail(
      function(err) {
        console.log("call to api/macro_refs/ failed with error " + err.status + ": " + err.statusText)
      }
    )

    evt.preventDefault()
  }) // #id_macro_name_submit click

  const draw_something = function () {
    // let canvas = $("#small-canvas canvas")[0]
    // if (canvas.getContext) {
    //   let context = canvas.getContext('2d')
    //   context.fillStyle = "rgb(255, 255, 255)"
    //   context.fillRect(0, 0, 100, 100)
    //   context.fillStyle = "rgb(200,0,0)"
    //   context.fillRect(10, 10, 50, 50)
    //   context.fillStyle = "rgba(0, 0, 200, 0.5)"
    //   context.fillRect(30, 30, 50, 50)
    //   context.clearRect(40, 40, 30, 30)
    //   context.strokeRect(42, 42, 26, 26)
    //   context.fillStyle = "rgba(0, 100, 100, 0.9)"
    //   context.beginPath()
    //   context.moveTo(55, 42)
    //   context.lineTo(90, 90)
    //   context.lineTo(10, 90)
    //   context.closePath()
    //   context.fill()
    // } else {
    //   // no canvas support. display an image?
    // }

  } // draw_something()

})  // end module

// Local Variables:
// js-indent-level: 2
// js2-strict-missing-semi-warning: nil
// End:
