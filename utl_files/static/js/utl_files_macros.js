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
  const utl_files = window.utl_files

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


  //============= immediate code =====================================
  const site_control = new utl_files.DropDownControl("#id_site", "#id_site_label", "Site"),
    global_control = new utl_files.DropDownControl("#id_global_skin", "#id_global_skin_label", "Global Skin"),
    skin_control = new utl_files.DropDownControl("#id_app_skin", "#id_app_skin_label", "App Skin"),
    select_form = new utl_files.SelectSiteSkinsForm(site_control, global_control, skin_control)

  function htmlEncode(value) {
    return $('<div/>').text(value).html();
  }

  $("#search-bar").on("allPicked", (evt) => {
    //console.log("search-bar event")
    utl_files.get_macros_for(site_control.text(), global_control.text(), skin_control.text(),
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
              // let api_call = "/files/api/macro_def_text/" + item_value.toString() + "/"
              let api_call = "/files/api/macro_w_syntax/" + item_value.toString() + "/"
              $.getJSON(api_call)
                .done(
                  data => {
                    // TODO: pre-wrap style mostly works, but wrapping sucks. Define our own formatter?
                    let pcode = '<p><span class="macro-detail-label">Name:</span> ' + data.name + '</p>'

                    $("#macro-name").html(pcode)
                    pcode = '<p><span class="macro-detail-label">Package:</span> ' + data.package + '</p>'
                    $("#macro-package-name").html(pcode)
                    pcode = '<p><span class="macro-detail-label">File:</span> ' + data.source + '</p>'
                    $("#macro-file-name").html(pcode)
                    let lines = data.text.split("\n")
                    $("#defs-text span").detach()
                    $("#defs-text br").detach()
                    lines = lines.join("<br>")
                    $("#defs-text").html(lines)
                    // lines.forEach((line) => {
                    //   // second arg of htmlEncode == true ==> &amp; gets converted to &amp;amp;
                    //   // will get converted back by browser
                    //   //$("#defs-text").append("<span>" + Encoder.htmlEncode(line, false) + "</span><br>")
                    //   $("#defs-text").append(line);
                    // })
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
