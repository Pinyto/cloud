'use strict';

pinytoWebApp.controller('PinytoAccountSettingsCtrl',
    function ($scope, $rootScope, Backend, Authenticate, $routeParams) {
    // Function Definitions
    $scope.changePassword = function () {
        if ($scope.password == $scope.passwodRepeat) {
            $scope.requestState = 'pending';
            Backend.changePassword($scope.password).success(function (data) {
                if (angular.fromJson(data)['success']) {
                    $scope.requestState = 'success';
                } else {
                    $scope.requestState = 'failure';
                }
            });
        } else {
            $scope.requestState = 'mismatch';
        }
    };

    // Initialization
    $scope.lang = $rootScope.language;

    // Event handlers
    $scope.$on('langChange', function (event, newLang) {
        $scope.lang = newLang;
    });
});
