'use strict';

var todoApp = angular.module(
        'Todo',
        [
            'TodoServices',
            'ngRoute',
            'localization'
        ]
    )
    .config(['$routeProvider', '$locationProvider', function ($routeProvider, $locationProvider) {
        $routeProvider.
            when('/webapps/pinyto/todo/', {
                templateUrl: '/webapps/pinyto/todo/partials/list.html',
                controller: 'todoCtrl'}).
            when('/webapps/pinyto/todo/login/', {
                templateUrl: '/webapps/pinyto/todo/partials/login.html',
                controller: 'loginCtrl'}).
            otherwise({
                templateUrl: '/webapps/pinyto/todo/partials/list.html',
                controller: 'todoCtrl'});
        // use the HTML5 History API
		$locationProvider.html5Mode(true).hashPrefix('!');
    }]);