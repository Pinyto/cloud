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

        $scope.assemblyChanged = function (index) {
            if ((index >= $scope.assembliesOnline.length) ||
                ($scope.assemblies[index]['name'] != $scope.assembliesOnline[index]['name']) ||
                ($scope.assemblies[index]['description'] != $scope.assembliesOnline[index]['description']) ||
                ($scope.assemblies[index]['api_functions'].length !=
                 $scope.assembliesOnline[index]['api_functions'].length)) {
                return true;
            }
            for (var i = 0; i < $scope.assemblies[index]['api_functions'].length; i++) {
                if (($scope.assemblies[index]['api_functions'][i]['name'] !=
                    $scope.assembliesOnline[index]['api_functions'][i]['name']) ||
                    ($scope.assemblies[index]['api_functions'][i]['code'] !=
                    $scope.assembliesOnline[index]['api_functions'][i]['code'])) {
                    return true;
                }
            }
            if ($scope.assemblies[index]['jobs'].length !=
                $scope.assembliesOnline[index]['jobs'].length) {
                return true;
            }
            for (i = 0; i < $scope.assemblies[index]['jobs'].length; i++) {
                if (($scope.assemblies[index]['jobs'][i]['name'] !=
                    $scope.assembliesOnline[index]['jobs'][i]['name']) ||
                    ($scope.assemblies[index]['jobs'][i]['code'] !=
                    $scope.assembliesOnline[index]['jobs'][i]['code']) ||
                    ($scope.assemblies[index]['jobs'][i]['schedule'] !=
                    $scope.assembliesOnline[index]['jobs'][i]['schedule'])) {
                    return true;
                }
            }
            return false;
        };

        $scope.assemblyHasAName = function (assembly) {
            return assembly['name'].length > 0;
        };

        $scope.apiFunctionHasAName = function (apiFunction) {
            return apiFunction['name'].length > 0;
        };

        $scope.assemblyApiFunctionsHaveDifferentNames = function (assembly) {
            for (var i = 0; i < assembly['api_functions'].length; i++) {
                if (!$scope.apiFunctionHasAName(assembly['api_functions'][i])) {
                    return false;
                }
                for (var j = i + 1; j < assembly['api_functions'].length; j++) {
                    if (assembly['api_functions'][i]['name'] == assembly['api_functions'][j]['name']) {
                        return false;
                    }
                }
            }
            return true;
        };

        $scope.jobHasAName = function (job) {
            return job['name'].length > 0;
        };

        $scope.assemblyJobsHaveDifferentNames = function (assembly) {
            for (var i = 0; i < assembly['jobs'].length; i++) {
                if (!$scope.jobHasAName(assembly['jobs'][i])) {
                    return false;
                }
                for (var j = i + 1; j < assembly['jobs'].length; j++) {
                    if (assembly['jobs'][i]['name'] == assembly['jobs'][j]['name']) {
                        return false;
                    }
                }
            }
            return true;
        };

        $scope.assemblyIsValid = function (assembly) {
            return ($scope.assemblyHasAName(assembly)) &&
                ($scope.assemblyApiFunctionsHaveDifferentNames(assembly)) &&
                ($scope.assemblyJobsHaveDifferentNames(assembly));
        };

        $scope.saveAssembly = function (assembly) {
            console.log(assembly);
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
