'use strict';

angular.module('TodoServices', [])
    .config(['$httpProvider', function($httpProvider) {
        $httpProvider.defaults.useXDomain = true;
        delete $httpProvider.defaults.headers.common['X-Requested-With'];
    }])
    .factory('Backend', function ($http) {
        return {
            login: function (username, password) {
                return $http({
                    url: '/keyserver/authenticate',
                    method: "POST",
                    data: angular.toJson({'name': username, 'password': password}),
                    headers: {'Content-Type': 'application/json'}
                });
            },
            logout: function (token) {
                return $http({
                    url: '/keyserver/logout',
                    method: "POST",
                    data: angular.toJson({'token': token}),
                    headers: {'Content-Type': 'application/json'}
                });
            },
            getList: function(token) {
                return $http({
                    method: "POST",
                    url: '/pinyto/Todo/get_list',
                    data: angular.toJson({'token': token}),
                    headers: {'Content-Type': 'application/json'}
                })
            },
            save: function(token, document) {
                document['type'] = 'todo';
                return $http({
                    method: "POST",
                    url: '/pinyto/Todo/save',
                    data: angular.toJson({'token': token, 'document': document}),
                    headers: {'Content-Type': 'application/json'}
                });
            },
            delete: function(token, document) {
                return $http({
                    method: "POST",
                    url: '/pinyto/Todo/delete',
                    data: angular.toJson({'token': token, 'document': document}),
                    headers: {'Content-Type': 'application/json'}
                });
            }
        }
    })
;
