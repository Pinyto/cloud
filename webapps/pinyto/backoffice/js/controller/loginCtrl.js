'use strict';

pinytoWebApp.controller('PinytoLoginCtrl',
    function ($scope, $location, Backend, Authenticate) {
    // Function Definitions
    $scope.login = function () {
        $scope.submitting = true;
        Authenticate.login($scope.username, $scope.password).success(function (data) {
            var response = angular.fromJson(data);
            $scope.submitting = undefined;
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
