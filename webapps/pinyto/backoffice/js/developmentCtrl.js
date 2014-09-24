'use strict';

pinytoWebApp.controller('PinytoDevelopmentCtrl',
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
