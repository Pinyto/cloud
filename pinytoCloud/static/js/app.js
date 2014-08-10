'use strict';

var pinytoWebApp = angular.module(
        'pinytoWeb',
        [
            'PinytoWebServices',
            'ngRoute',
            'localization'
        ]
    )
    .config(['$routeProvider', '$locationProvider', function ($routeProvider, $locationProvider) {
        $routeProvider.
            when('/', {templateUrl: '/static/partials/welcome.html', controller: 'welcomeCtrl'}).
            when('/login/', {templateUrl: '/static/partials/login.html', controller: 'loginCtrl'}).
            otherwise({templateUrl: '/static/partials/welcome.html', controller: 'welcomeCtrl'});
        // use the HTML5 History API
		$locationProvider.html5Mode(true).hashPrefix('!');
    }]);