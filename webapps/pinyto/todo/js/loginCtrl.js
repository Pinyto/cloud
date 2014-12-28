'use strict';

todoApp.controller('loginCtrl',
    function ($scope, $location, Backend, Authenticate) {
    // Function Definitions
    $scope.login = function () {
        Authenticate.login($scope.username, $scope.password).success(function (data) {
            var response = angular.fromJson(data);
            if ('token' in response) {
                $location.path('/');
            } else {
                $scope.error = Authenticate.getLastError();
            }
        });
    };
    // Initialization
    document.getElementById('username').focus();
});
