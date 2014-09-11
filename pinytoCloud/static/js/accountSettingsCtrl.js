'use strict';

pinytoWebApp.controller('PinytoAccountSettingsCtrl',
    function ($scope, $rootScope, Backend, Authenticate, $routeParams) {
    // Function Definitions
    $scope.changePassword = function () {
        if ($scope.password && $scope.password.length >= 6) {
            if ($scope.password == $scope.passwordRepeat) {
                $scope.requestState = 'pending';
                Backend.changePassword(Authenticate.getToken(), $scope.password).success(function (data) {
                    if (angular.fromJson(data)['success']) {
                        $scope.requestState = 'success';
                    } else {
                        $scope.requestState = 'failure';
                    }
                });
            } else {
                $scope.requestState = 'mismatch';
            }
        } else {
            $scope.requestState = 'tooshort';
        }
    };

    // Initialization
    $scope.lang = $rootScope.language;

    // Event handlers
    $scope.$on('langChange', function (event, newLang) {
        $scope.lang = newLang;
    });
});
