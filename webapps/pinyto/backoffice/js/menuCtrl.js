'use strict';

pinytoWebApp.controller('PinytoMenuCtrl', function($scope, $location) {
    $scope.isActive = function (pathBeginning) {
        var matches = $location.path().match("^/?([^/]+)/.*$");
        if (matches && (matches.length >= 2)) {
            if (pathBeginning == matches[1]) {
                return true;
            }
        }
        return false;
    }
});
