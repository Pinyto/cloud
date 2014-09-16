'use strict';

pinytoWebApp.controller(
    'PinytoAllAssembliesCtrl',
    function ($scope, $rootScope, Backend, Authenticate) {
        // Function Definitions
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

        // Initialization
        $scope.lang = $rootScope.language;
        $scope.getAssemblies();

        // Event handlers
        $scope.$on('langChange', function (event, newLang) {
            $scope.lang = newLang;
        });
    }
);
