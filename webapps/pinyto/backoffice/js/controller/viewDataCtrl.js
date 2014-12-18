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
            if (localDocument['assembly']) {
                document['assembly'] = localDocument['assembly'];
            } else {
                document['assembly'] = "";
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
            $scope.saving = true;
            Backend.saveDocument(Authenticate.getToken(), document).success(function (data) {
                $scope.saving = undefined;
                var response = angular.fromJson(data);
                if (response['success']) {
                    localDocument['_id'] = response['_id'];
                    $scope.updateDocument(localDocument);
                }
            });
        };

        $scope.updateDocument = function (localDocument) {
            if (localDocument['_id']) {
                $scope.updating = true;
                Backend.searchDocuments(
                    Authenticate.getToken(),
                    {'_id': localDocument['_id']},
                    0,
                    1
                ).success(function (data) {
                    $scope.updating = undefined;
                    var documentData = angular.fromJson(data)['result'][0];
                    var newLocalDocument = {};
                    newLocalDocument['_id'] = documentData['_id'];
                    newLocalDocument['type'] = documentData['type'];
                    newLocalDocument['assembly'] = documentData['assembly'];
                    newLocalDocument['time'] = documentData['time'];
                    newLocalDocument['tags'] = angular.copy(documentData['tags']);
                    var dataType = 'simple';
                    if (angular.isObject(documentData['data'])) {
                        dataType = 'object';
                    }
                    if (angular.isArray(documentData['data'])) {
                        dataType = 'array';
                    }
                    newLocalDocument['dataType'] = dataType;
                    newLocalDocument['data'] = $scope.createLocalDocumentStructure(documentData['data']);
                    if ($scope.localDocuments) {
                        for (var i = 0; i < $scope.localDocuments.length; i++) {
                            if (localDocument['_id'] == $scope.localDocuments[i]['_id']) {
                                $scope.documents[i] = documentData;
                                $scope.localDocuments[i] = newLocalDocument;
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
                    (($scope.documents[index]['assembly']) &&
                     ($scope.documents[index]['assembly'] != $scope.localDocuments[index]['assembly'])) ||
                    (($scope.documents[index]['time']) &&
                    ($scope.documents[index]['time'] != $scope.localDocuments[index]['time']))) {
                    return true;
                }
                if ($scope.documents[index]['tags']) {
                    if ($scope.documents[index]['tags'].length != $scope.localDocuments[index]['tags'].length) {
                        return true;
                    }
                    for (var i = 0; i < $scope.documents[index]['tags'].length; i++) {
                        if ($scope.documents[index]['tags'][i] != $scope.localDocuments[index]['tags'][i]) {
                            return true;
                        }
                    }
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
                    'assembly': "",
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
            $scope.localDocuments[index].tags.push("");
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
                $scope.searchingInProgress = true;
                Backend.searchDocuments(
                    Authenticate.getToken(),
                    angular.fromJson($scope.query),
                    $scope.offset,
                    $scope.limit
                ).success(function (data) {
                    $scope.searchingInProgress = undefined;
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
                            'assembly': $scope.documents[i]['assembly'],
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
                    {'_id': localDocument['_id']}
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

        $scope.revertDocument = function (index) {
            var dataType = 'simple';
            if (angular.isObject($scope.documents[index]['data'])) {
                dataType = 'object';
            }
            if (angular.isArray($scope.documents[index]['data'])) {
                dataType = 'array';
            }
            $scope.localDocuments[index]['_id'] = angular.copy($scope.documents[index]['_id']);
            $scope.localDocuments[index]['time'] = angular.copy($scope.documents[index]['time']);
            $scope.localDocuments[index]['type'] = angular.copy($scope.documents[index]['type']);
            $scope.localDocuments[index]['tags'] = angular.copy($scope.documents[index]['tags']);
            $scope.localDocuments[index]['assembly'] = angular.copy($scope.documents[index]['assembly']);
            $scope.localDocuments[index]['data'] = $scope.createLocalDocumentStructure(
                $scope.documents[index]['data']
            );
            $scope.localDocuments[index]['dataType'] = dataType;
            $scope.localDocuments[index]['validFormat'] = true;
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
