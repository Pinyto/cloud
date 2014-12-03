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
                    data: {'name': username, 'password': password},
                    headers: {'Content-Type': 'application/json'}
                });
            },
            logout: function (token) {
                return $http({
                    url: '/keyserver/logout',
                    method: "POST",
                    data: {'token': token},
                    headers: {'Content-Type': 'application/json'}
                });
            },
            register: function (username, password) {
                return $http({
                    url: '/keyserver/register',
                    method: "POST",
                    data: {'name': username, 'password': password},
                    headers: {'Content-Type': 'application/json'}
                });
            },
            statistics: function (token) {
                return $http({
                    method: "POST",
                    url: '/statistics',
                    data: {'token': token},
                    headers: {'Content-Type': 'application/json'}
                });
            },
            changePassword: function (token, password) {
                return $http({
                    method: "POST",
                    url: '/keyserver/change_password',
                    data: {'token': token, 'password': password},
                    headers: {'Content-Type': 'application/json'}
                });
            },
            listKeys: function (token) {
                return $http({
                    method: "POST",
                    url: '/list_keys',
                    data: {'token': token},
                    headers: {'Content-Type': 'application/json'}
                });
            },
            setKeyActive: function (token, keyHash, activeState) {
                return $http({
                    method: "POST",
                    url: '/set_key_active',
                    data: {'token': token, 'key_hash': keyHash, 'active_state': activeState},
                    headers: {'Content-Type': 'application/json'}
                });
            },
            deleteKey: function (token, keyHash) {
                return $http({
                    method: "POST",
                    url: '/delete_key',
                    data: {'token': token, 'key_hash': keyHash},
                    headers: {'Content-Type': 'application/json'}
                });
            },
            listOwnAssemsblies: function (token) {
                return $http({
                    method: "POST",
                    url: '/list_own_assemblies',
                    data: {'token': token},
                    headers: {'Content-Type': 'application/json'}
                });
            },
            saveAssembly: function (token, originalName, assemblyJson) {
                return $http({
                    method: "POST",
                    url: '/save_assembly',
                    data: {'token': token, 'original_name': originalName, 'data': assemblyJson},
                    headers: {'Content-Type': 'application/json'}
                });
            },
            deleteAssembly: function (token, name) {
                return $http({
                    method: "POST",
                    url: '/delete_assembly',
                    data: {'token': token, 'name': name},
                    headers: {'Content-Type': 'application/json'}
                });
            },
            listInstalledAssemsblies: function (token) {
                return $http({
                    method: "POST",
                    url: '/list_installed_assemblies',
                    data: {'token': token},
                    headers: {'Content-Type': 'application/json'}
                });
            },
            listAllAssemsblies: function (token) {
                return $http({
                    method: "POST",
                    url: '/list_all_assemblies',
                    data: {'token': token},
                    headers: {'Content-Type': 'application/json'}
                });
            },
            installAssembly: function (token, author, name) {
                return $http({
                    method: "POST",
                    url: '/install_assembly',
                    data: {'token': token, 'author': author, 'name': name},
                    headers: {'Content-Type': 'application/json'}
                });
            },
            uninstallAssembly: function (token, author, name) {
                return $http({
                    method: "POST",
                    url: '/uninstall_assembly',
                    data: {'token': token, 'author': author, 'name': name},
                    headers: {'Content-Type': 'application/json'}
                });
            },
            getAssemblySource: function (token, author, name) {
                return $http({
                    method: "POST",
                    url: '/get_assembly_source',
                    data: {'token': token, 'author': author, 'name': name},
                    headers: {'Content-Type': 'application/json'}
                });
            },
            searchDocuments: function (token, query, skip, limit) {
                var data = {'token': token};
                if (limit) {
                    data['limit'] = limit;
                }
                if (skip) {
                    data['skip'] = skip;
                }
                if (query) {
                    data['query'] = query;
                }
                return $http({
                    method: "POST",
                    url: '/pinyto/DocumentsAdmin/search',
                    data: data,
                    headers: {'Content-Type': 'application/json'}
                });
            },
            saveDocument: function (token, document) {
                return $http({
                    method: "POST",
                    url: '/pinyto/DocumentsAdmin/save',
                    data: {'token': token, 'document': document},
                    headers: {'Content-Type': 'application/json'}
                });
            },
            deleteDocument: function (token, document) {
                return $http({
                    method: "POST",
                    url: '/pinyto/DocumentsAdmin/delete',
                    data: {'token': token, 'document': document},
                    headers: {'Content-Type': 'application/json'}
                });
            }
        }
    })
;
