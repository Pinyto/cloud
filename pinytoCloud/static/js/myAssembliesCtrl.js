'use strict';

pinytoWebApp.controller('PinytoMyAssembliesCtrl',
    function ($scope, $rootScope, Backend, Authenticate) {
        // Function Definitions
        $scope.getUserName = function () {
            return Authenticate.getUsername();
        };

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
                'api_functions': [],
                'jobs': []
            });
        };

        $scope.addApiFunction = function (assembly) {
            assembly['api_functions'].push({
                'name': "",
                'code': ""
            })
        };

        $scope.deleteApiFunction = function (assembly, index) {
            assembly['api_functions'].splice(index, 1);
        };

        $scope.addJob = function (assembly) {
            assembly['jobs'].push({
                'name': "",
                'code': "",
                'scheduleActivated': false,
                'schedule': 0
            })
        };

        $scope.deleteJob = function (assembly, index) {
            assembly['jobs'].splice(index, 1);
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
