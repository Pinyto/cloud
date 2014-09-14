'use strict';

pinytoWebApp.controller('PinytoMyAssembliesCtrl',
    function ($scope, $rootScope, Backend, Authenticate) {
        // Function Definitions
        $scope.getAssemblies = function () {
            Backend.listOwnAssemsblies(Authenticate.getToken()).success(function (data) {
                $scope.assemblies = angular.fromJson(data);
            });
        };

        // Initialization
        $scope.lang = $rootScope.language;
        $scope.assemblies = [];
        $scope.getAssemblies();

        // Event handlers
        $scope.$on('langChange', function (event, newLang) {
            $scope.lang = newLang;
        });
    }
);
