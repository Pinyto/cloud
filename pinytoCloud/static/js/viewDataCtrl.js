'use strict';

pinytoWebApp.controller('PinytoViewDataCtrl',
    function ($scope, $rootScope, Backend, Authenticate) {
        // Function Definitions
        $scope.getKeys = function (object) {
            var keys = [];
            for (var attribute in object) {
                if (object.hasOwnProperty(attribute) && (attribute != '$$hashKey')) {
                    keys.push({});
                }
            }
            console.log(keys);
            return keys;
        };

        $scope.changeAttribute = function (document, attribute) {
            //if (attribute.oldValue != attribute.newValue) {
            //    console.log(attribute.oldValue);
            //    console.log(attribute.newValue);
                //document[attribute.newValue] = document[attribute.oldValue];
                //delete document[attribute.oldValue];
            //}
        };

        $scope.printIt = function (document) {
            console.log(document);
        };

        $scope.saveDocument = function (document) {
            Backend.saveDocument(Authenticate.getToken(), document).success(function (data) {
                var response = angular.fromJson(data);
                if (response['success']) {
                    document['_id'] = response['_id'];
                }
            });
        };

        $scope.addDocument = function () {
            $scope.localDocuments.push(
                [
                    {
                        attribute: 'type',
                        value: ''
                    }
                ]);
        };

        $scope.addAttribute = function (localDocument) {
            localDocument.push({
                attribute: '',
                value: ''
            });
        };

        // Initialization
        $scope.lang = $rootScope.language;
        $scope.localDocuments = [];
        $scope.offset = 0;

        // Event handlers
        $scope.$on('langChange', function (event, newLang) {
            $scope.lang = newLang;
        });
    }
);
