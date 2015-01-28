'use strict';

todoApp.controller('todoCtrl',
    function ($scope, Backend, Authenticate, $interval, $rootScope) {
        // Function Definitions
        $scope.hasID = function (document) {
            return !!document['_id'];
        };

        $scope.checkIfDocumentIsChanged = function (document) {
            for (var i = 0; i < $scope.cloudList.length; i++) {
                if ($scope.cloudList[i]['_id'] == document['_id']) {
                    if (($scope.cloudList[i]['data']['text'] != document['data']['text']) ||
                        ($scope.cloudList[i]['data']['finished'] != document['data']['finished']) ||
                        ($scope.cloudList[i]['data']['priority'] != document['data']['priority'])) {
                        return true;
                    }
                }
            }
            return false;
        };

        $scope.createTransmissionDocument = function (document) {
            var tDoc = {
                '_id': document['_id'],
                'type': 'todo',
                'data': document['data']
            };
            if (document['time']) {
                tDoc['time'] = document['time'];
            }
            if (document['data']['finished']) {
                document['data']['finished'] = 1;
            } else {
                document['data']['finished'] = 0;
            }
            return tDoc;
        };

        $scope.saveDocumentIfNecessary = function (document) {
            if ($scope.hasID(document)) {
                if ($scope.checkIfDocumentIsChanged(document)) {
                    Backend.save(
                        Authenticate.getToken(),
                        $scope.createTransmissionDocument(document)
                    ).success(function (data) {
                        if (data['success']) {
                            document['_id'] = data['_id'];
                        }
                    });
                }
            } else {
                Backend.save(
                    Authenticate.getToken(),
                    $scope.createTransmissionDocument(document)
                ).success(function (data) {
                    if (data['success']) {
                        document['_id'] = data['_id'];
                    }
                    $scope.loadList();
                });
            }
        };

        $scope.checkForUnsaved = function () {
            var i, j;
            for (i = 0; i < $scope.unfinishedTodo.length; i++) {
                $scope.saveDocumentIfNecessary($scope.unfinishedTodo[i]);
            }
            for (i = 0; i < $scope.finishedTodo.length; i++) {
                $scope.saveDocumentIfNecessary($scope.finishedTodo[i]);
            }
            if ($scope.cloudList) {
                for (i = 0; i < $scope.cloudList.length; i++) {
                    var found = false;
                    for (j = 0; j < $scope.unfinishedTodo.length; j++) {
                        if ($scope.cloudList[i]['_id'] == $scope.unfinishedTodo[j]['_id']) {
                            found = true;
                        }
                    }
                    for (j = 0; j < $scope.finishedTodo.length; j++) {
                        if ($scope.cloudList[i]['_id'] == $scope.finishedTodo[j]['_id']) {
                            found = true;
                        }
                    }
                    if (!found) {
                        var deletedDoc = $scope.cloudList[i];
                        Backend.delete(
                            Authenticate.getToken(),
                            {'_id': $scope.cloudList[i]['_id']}
                        ).success(function (data) {
                            if (!data['success']) {
                                $scope.cloudList.splice(i, 0, deletedDoc);
                            }
                        }).error(function () {
                            $scope.cloudList.splice(i, 0, deletedDoc);
                        });
                        $scope.cloudList.splice(i, 1);
                    }
                }
            }
        };

        $scope.addTodo = function () {
            $scope.unfinishedTodo.splice(0, 0, {data: {text: '', finished: false}});
        };

        $scope.moveToFinished = function (index) {
            $scope.unfinishedTodo[index]['data']['finished'] = true;
            $scope.finishedTodo.splice(0, 0, $scope.unfinishedTodo[index]);
            $scope.unfinishedTodo.splice(index, 1);
            $scope.checkForUnsaved();
        };

        $scope.moveToUnfinished = function (index) {
            $scope.finishedTodo[index]['data']['finished'] = false;
            $scope.unfinishedTodo.splice(0, 0, $scope.finishedTodo[index]);
            $scope.finishedTodo.splice(index, 1);
            $scope.checkForUnsaved();
        };

        $scope.deleteUnfinishedTodo = function (index) {
            $scope.unfinishedTodo.splice(index, 1);
            $scope.checkForUnsaved();
        };

        $scope.deleteFinishedTodo = function (index) {
            $scope.finishedTodo.splice(index, 1);
            $scope.checkForUnsaved();
        };

        $scope.moveFinishedUp = function (index) {
            var document = $scope.finishedTodo.splice(index, 1)[0];
            $scope.finishedTodo.splice(0, 0, document);
            $scope.setPriorityFromOrder();
            $scope.checkForUnsaved();
        };

        $scope.moveUnfinishedUp = function (index) {
            var document = $scope.unfinishedTodo.splice(index, 1)[0];
            $scope.unfinishedTodo.splice(0, 0, document);
            $scope.setPriorityFromOrder();
            $scope.checkForUnsaved();
        };

        $scope.setPriorityFromOrder = function () {
            var i;
            for (i = 0; i < $scope.unfinishedTodo.length; i++) {
                $scope.unfinishedTodo[i]['data']['priority'] = i;
            }
            for (i = 0; i < $scope.finishedTodo.length; i++) {
                $scope.finishedTodo[i]['data']['priority'] = i;
            }
        };

        $scope.loadList = function () {
            Backend.getList(Authenticate.getToken()).success(function (data) {
                if (data['error'] == 'Unknown token. Please authenticate.') {
                    $rootScope.logout();
                }
                var found, i;
                $scope.cloudList = [];
                angular.forEach(data['result'], function (item) {
                    if (item['data']['finished']) {
                        item['data']['finished'] = true;
                        $scope.cloudList.push(angular.copy(item));
                        found = false;
                        angular.forEach($scope.finishedTodo, function (point) {
                            if (point['_id'] == item['_id']) {
                                found = true;
                            }
                        });
                        if (!found) {
                            $scope.finishedTodo.push(item);
                        }
                    } else {
                        item['data']['finished'] = false;
                        $scope.cloudList.push(angular.copy(item));
                        found = false;
                        angular.forEach($scope.unfinishedTodo, function (point) {
                            if (point['_id'] == item['_id']) {
                                found = true;
                            }
                        });
                        if (!found) {
                            $scope.unfinishedTodo.push(item);
                        }
                    }
                });
                for (i = 0; i < $scope.finishedTodo.length; i++) {
                    found = false;
                    angular.forEach(data['result'], function (item) {
                        if (item['_id'] == $scope.finishedTodo[i]['_id']) {
                            found = true;
                            $scope.finishedTodo[i]['type'] = item['type'];
                            if (item['assembly']) {
                                $scope.finishedTodo[i]['assembly'] = item['assembly'];
                            }
                            if (item['time']) {
                                $scope.finishedTodo[i]['time'] = item['time'];
                            }
                            if (item['tags']) {
                                $scope.finishedTodo[i]['tags'] = item['tags'];
                            }
                            $scope.finishedTodo[i]['data']['finished'] = item['data']['finished'];
                            $scope.finishedTodo[i]['data']['text'] = item['data']['text'];
                        }
                    });
                    if (!found) {
                        $scope.finishedTodo.splice(i, 1);
                    }
                }
                for (i = 0; i < $scope.unfinishedTodo.length; i++) {
                    found = false;
                    angular.forEach(data['result'], function (item) {
                        if (item['_id'] == $scope.unfinishedTodo[i]['_id']) {
                            found = true;
                            $scope.unfinishedTodo[i]['type'] = item['type'];
                            if (item['assembly']) {
                                $scope.unfinishedTodo[i]['assembly'] = item['assembly'];
                            }
                            if (item['time']) {
                                $scope.unfinishedTodo[i]['time'] = item['time'];
                            }
                            if (item['tags']) {
                                $scope.unfinishedTodo[i]['tags'] = item['tags'];
                            }
                            $scope.unfinishedTodo[i]['data']['finished'] = item['data']['finished'];
                            $scope.unfinishedTodo[i]['data']['text'] = item['data']['text'];
                        }
                    });
                    if (!found) {
                        $scope.unfinishedTodo.splice(i, 1);
                    }
                }
                var compare = function (a, b) {
                    var aPriority = parseInt(a['data']['priority']);
                    if (isNaN(aPriority)) {
                        aPriority = 0;
                    }
                    var bPriority = parseInt(b['data']['priority']);
                    if (isNaN(bPriority)) {
                        bPriority = 0;
                    }
                    if (aPriority < bPriority) {
                        return -1;
                    } else if (aPriority > bPriority) {
                        return 1;
                    }
                    return 0;
                };
                $scope.unfinishedTodo.sort(compare);
                $scope.finishedTodo.sort(compare);
                $scope.setPriorityFromOrder();
            });
        };

        // Initialization
        $scope.unfinishedTodo = [];
        $scope.finishedTodo = [];
        $scope.loadList();

        $interval($scope.loadList, 30000);
    }
);
