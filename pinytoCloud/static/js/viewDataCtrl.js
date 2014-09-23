'use strict';

pinytoWebApp.controller('PinytoViewDataCtrl',
    function ($scope, $rootScope, Backend, Authenticate) {
        // Function Definitions
        $scope.createLocalDocumentStructure = function (data) {
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
                            value: $scope.createLocalDocumentStructure(data[attribute])
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
                        value: $scope.createLocalDocumentStructure(data[i])
                    })
                }
            } else {
                return angular.copy(data);
            }
        };

        $scope.convertLocalStructureToOnlineStructure = function (localStructure, type) {
            var structure, i;
            if (type == 'array') {
                structure = [];
                for (i = 0; i < localStructure.length; i++) {
                    structure.push($scope.convertLocalStructureToOnlineStructure(
                        localStructure[i].value,
                        localStructure[i].type
                    ));
                }
                return structure;
            } else if (type == 'object') {
                structure = {};
                for (i = 0; i < localStructure.length; i++) {
                    structure[localStructure[i].attribute] = $scope.convertLocalStructureToOnlineStructure(
                        localStructure[i].value,
                        localStructure[i].type
                    );
                }
                return structure;
            } else {
                return angular.copy(localStructure);
            }
        };

        $scope.saveDocument = function (localDocument) {
            var document = {};
            if (localDocument['_id']) {
                document['_id'] = localDocument['_id'];
            }
            if (localDocument['type']) {
                document['type'] = localDocument['type'];
            } else {
                document['type'] = "";
            }
            if (localDocument['time']) {
                document['time'] = localDocument['time'];
            }
            if (localDocument['tags']) {
                document['tags'] = localDocument['tags'];
            } else {
                document['tags'] = [];
            }
            if (localDocument['data']) {
                document['data'] = $scope.convertLocalStructureToOnlineStructure(
                    localDocument['data'],
                    localDocument['dataType']
                );
            } else {
                document['data'] = {};
            }
            Backend.saveDocument(Authenticate.getToken(), angular.toJson(document)).success(function (data) {
                var response = angular.fromJson(data);
                if (response['success']) {
                    localDocument['_id'] = response['_id'];
                    $scope.updateDocument(localDocument);
                }
            });
        };

        $scope.updateDocument = function (localDocument) {
            if (localDocument['_id']) {
                Backend.searchDocuments(
                    Authenticate.getToken(),
                    angular.toJson({'_id': localDocument['_id']}),
                    0,
                    1
                ).success(function (data) {
                    var documentData = angular.fromJson(data)['result'][0];
                    var newLocalDocument = {};
                    newLocalDocument['_id'] = documentData['_id'];
                    newLocalDocument['type'] = documentData['type'];
                    newLocalDocument['time'] = documentData['time'];
                    newLocalDocument['tags'] = documentData['tags'];
                    if (angular.isObject(documentData['data'])) {
                        newLocalDocument['dataType'] = 'object';
                    }
                    if (angular.isArray(documentData['data'])) {
                        newLocalDocument['dataType'] = 'array';
                    } else {
                        newLocalDocument['dataType'] = 'simple';
                    }
                    newLocalDocument['data'] = $scope.createLocalDocumentStructure(documentData['data']);
                    localDocument = newLocalDocument;
                    if ($scope.localDocuments) {
                        for (var i = 0; i < $scope.localDocuments.length; i++) {
                            if (localDocument['_id'] == $scope.localDocuments[i]['_id']) {
                                $scope.documents[i] = documentData;
                            }
                        }
                    }
                });
            }
        };

        $scope.documentChanged = function (index) {
            if ($scope.documents && ($scope.documents.length > index)) {
                if ((($scope.documents[index]['_id']) &&
                     ($scope.documents[index]['_id'] != $scope.localDocuments[index]['_id'])) ||
                    (($scope.documents[index]['type']) &&
                     ($scope.documents[index]['type'] != $scope.localDocuments[index]['type'])) ||
                    (($scope.documents[index]['time']) &&
                    ($scope.documents[index]['time'] != $scope.localDocuments[index]['time'])) ||
                    (($scope.documents[index]['tags']) &&
                    (!angular.equals($scope.documents[index]['tags'], $scope.localDocuments[index]['tags'])))) {
                    return true;
                }
                return !!(($scope.documents[index]['data']) &&
                    (!angular.equals($scope.documents[index]['data'], $scope.convertLocalStructureToOnlineStructure(
                        $scope.localDocuments[index]['data'],
                        $scope.localDocuments[index]['dataType']
                    ))));
            } else {
                return true;
            }
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
                {
                    'type': "",
                    'tags': [],
                    'data': "",
                    'dataType': 'simple',
                    'validFormat': true
                });
        };

        $scope.addAttribute = function (localObject) {
            localObject.push({
                attribute: '',
                type: 'simple',
                value: ''
            });
        };

        $scope.deleteAttribute = function (localObject, index) {
            localObject.splice(index, 1);
        };

        $scope.addItem = function (localArray) {
            localArray.push({
                type: 'simple',
                value: ''
            });
        };

        $scope.deleteItem = function (localArray, index) {
            localArray.splice(index, 1);
        };

        $scope.addTag = function (index) {
            if ($scope.localDocuments[index].tags.indexOf("") < 0) {
                $scope.localDocuments[index].tags.push("");
            }
        };

        $scope.deleteTag = function (documentIndex, tagIndex) {
            $scope.localDocuments[documentIndex].tags.splice(tagIndex, 1);
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
                            'data': $scope.createLocalDocumentStructure($scope.documents[i]['data']),
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
                });
            }
        };

        $scope.deleteDocument = function (localDocument, index) {
            if (localDocument['_id']) {
                Backend.deleteDocument(
                    Authenticate.getToken(),
                    angular.toJson({'_id': localDocument['_id']})
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
                return [];
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
