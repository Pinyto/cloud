'use strict';

pinytoWebApp.controller('PinytoImpressumCtrl',
    function ($scope, $rootScope, Backend, Authenticate, $routeParams) {
    // Function Definitions


    // Initialization
    $scope.lang = $rootScope.language;

    // Event handlers
    $scope.$on('langChange', function (event, newLang) {
        console.log(newLang);
        $scope.lang = newLang;
    });
});
