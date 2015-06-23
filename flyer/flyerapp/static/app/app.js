(function() {
 'use strict';
 angular.module('app',[
	'ngCookies',
     'ui.bootstrap',
     'angularjs-dropdown-multiselect'
 ], function($interpolateProvider){
	// Contorna prroblema de interpolação da renderização de template do django
	$interpolateProvider.startSymbol('{[{');
	$interpolateProvider.endSymbol('}]}');
 })
 .run( function run($http, $cookies ){
	// Evita problemas relacionados ao CSRF
	$http.defaults.headers.post['X-CSRFToken'] = $cookies['csrftoken'];
 });
})();