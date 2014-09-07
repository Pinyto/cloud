'use strict';

pinytoWebApp.factory('Authenticate', function (Backend, SessionService) {
    var error = '';
    var authService = {};

    authService.login = function (username, password) {
        return Backend.login(username, password).success(function (data) {
            var response = angular.fromJson(data);
            if ('token' in response) {
                SessionService.set('authenticated', true);
                SessionService.set('token', response['token']);
            } else {
                error = angular.fromJson(data)['error'];
            }
        });
    };

    authService.logout = function () {
        if (authService.isAuthenticated()) {
            Backend.logout();
        }
        SessionService.unset('token');
        SessionService.set('authenticated', false);
    };

    authService.isAuthenticated = function () {
        return SessionService.get('authenticated');
    };

    authService.getToken = function () {
        if (authService.isAuthenticated()) {
            return SessionService.get('token');
        } else {
            return '';
        }
    };

    authService.getLastError = function () {
        return error;
    };

    return authService;
});

pinytoWebApp.factory('SessionService', function () {
    return {
        get: function(key) {
            return sessionStorage.getItem(key);
        },
        set: function(key, data) {
            return sessionStorage.setItem(key, data);
        },
        unset: function(key) {
            return sessionStorage.removeItem(key);
        }
    }
});

pinytoWebApp.run(function ($rootScope, $location, Authenticate) {
    $rootScope.$on('$routeChangeStart', function (event, next, current) {
        if(!Authenticate.isAuthenticated() && !($location.path() in {
            '/login/':'',
            '/register/':'',
            '/':'',
            '/explanation/':'',
            '/hardware/':'',
            '/development/':''})) {
            $location.path('/login/');
        }
    });
});