'use strict';

pinytoWebApp.controller('PinytoLoginCtrl',
    function ($scope, $location, Backend, Authenticate) {
    // Function Definitions
    $scope.login = function () {
        Authenticate.login($scope.username, $scope.password).success(function (data) {
            var response = angular.fromJson(data);
            if ('token' in response) {
                console.log("Successfully authenticated.");
                $location.path('/');
            } else {
                console.log("Error while authenticating.");
                $scope.error = Authenticate.getLastError();
            }
        });
    };
    // Initialization
    document.getElementById('username').focus();
});
