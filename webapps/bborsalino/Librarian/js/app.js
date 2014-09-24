'use strict';

var bibApp = angular.module(
        'Bib',
        [
            'BibServices',
            'ngRoute',
            'localization'
        ]
    )
    .config(['$routeProvider', '$locationProvider', function ($routeProvider, $locationProvider) {
        $routeProvider.
            when('/webapps/bborsalino/Librarian/', {
                templateUrl: '/webapps/bborsalino/Librarian/partials/cards.html',
                controller: 'bibCtrl'}).
            when('/webapps/bborsalino/Librarian/login/', {
                templateUrl: '/webapps/bborsalino/Librarian/partials/login.html',
                controller: 'loginCtrl'}).
            otherwise({
                templateUrl: '/webapps/bborsalino/Librarian/partials/cards.html',
                controller: 'bibCtrl'});
        // use the HTML5 History API
		$locationProvider.html5Mode(true).hashPrefix('!');
    }]);