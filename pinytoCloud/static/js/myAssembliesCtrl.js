'use strict';

pinytoWebApp.controller('PinytoMyAssembliesCtrl',
    function ($scope, $rootScope, Backend, Authenticate) {
        // Function Definitions
        $scope.getAssemblies = function () {
            Backend.listOwnAssemsblies(Authenticate.getToken()).success(function (data) {
                $scope.assembliesOnline = angular.fromJson(data);
                $scope.assemblies = angular.copy($scope.assembliesOnline);
            });
        };

        $scope.addAssembly = function () {
            $scope.assemblies.push({
                'name': "",
                'description': "",
                'api_-functions': [],
                'jobs': []
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
