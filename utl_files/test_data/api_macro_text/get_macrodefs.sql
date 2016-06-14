SELECT macrodef.*
  FROM papers_townnewssite tns
       INNER JOIN utl_files_package pkg ON tns.id = pkg.site_id
       INNER JOIN utl_files_utlfile file ON pkg.id = file.pkg_id
       INNER JOIN utl_files_macrodefinition macrodef ON file.id = macrodef.source_id
 WHERE tns."URL" = 'http://kearneyhub.com'
   AND pkg.name = 'base-kh-oct-2013-1-ads'
