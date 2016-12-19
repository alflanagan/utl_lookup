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
   $, macroName
*/

$(function () {
  'use strict'
  let siteName = ''
  const SITE_BTN = '#id_site_btn'
  const CERTIFIED_BOX = '#id_certified_check'
  const CUSTOM_BOX = '#id_custom_check'

  /** Disable site buttton to indicate it is not relevant */
  const disableSiteButton = function () {
    /* probably should set a class here, specify appearance in CSS */
    $(SITE_BTN).attr('disabled', 'disabled').css('color', 'lightgrey')
  }

  /** Ensure site button is enabled and default appearance */
  const enableSiteButton = function () {
    $(SITE_BTN).removeAttr('disabled').css('color', '')
  }

  /** Ensure a checkbox is checked */
  const checkBox = function (boxId) {
    let daBox = $(boxId)
    if (!daBox[0].checked) {
      daBox.trigger('click')
    }
  }

  /**
   * Change label on site button to currently selected site.
   */
  $('#id_site li').on('click', function (evt) {
    siteName = evt.currentTarget.innerText
    if (siteName === '[All Sites]') {
      siteName = ''
      $(SITE_BTN).html('Select a site<span class="caret"></span>')
    } else {
      $(SITE_BTN).html(siteName + '<span class="caret"></span>')
    }
  })

  /**
   * Enable/disable site button as custom checkbox is clicked, ensure
   * at least one checkbox is selected.
   */
  $(CUSTOM_BOX).on('click', function (evt) {
    if (evt.currentTarget.checked) {
      enableSiteButton()
    } else {
      disableSiteButton()
      checkBox(CERTIFIED_BOX)
    }
  }) // custom checkbox on "click"

  /**
   * If user deselects "certified" for search, enable "custom"
   * checkbox.
   */
  $(CERTIFIED_BOX).on('click', function (evt) {
    if (!evt.currentTarget.checked) {
      /* ensure one box is always checked */
      checkBox(CUSTOM_BOX)
    }
  })

  /**
   * Make asynch call to api_macro_defs(). Returns promise. If promise
   * is successful, it will provide an array of objects, each of which
   * is a definition spec.
   */
  const apiMacroDefsSearch = function (macroName, searchCertified, searchCustom, searchSite) {
    searchCertified = searchCertified === false ? 'false' : 'true'
    searchCustom = searchCustom === false ? 'false' : 'true'
    let apiURL = '/files/api/macro_defs_search/' + encodeURIComponent(macroName) + '/' + searchCertified + '/' + searchCustom + '/'
    if (searchSite) {
      apiURL += encodeURIComponent(searchSite) + '/'
    }
    console.log('URL is ' + apiURL)
    return $.ajax({url: apiURL, dataType: 'json'})
  } // apiMacroDefsSearch()

  /**
   * Make async call to api_macro_refs(). Returns promise. If promise
   * is successful, it will provide an array of objects, each of which
   * is a reference location.
   */
  const apiMacroRefsSearch = function (macroName) {
    let apiURL = '/files/api/macro_refs/' + encodeURIComponent(macroName) + '/'
    return $.ajax({url: apiURL, dataType: 'json'})
  } // apiMacroRefsSearch()

  /**
   * Given an object returned by /api/macro_refs/ call, constructs the
   * HTML for displaying that information on the page.
   */
  const buildMacroRefLine = function (macroRef) {
    let listItem = '<li><span class="pkg-name">'
    listItem += macroRef.pkg_name
    listItem += '</span>/<span class="pkg-file">'
    listItem += macroRef.file + ': ' + macroRef.line
    listItem += '</span></li>'
    return listItem
  }  // buildMacroRefLine()

  /**
   * Given a macro definition, return a function which populates the
   * text of that macro into the definition pane.
   */
  const buildMacroDefOnClick = function (macroDef) {
    // macroDef keys: id, file, start, line, text, name, pkg_name, pkg_version, pkg_site, pkg_download, pkg_certified
    return function (evt) {
      $.ajax({
        url: '/files/api/macro_w_syntax/' + macroDef.id + '/',
        dataType: 'json'
      }).done(function (data) {
        $('#macro-code-display pre').remove()
        $('#macro-code-display').append('<pre>' + data.text.replace('\t', '  ') + '</pre>')
      }).fail(function (err) {
        console.log('Call to /files/api/macro_w_syntax/ failed with error ' + err.status + ': ' + err.statusText)
      })
    }
  } // buildMacroDefOnClick()

  const buildMacroDefLine = function (macroDef) {
    let newButton = $('<button type="button" class="btn btn-default btn-sm btn-block">' +
                      macroDef.pkg_name + ' (' + macroDef.pkg_version + ')' +
                      '</button>')
    newButton.on('click', buildMacroDefOnClick(macroDef))
    return $('<li></li>').append(newButton)
  } // buildMacroDefLine()

  $('#id_macro_name_submit').on('click', function (evt) {
    const macroName = $('#id_macro_name_input')[0].value
    const searchCertified = $(CERTIFIED_BOX)[0].checked
    const searchCustom = $(CUSTOM_BOX)[0].checked

    $('#save-macro-name').value = macroName // save it for later
    apiMacroDefsSearch(macroName, searchCertified, searchCustom).done(
      function (data) {
        $('#macro_defn_ul').empty()
        data.forEach(function (macroRef) {
          $('#macro_defn_ul').append(buildMacroDefLine(macroRef))
        })
      }
    ).fail(
      function (err) {
        console.log('call to api/macro_defs failed with error ' + err.status + ': ' + err.statusText)
      }
    )

    apiMacroRefsSearch(macroName).done(
      function (data) {
        $('#macro-ref-list').empty()
        data.forEach(function (macroRef) {
          $('#macro-ref-list').append(buildMacroRefLine(macroRef))
        })
      }
    ).fail(
      function (err) {
        console.log('call to api/macro_refs/ failed with error ' + err.status + ': ' + err.statusText)
      }
    )

    evt.preventDefault()
  }) // #id_macro_name_submit click

  if (macroName !== null) {
    $('#id_macro_name_input')[0].value = macroName
    $('#id_macro_name_submit').trigger('click')
  }
})  // end module

// Local Variables:
// js-indent-level: 2
// js2-strict-missing-semi-warning: nil
// End:
