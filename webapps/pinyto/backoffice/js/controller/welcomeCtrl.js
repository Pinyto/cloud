'use strict';

pinytoWebApp.controller('PinytoWelcomeCtrl',
    function ($scope, $rootScope, Backend, Authenticate) {
    // Function Definitions
    $scope.foo = function () {

    };

    // Initialization
    $scope.bar = true;
    $scope.lang = $rootScope.language;

    // Event handlers
    $scope.$on('langChange', function (event, newLang) {
        $scope.lang = newLang;
    });
});
