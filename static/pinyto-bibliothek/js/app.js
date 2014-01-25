'use strict';

angular.module('Bib', ['BibServices', 'ngRoute'])
    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider.
            when('/', {templateUrl: '/index.html', controller: bibCtrl}).
            otherwise({templateUrl: '/index.html', controller: bibCtrl});
    }]);