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

  $("#id_site li").on("click", function (evt) { console.log("site chosen: " + evt.currentTarget.innerText)})

  $("#id_custom_check").on("click", function(evt) { 
    console.log(evt.currentTarget.innerText)
  })

})

// Local Variables:
// js-indent-level: 2
// js2-strict-missing-semi-warning: nil
// End:
