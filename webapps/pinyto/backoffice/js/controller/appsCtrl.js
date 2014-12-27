'use strict';

pinytoWebApp.controller('PinytoAppsCtrl',
    function ($scope, $rootScope, Backend, Authenticate, $routeParams) {
    // Function Definitions


    // Initialization
    $scope.lang = $rootScope.language;

    // Event handlers
    $scope.$on('langChange', function (event, newLang) {
        $scope.lang = newLang;
    });
});
