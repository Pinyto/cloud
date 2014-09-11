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
            when('/register/', {templateUrl: '/static/partials/register.html', controller: 'PinytoRegisterCtrl'}).
            when('/backoffice/', {templateUrl: '/static/partials/backoffice.html', controller: 'PinytoBackofficeCtrl'}).
            when('/backoffice/assemblies/', {templateUrl: '/static/partials/all_assemblies.html', controller: 'PinytoAllAssembliesCtrl'}).
            when('/backoffice/assemblies/mine/', {templateUrl: '/static/partials/my_assemblies.html', controller: 'PinytoMyAssembliesCtrl'}).
            when('/backoffice/data/', {templateUrl: '/static/partials/view_data.html', controller: 'PinytoViewDataCtrl'}).
            when('/backoffice/account/settings/', {templateUrl: '/static/partials/account_settings.html', controller: 'PinytoAccountSettingsCtrl'}).
            when('/explanation/', {templateUrl: '/static/partials/explanation.html', controller: 'PinytoExplanationCtrl'}).
            when('/hardware/', {templateUrl: '/static/partials/hardware.html', controller: 'PinytoHardwareCtrl'}).
            when('/development/', {templateUrl: '/static/partials/development.html', controller: 'PinytoDevelopmentCtrl'}).
            when('/impressum/', {templateUrl: '/static/partials/impressum.html', controller: 'PinytoImpressumCtrl'}).
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
        if ($rootScope.language && ($rootScope.language.length > 2)) {
            $rootScope.language = $rootScope.language.substr(0, 2);
        }
    }
});