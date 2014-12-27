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
            update: function(token, book) {
                return $http({
                    method: "POST",
                    url: '/pinyto/Todo/update',
                    data: angular.toJson({'token': token, 'book': book}),
                    headers: {'Content-Type': 'application/json'}
                });
            },
            remove: function(token, book) {
                return $http({
                    method: "POST",
                    url: '/pinyto/Todo/remove',
                    data: angular.toJson({'token': token, 'book': book}),
                    headers: {'Content-Type': 'application/json'}
                });
            }
        }
    })
;
