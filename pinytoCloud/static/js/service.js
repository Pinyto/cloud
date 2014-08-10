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
                    url: pinytoKeyserver+'authenticate',
                    method: "POST",
                    data: 'name='+username+'&password='+password,
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                });
            },
            statistics: function (token) {
                return $http({
                    method: "POST",
                    url: pinytoCloud + 'bborsalino/Librarian/statistics',
                    data: 'token=' + token,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            }
        }
    })
;
