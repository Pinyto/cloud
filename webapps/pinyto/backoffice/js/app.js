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
            when('/', {
                templateUrl: '/webapps/pinyto/backoffice/partials/welcome.html',
                controller: 'PinytoWelcomeCtrl'}).
            when('/login/', {
                templateUrl: '/webapps/pinyto/backoffice/partials/login.html',
                controller: 'PinytoLoginCtrl'}).
            when('/register/', {
                templateUrl: '/webapps/pinyto/backoffice/partials/register.html',
                controller: 'PinytoRegisterCtrl'}).
            when('/backoffice/', {
                templateUrl: '/webapps/pinyto/backoffice/partials/backoffice.html',
                controller: 'PinytoBackofficeCtrl'}).
            when('/backoffice/assemblies/', {
                templateUrl: '/webapps/pinyto/backoffice/partials/all_assemblies.html',
                controller: 'PinytoAllAssembliesCtrl'}).
            when('/backoffice/assemblies/mine/', {
                templateUrl: '/webapps/pinyto/backoffice/partials/my_assemblies.html',
                controller: 'PinytoMyAssembliesCtrl'}).
            when('/backoffice/data/', {
                templateUrl: '/webapps/pinyto/backoffice/partials/view_data.html',
                controller: 'PinytoViewDataCtrl'}).
            when('/backoffice/account/settings/', {
                templateUrl: '/webapps/pinyto/backoffice/partials/account_settings.html',
                controller: 'PinytoAccountSettingsCtrl'}).
            when('/explanation/', {
                templateUrl: '/webapps/pinyto/backoffice/partials/explanation.html',
                controller: 'PinytoExplanationCtrl'}).
            when('/hardware/', {
                templateUrl: '/webapps/pinyto/backoffice/partials/hardware.html',
                controller: 'PinytoHardwareCtrl'}).
            when('/development/', {
                templateUrl: '/webapps/pinyto/backoffice/partials/development.html',
                controller: 'PinytoDevelopmentCtrl'}).
            when('/impressum/', {
                templateUrl: '/webapps/pinyto/backoffice/partials/impressum.html',
                controller: 'PinytoImpressumCtrl'}).
            otherwise({
                templateUrl: '/webapps/pinyto/backoffice/partials/welcome.html',
                controller: 'PinytoWelcomeCtrl'});
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

pinytoWebApp.run(function ($http, $templateCache) {
    // Template prefetching
    var prefetchingTemplates = [
        '/webapps/pinyto/backoffice/partials/login.html',
        '/webapps/pinyto/backoffice/partials/backoffice_tabs.html'
    ];
    angular.forEach(prefetchingTemplates, function (templateUrl) {
        console.log("prefetching: "+templateUrl);
        $http.get(templateUrl).success(function (templateData) {
            console.log(templateUrl+" fetched.");
            $templateCache.put(templateUrl, templateData);
        });
    });
});