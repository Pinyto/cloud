'use strict';

pinytoWebApp.controller(
    'PinytoAllAssembliesCtrl',
    function ($scope, $rootScope, Backend, Authenticate) {
        // Function Definitions
        $scope.getUserName = function () {
            return Authenticate.getUsername();
        };

        $scope.getAssemblies = function () {
            var calculateAvailableAssemblies = function () {
                $scope.availableAssemblies = angular.copy($scope.allAssemblies);
                for (var i = 0; i < $scope.installedAssemblies.length; i++) {
                    for (var j = 0; j < $scope.availableAssemblies.length; j++) {
                        if ($scope.availableAssemblies[j]['name'] == $scope.installedAssemblies[i]['name']) {
                            $scope.availableAssemblies.splice(j, 1);
                            break;
                        }
                    }
                }
            };
            Backend.listInstalledAssemsblies(Authenticate.getToken()).success(function (data) {
                $scope.installedAssemblies = angular.fromJson(data);
                if ($scope.allAssemblies) {
                    calculateAvailableAssemblies();
                }
            });
            Backend.listAllAssemsblies(Authenticate.getToken()).success(function (data) {
                $scope.allAssemblies = angular.fromJson(data);
                if ($scope.installedAssemblies) {
                    calculateAvailableAssemblies();
                }
            });
        };

        $scope.installAssembly = function (assembly) {
            assembly.installState = 'pending';
            Backend.installAssembly(
                Authenticate.getToken(),
                assembly.author,
                assembly.name
            ).success(function (data) {
                if (angular.fromJson(data)['success']) {
                    assembly.installState = 'success';
                    if ($scope.installedAssemblies) {
                        $scope.installedAssemblies.push({
                            'name': assembly['name'],
                            'author': assembly['author'],
                            'description': assembly['description'],
                            'api_functions': assembly['api_functions'],
                            'jobs': assembly['jobs'],
                            'sourceCodeLoadState': assembly['sourceCodeLoadState'],
                            'showSource': (assembly['description'] && assembly['api_functions']) ? false : undefined
                        })
                    }
                    if ($scope.availableAssemblies) {
                        for (var i = 0; i < $scope.availableAssemblies.length; i++) {
                            if ($scope.availableAssemblies[i]['name'] == assembly['name']) {
                                $scope.availableAssemblies.splice(i, 1);
                                break;
                            }
                        }
                    }
                } else {
                    assembly.installState = 'error';
                }
            });
        };

        $scope.uninstallAssembly = function (assembly) {
            assembly.uninstallState = 'pending';
            Backend.uninstallAssembly(
                Authenticate.getToken(),
                assembly.author,
                assembly.name
            ).success(function (data) {
                if (angular.fromJson(data)['success']) {
                    assembly.uninstallState = 'success';
                    if ($scope.availableAssemblies) {
                        $scope.availableAssemblies.push({
                            'name': assembly['name'],
                            'author': assembly['author'],
                            'description': assembly['description'],
                            'api_functions': assembly['api_functions'],
                            'jobs': assembly['jobs'],
                            'sourceCodeLoadState': assembly['sourceCodeLoadState'],
                            'showSource': (assembly['description'] && assembly['api_functions']) ? false : undefined
                        })
                    }
                    if ($scope.installedAssemblies) {
                        for (var i = 0; i < $scope.installedAssemblies.length; i++) {
                            if ($scope.installedAssemblies[i]['name'] == assembly['name']) {
                                $scope.installedAssemblies.splice(i, 1);
                                break;
                            }
                        }
                    }
                } else {
                    assembly.uninstallState = 'error';
                }
            });
        };

        $scope.getAssemblySource = function (assembly) {
            assembly.sourceCodeLoadState = 'pending';
            Backend.getAssemblySource(
                Authenticate.getToken(),
                assembly.author,
                assembly.name
            ).success(function (data) {
                var codeData = angular.fromJson(data);
                if (codeData['api_functions'] && codeData['jobs']) {
                    assembly['api_functions'] = codeData['api_functions'];
                    assembly['jobs'] = codeData['jobs'];
                    assembly.sourceCodeLoadState = 'loaded';
                    assembly.showSource = true;
                } else {
                    assembly.sourceCodeLoadState = 'error';
                }
            });
        };

        // Initialization
        $scope.lang = $rootScope.language;
        $scope.getAssemblies();

        // Event handlers
        $scope.$on('langChange', function (event, newLang) {
            $scope.lang = newLang;
        });
    }
);
