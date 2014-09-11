'use strict';

pinytoWebApp.controller('PinytoBackofficeCtrl',
    function ($scope, $rootScope, $interval, Backend, Authenticate) {
    // Function Definitions
    $scope.loadStatistics = function () {
        Backend.statistics(Authenticate.getToken()).success(function (data) {
            $scope.statistics = angular.fromJson(data);
            $scope.statistics['calculated_storage_budget'] = $scope.statistics['storage_budget'] +
                (Date.now() - parseInt($scope.statistics['last_calculation'])) / 1000.0 *
                    parseInt($scope.statistics['current_storage']);
        });
    };

    // Initialization
    $scope.lang = $rootScope.language;
    $scope.loadStatistics();

    $interval(function () {
        if ($scope.statistics) {
            $scope.statistics['calculated_storage_budget'] = $scope.statistics['storage_budget'] +
                (Date.now() - parseInt($scope.statistics['last_calculation'])) / 1000.0 *
                    parseInt($scope.statistics['current_storage']);
        }
    }, 1000);

    // Event handlers
    $scope.$on('langChange', function (event, newLang) {
        $scope.lang = newLang;
    });
});
