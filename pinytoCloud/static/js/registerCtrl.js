'use strict';

pinytoWebApp.controller('PinytoRegisterCtrl',
    function ($scope, $location, Backend) {
    // Function Definitions
    $scope.register = function () {
        if ($scope.password && ($scope.password.length >= 6)) {
            if ($scope.password == $scope.passwordRepeat) {
                Backend.register($scope.username, $scope.password).success(function (data) {
                    var response = angular.fromJson(data);
                    if (('success' in response) && (response['success'])) {
                        $scope.success = true;
                    } else {
                        $scope.error = response['error'];
                    }
                });
            } else {
                $scope.error = "The entered passwords did not match. Please correct this and try again."
            }
        } else {
            $scope.error = "Your password is too short. It must consist of at least 6 characters."
        }
    };
    // Initialization
    document.getElementById('username').focus();
});
