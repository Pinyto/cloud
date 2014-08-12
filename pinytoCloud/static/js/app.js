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
            when('/development/', {templateUrl: '/static/partials/development.html', controller: 'PinytoDevelopmentCtrl'}).
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
    $rootScope.$watch('language', function (newLang) {
        localize.setLanguage(newLang);
        $rootScope.$broadcast('langChange', newLang);
    });
    // initialization
    if (!$rootScope.language) {
        $rootScope.language = $window.navigator.userLanguage ||
                              $window.navigator.language ||
                              $document.getElementsByTagName('html')[0].lang;
    }
});