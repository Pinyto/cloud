'use strict';

var pinytoCloud = 'http://cloud.pinyto.de/';

function getEANifValid(string) {
    if (typeof string != 'string') {
        string = "";
    }
    var match = /^[0-9]{13}$/.exec(string.replace(/\s+/g, ''));
    if (match) {
        return match[0];
    } else {
        return null;
    }
}

function getISBNifValid(string) {
    if (typeof string != 'string') {
        string = "";
    }
    var match = /^(97[8,9]-)?[0-9]{1,5}-[0-9]{1,6}-[0-9]{1,6}-[0-9]{1,6}$/.exec(string.replace(/\s+/g, ''));
    if ((match) && ((match[0].length == 13) || (match[0].length == 17))) {
        return match[0];
    } else {
        return null;
    }
}

angular.module('BibServices', [])
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
            searchOrStore: function (searchString, place, books) {
                var ean = getEANifValid(searchString);
                var isbn = getISBNifValid(searchString);
                var promise;
                if (ean || isbn) {
                    if (ean) {
                        promise = $http({method: 'GET', url:pinytoCloud+'?type=index&ean=' + ean});
                    } else { //must be isbn
                        promise = $http({method: 'GET', url:pinytoCloud+'?type=index&isbn=' + isbn});
                    }
                    promise.success(function (data) {
                        var books = angular.fromJson(data)['index'];
                        if (books.length == 0) {
                            var savePromise;
                            if (ean) {
                                savePromise = $http({
                                    url: pinytoCloud+'.store',
                                    method: "POST",
                                    data: 'type=book&data='+angular.toJson({'ean': ean, 'place': place})+'',
                                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                                });
                            } else { //must be isbn
                                savePromise = $http({
                                    url: pinytoCloud+'.store',
                                    method: "POST",
                                    data: 'type=book&data='+angular.toJson({'isbn': isbn, 'place': place})+'',
                                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                                });
                            }
                            savePromise.success(function (data) {
                                if (angular.fromJson(data)['success']) {
                                    console.log('savedSuccessfully');
                                }
                            });
                        }
                    });
                } else {
                    if (typeof searchString != 'string') {
                        searchString = "";
                    }
                    promise = $http.get(pinytoCloud+'?type=search&searchstring=' + searchString);
                }
                return promise;
            },
            update: function(book) {
                var promise = $http({
                    url: pinytoCloud+'?type=update',
                    method: "POST",
                    data: 'book=' + angular.toJson(book),
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
                return promise;
            },
            statistics: function () {
                return $http({method: 'GET', url:pinytoCloud+'?type=statistics'});
            }
        }
    })
;
