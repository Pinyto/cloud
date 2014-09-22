'use strict';

pinytoWebApp.controller('PinytoViewDataCtrl',
    function ($scope, $rootScope, Backend, Authenticate) {
        // Function Definitions
        $scope.saveDocument = function (localDocument) {
            var document = {};
            for (var i = 0; i < localDocument.length; i++) {
                document[localDocument[i].attribute] = localDocument[i].value;
            }
            Backend.saveDocument(Authenticate.getToken(), angular.toJson(document)).success(function (data) {
                var response = angular.fromJson(data);
                if (response['success']) {
                    var found = false;
                    for (var i = 0; i < localDocument.length; i++) {
                        if (localDocument[i].attribute == '_id') {
                            found = true;
                            localDocument[i].value = response['_id'];
                            break;
                        }
                    }
                    if (!found) {
                        localDocument.splice(0, 0, {
                            attribute: '_id',
                            value: response['_id']
                        })
                    }
                    $scope.updateDocument(localDocument);
                }
            });
        };

        $scope.updateDocument = function (localDocument) {
            for (var i = 0; i < localDocument.length; i++) {
                if (localDocument[i].attribute == '_id') {
                    var documentId = localDocument[i].value;
                    break;
                }
            }
            if (documentId) {
                Backend.searchDocuments(
                    Authenticate.getToken(),
                    angular.toJson({'_id': documentId}),
                    0,
                    1
                ).success(function (data) {
                    var documentData = angular.fromJson(data);
                    var newLocalDocument = [];
                    for (var attribute in documentData) {
                        if (documentData.hasOwnProperty(attribute)) {
                            newLocalDocument.push({attribute: attribute, value: documentData[attribute]});
                        }
                    }
                    localDocument = newLocalDocument;
                });
            }
        };

        $scope.documentChanged = function (index) {
            var i;
            if ($scope.documents && ($scope.documents.length > index)) {
                for (var attribute in $scope.documents[index]) {
                    if ($scope.documents[index].hasOwnProperty(attribute)) {
                        var keyFound = false;
                        for (i = 0; i < $scope.localDocuments[index].length; i++) {
                            if (attribute == $scope.localDocuments[index][i].attribute) {
                                keyFound = true;
                                if ($scope.documents[index][attribute] != $scope.localDocuments[index][i].value) {
                                    return true;
                                }
                            }
                        }
                        if (!keyFound) {
                            return true
                        }
                    }
                }
                for (i = 0; i < $scope.localDocuments[index].length; i++) {
                    if (!($scope.localDocuments[index][i].attribute in $scope.documents[index]) ||
                        ($scope.documents[index][$scope.localDocuments[index][i].attribute] !=
                            $scope.localDocuments[index][i].value)) {
                        return true;
                    }
                }
            } else {
                return true;
            }
            return false;
        };

        $scope.documentIsValid = function (localDocument) {
            for (var i = 0; i < localDocument.length; i++) {
                if ((localDocument[i].attribute == 'type') && (localDocument[i].value.length <= 0)) {
                    return false;
                }
            }
            return true;
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

        $scope.addAttribute = function (localObject) {
            localObject.push({
                attribute: '',
                type: 'simple',
                value: ''
            });
        };

        $scope.addItem = function (localArray) {
            localArray.push({
                type: 'simple',
                value: ''
            });
        };

        $scope.validQuery = function () {
            try {
                angular.fromJson($scope.query);
                return true;
            } catch (exception) {
                return false;
            }
        };

        $scope.searchDocuments = function () {
            var createLocalDocumentStructure = function (data) {
                if (angular.isObject(data)) {
                    var localObjectStructure = [];
                    for (var attribute in data) {
                        if (data.hasOwnProperty(attribute)) {
                            var type = 'simple';
                            if (angular.isObject(data[attribute])) {
                                type = 'object';
                            }
                            if (angular.isArray(data[attribute])) {
                                type = 'array';
                            }
                            localObjectStructure.push({
                                attribute: attribute,
                                type: type,
                                value: createLocalDocumentStructure(data[attribute])
                            });
                        }
                    }
                    return localObjectStructure;
                } else if (angular.isArray(data)) {
                    var localArrayStructure = [];
                    for (var i = 0; i < data.length; i++) {
                        type = 'simple';
                        if (angular.isObject(data[i])) {
                            type = 'object';
                        }
                        if (angular.isArray(data[i])) {
                            type = 'array';
                        }
                        localArrayStructure.push({
                            type: type,
                            value: createLocalDocumentStructure(data[i])
                        })
                    }
                } else {
                    return angular.copy(data);
                }
            };
            if ($scope.validQuery()) {
                Backend.searchDocuments(
                    Authenticate.getToken(),
                    $scope.query,
                    $scope.offset,
                    $scope.limit
                ).success(function (data) {
                    $scope.localDocuments = [];
                    $scope.documents = angular.fromJson(data)['result'];
                    for (var i = 0; i < $scope.documents.length; i++) {
                        var dataType = 'simple';
                        if (angular.isObject($scope.documents[i]['data'])) {
                            dataType = 'object';
                        }
                        if (angular.isArray($scope.documents[i]['data'])) {
                            dataType = 'array';
                        }
                        $scope.localDocuments.push({
                            '_id': $scope.documents[i]['_id'],
                            'time': $scope.documents[i]['time'],
                            'type': $scope.documents[i]['type'],
                            'tags': [],
                            'data': createLocalDocumentStructure($scope.documents[i]['data']),
                            'dataType': dataType,
                            'validFormat': true
                        });
                        if ($scope.documents[i]['tags']) {
                            if (angular.isArray($scope.documents[i]['tags'])) {
                                for (var j = 0; j < $scope.documents[i]['tags'].length; j++) {
                                    if (angular.isString($scope.documents[i]['tags'][j])) {
                                        $scope.localDocuments[i]['tags'].push($scope.documents[i]['tags'][j]);
                                    } else {
                                        $scope.localDocuments[i]['validFormat'] = false;
                                    }
                                }
                            } else {
                                $scope.localDocuments[i]['validFormat'] = false;
                            }
                        }
                    }
                    console.log($scope.documents);
                    console.log($scope.localDocuments);
                });
            }
        };

        $scope.deleteDocument = function (localDocument, index) {
            var documentId = undefined;
            for (var i = 0; i < localDocument.length; i++) {
                if (localDocument[i].attribute == '_id') {
                    documentId = localDocument[i].value
                }
            }
            if (documentId) {
                Backend.deleteDocument(
                    Authenticate.getToken(),
                    angular.toJson({'_id': documentId})
                ).success(function (data) {
                    if (angular.fromJson(data)['success']) {
                        $scope.documents.splice(index, 1);
                        $scope.localDocuments.splice(index, 1);
                    }
                })
            } else {
                $scope.localDocuments.splice(index, 1);
            }
        };

        $scope.getInitialValue = function (type) {
            if (type == 'object') {
                return {};
            } else if (type == 'array') {
                return [];
            } else {
                return "";
            }
        };

        // Initialization
        $scope.lang = $rootScope.language;
        $scope.localDocuments = [];
        $scope.offset = 0;
        $scope.limit = 20;
        $scope.query = "{}";
        $scope.searchDocuments();

        // Event handlers
        $scope.$on('langChange', function (event, newLang) {
            $scope.lang = newLang;
        });
    }
);
