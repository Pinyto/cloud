'use strict';

var pinytoWebApp = angular.module(
    'pinytoWeb',
    [
        'PinytoWebServices',
        'ngRoute',
        'localization'
    ]
).config(
    ['$routeProvider', '$locationProvider', function ($routeProvider, $locationProvider) {
        $routeProvider.
            when('/', {templateUrl: '/static/partials/welcome.html', controller: 'PinytoWelcomeCtrl'}).
            when('/login/', {templateUrl: '/static/partials/login.html', controller: 'PinytoLoginCtrl'}).
            otherwise({templateUrl: '/static/partials/welcome.html', controller: 'PinytoWelcomeCtrl'});
        // use the HTML5 History API
        $locationProvider.html5Mode(true).hashPrefix('!');
    }]
);

pinytoWebApp.run(function ($rootScope, $window, $document, localize) {
    // root scope functions
    $rootScope.getLanguages = function () {
        return ['en', 'de'];
    };
    $rootScope.setLanguage = function (lang) {
        $rootScope.language = lang;
        localize.setLanguage(lang);
    };
    // initialization
    if (!$rootScope.language) {
        $rootScope.setLanguage(
                $window.navigator.userLanguage ||
                $window.navigator.language ||
                $document.getElementsByTagName('html')[0].lang
        );
    }
});