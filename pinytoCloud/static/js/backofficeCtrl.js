'use strict';

pinytoWebApp.controller('PinytoBackofficeCtrl',
    function ($scope, $rootScope, Backend, Authenticate, $routeParams) {
    // Function Definitions
    $scope.loadStatistics = function () {
        console.log(Authenticate.getToken());
        Backend.statistics(Authenticate.getToken()).success(function (data) {
            console.log(data);
            $scope.statistics = angular.fromJson(data);
        });
    };

    // Initialization
    $scope.lang = $rootScope.language;
    $scope.loadStatistics();

    // Event handlers
    $scope.$on('langChange', function (event, newLang) {
        $scope.lang = newLang;
    });
});
