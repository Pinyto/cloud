'use strict';

pinytoWebApp.controller('PinytoLoginCtrl',
    function ($scope, $location, Backend, Authenticate) {
    // Function Definitions
    $scope.login = function () {
        Authenticate.login($scope.username, $scope.password).success(function (data) {
            var response = angular.fromJson(data);
            if ('token' in response) {
                $location.path('/backoffice/');
            } else {
                $scope.error = Authenticate.getLastError();
            }
        });
    };
    // Initialization
    document.getElementById('username').focus();
});
