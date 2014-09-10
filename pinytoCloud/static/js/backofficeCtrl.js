'use strict';

pinytoWebApp.controller('PinytoBackofficeCtrl',
    function ($scope, $rootScope, Backend, Authenticate) {
    // Function Definitions
    $scope.loadStatistics = function () {
        Backend.statistics(Authenticate.getToken()).success(function (data) {
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
