'use strict';

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
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
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
            searchOrStore: function (token, searchString, place) {
                var ean = getEANifValid(searchString);
                var isbn = getISBNifValid(searchString);
                var promise;
                var savePossible = false;
                if (ean || isbn) {
                    if (ean) {
                        promise = $http({
                            method: 'POST',
                            url: '/bborsalino/Librarian/index',
                            data: 'token=' + token + '&ean=' + ean,
                            headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                        });
                    } else { //must be isbn
                        promise = $http({
                            method: 'POST',
                            url: '/bborsalino/Librarian/index',
                            data: 'token=' + token + '&isbn=' + isbn,
                            headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                        });
                    }
                    promise.success(function (data) {
                        console.log(data);
                        var books = angular.fromJson(data)['index'];
                        if (books.length === 0) {
                            var savePromise;
                            if (ean) {
                                savePromise = $http({
                                    url: '/store',
                                    method: "POST",
                                    data: 'token=' + token + '&type=book&data=' + angular.toJson(
                                        {'ean': ean, 'place': place}
                                    ) + '',
                                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                                });
                            } else { //must be isbn
                                savePromise = $http({
                                    url: '/store',
                                    method: "POST",
                                    data: 'token=' + token + '&type=book&data=' + angular.toJson(
                                        {'isbn': isbn, 'place': place}
                                    ) + '',
                                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                                });
                            }
                            savePromise.success(function (data) {
                                if (angular.fromJson(data)['success']) {
                                    console.log('savedSuccessfully');
                                }
                            });
                            // Save the job to complete the data
                            var jobCreatePromise = $http({
                                    url: '/store',
                                    method: "POST",
                                    data: 'token=' + token + '&type=job&data=' + angular.toJson({
                                        'assembly_user': 'bborsalino',
                                        'assembly_name': 'Librarian',
                                        'job_name': 'job_complete_data_by_asking_dnb'
                                    }) + '',
                                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                                });
                            jobCreatePromise.success(function (data) {
                                if (angular.fromJson(data)['success']) {
                                    console.log('jobCreatedSuccessfully');
                                }
                            });
                        }
                    });
                    savePossible = true;
                } else {
                    if (typeof searchString != 'string') {
                        searchString = "";
                    }
                    promise = $http({
                        method: 'POST',
                        url: '/bborsalino/Librarian/search',
                        data: 'token=' + token + '&searchstring=' + searchString,
                        headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                    });
                }
                return {'promise': promise, 'savePossible': savePossible};
            },
            update: function(token, book) {
                return $http({
                    method: "POST",
                    url: '/bborsalino/Librarian/update',
                    data: 'token=' + token + '&book=' + btoa(unescape(encodeURIComponent(angular.toJson(book)))),
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            },
            duplicate: function(token, book) {
                return $http({
                    method: "POST",
                    url: '/bborsalino/Librarian/duplicate',
                    data: 'token=' + token + '&book=' + angular.toJson(book),
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            },
            remove: function(token, book) {
                return $http({
                    method: "POST",
                    url: '/bborsalino/Librarian/remove',
                    data: 'token=' + token + '&book=' + angular.toJson(book),
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            },
            statistics: function (token) {
                return $http({
                    method: "POST",
                    url: '/bborsalino/Librarian/statistics',
                    data: 'token=' + token,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                });
            }
        }
    })
;
