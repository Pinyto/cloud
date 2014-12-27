'use strict';

todoApp.controller('todoCtrl',
    function ($scope, Backend, Authenticate, $timeout) {
    // Function Definitions
    $scope.hasID = function (document) {
        return !!document['_id'];
    };

    // Initialization

});
