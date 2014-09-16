'use strict';

var pinytoCloud = 'https://cloud.pinyto.de/';
var pinytoKeyserver = 'https://keyserver.pinyto.de/';

angular.module('PinytoWebServices', [])
    .config(['$httpProvider', function($httpProvider) {
        $httpProvider.defaults.useXDomain = true;
        delete $httpProvider.defaults.headers.common['X-Requested-With'];
    }])
    .factory('Backend', function ($http) {
        function fillArray(array, attributes) {
            return function (data) {
                for (var i = 0; i < attributes.length; ++i) {
                    data = data[attributes[i]];
                }
                array.length = 0;
                angular.forEach(data, function (item) {
                    array.push(item);
                });
            }
        }

        return {
            login: function (username, password) {
                return $http({
                    url: '/keyserver/authenticate',
                    method: "POST",
                    data: 'name='+username+'&password='+password,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            },
            logout: function (token) {
                return $http({
                    url: '/keyserver/logout',
                    method: "POST",
                    data: 'token=' + token,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            },
            register: function (username, password) {
                return $http({
                    url: '/keyserver/register',
                    method: "POST",
                    data: 'name='+username+'&password='+password,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            },
            statistics: function (token) {
                return $http({
                    method: "POST",
                    url: '/statistics',
                    data: 'token=' + token,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            },
            changePassword: function (token, password) {
                return $http({
                    method: "POST",
                    url: '/keyserver/change_password',
                    data: 'token=' + token + '&password=' + password,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            },
            listKeys: function (token) {
                return $http({
                    method: "POST",
                    url: '/list_keys',
                    data: 'token=' + token,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            },
            setKeyActive: function (token, keyHash, activeState) {
                return $http({
                    method: "POST",
                    url: '/set_key_active',
                    data: 'token=' + token + '&key_hash=' + keyHash + '&active_state=' + activeState,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            },
            deleteKey: function (token, keyHash) {
                return $http({
                    method: "POST",
                    url: '/delete_key',
                    data: 'token=' + token + '&key_hash=' + keyHash,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            },
            listOwnAssemsblies: function (token) {
                return $http({
                    method: "POST",
                    url: '/list_own_assemblies',
                    data: 'token=' + token,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            },
            saveAssembly: function (token, originalName, assemblyJson) {
                return $http({
                    method: "POST",
                    url: '/save_assembly',
                    data: 'token=' + token + '&original_name=' + originalName + '&data=' + assemblyJson,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            },
            deleteAssembly: function (token, name) {
                return $http({
                    method: "POST",
                    url: '/delete_assembly',
                    data: 'token=' + token + '&name=' + name,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            },
            listInstalledAssemsblies: function (token) {
                return $http({
                    method: "POST",
                    url: '/list_installed_assemblies',
                    data: 'token=' + token,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            },
            listAllAssemsblies: function (token) {
                return $http({
                    method: "POST",
                    url: '/list_all_assemblies',
                    data: 'token=' + token,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            },
            installAssembly: function (token, author, name) {
                return $http({
                    method: "POST",
                    url: '/install_assembly',
                    data: 'token=' + token + '&author=' + author + '&name=' + name,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            },
            uninstallAssembly: function (token, author, name) {
                return $http({
                    method: "POST",
                    url: '/uninstall_assembly',
                    data: 'token=' + token + '&author=' + author + '&name=' + name,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            }
        }
    })
;
