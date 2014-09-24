'use strict';

pinytoWebApp.controller(
    'PinytoAccountSettingsCtrl',
    function ($scope, $rootScope, Backend, Authenticate) {
        // Function Definitions
        $scope.changePassword = function () {
            if ($scope.password && $scope.password.length >= 6) {
                if ($scope.password == $scope.passwordRepeat) {
                    $scope.requestState = 'pending';
                    Backend.changePassword(Authenticate.getToken(), $scope.password).success(function (data) {
                        if (angular.fromJson(data)['success']) {
                            $scope.requestState = 'success';
                        } else {
                            $scope.requestState = 'failure';
                        }
                    });
                } else {
                    $scope.requestState = 'mismatch';
                }
            } else {
                $scope.requestState = 'tooshort';
            }
        };

        $scope.getKeys = function () {
            Backend.listKeys(Authenticate.getToken()).success(function (data) {
                $scope.keys = angular.fromJson(data);
            });
        };

        $scope.setActive = function (key) {
            key.requestState = 'pending';
            Backend.setKeyActive(Authenticate.getToken(), key.key_hash, key.active).success(function (data) {
                if (angular.fromJson(data)['success']) {
                    key.requestState = 'success';
                } else {
                    key.requestState = 'failure';
                }
            });
        };

        $scope.isLastActiveKey = function (key) {
            var activeKeyCount = 0;
            if ($scope.keys) {
                for (var i = 0; i < $scope.keys.length; i++) {
                    if ($scope.keys[i].active) {
                        activeKeyCount++;
                    }
                }
            }
            return (activeKeyCount <= 1) && key.active;
        };

        $scope.deleteKey = function (key) {
            Backend.deleteKey(Authenticate.getToken(), key.key_hash).success(function (data) {
                if (angular.fromJson(data)['success']) {
                    $scope.getKeys();
                }
            });
        };

        // Initialization
        $scope.lang = $rootScope.language;
        $scope.keys = [];
        $scope.getKeys();
        $scope.username = Authenticate.getUsername();

        // Event handlers
        $scope.$on('langChange', function (event, newLang) {
            $scope.lang = newLang;
        });
    }
);
