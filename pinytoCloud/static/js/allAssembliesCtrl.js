'use strict';

pinytoWebApp.controller('PinytoAllAssembliesCtrl',
    function ($scope, $rootScope, Backend, Authenticate) {
    // Function Definitions


    // Initialization
    $scope.lang = $rootScope.language;

    // Event handlers
    $scope.$on('langChange', function (event, newLang) {
        $scope.lang = newLang;
    });
});
