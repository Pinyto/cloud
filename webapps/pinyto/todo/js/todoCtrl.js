'use strict';

todoApp.controller('todoCtrl',
    function ($scope, Backend, Authenticate, $timeout) {
        // Function Definitions
        $scope.hasID = function (document) {
            return !!document['_id'];
        };

        $scope.addTodo = function () {
            $scope.unfinishedTodo.splice(0, 0, {data: {text: ''}});
        };

        $scope.moveToFinished = function (index) {
            $scope.finishedTodo.splice(0, 0, $scope.unfinishedTodo[index]);
            $scope.unfinishedTodo.splice(index, 1);
        };

        $scope.moveToUnfinished = function (index) {
            $scope.unfinishedTodo.splice(0, 0, $scope.finishedTodo[index]);
            $scope.finishedTodo.splice(index, 1);
        };

        $scope.deleteUnfinishedTodo = function (index) {
            $scope.unfinishedTodo.splice(index, 1);
        };

        $scope.deleteFinishedTodo = function (index) {
            $scope.finishedTodo.splice(index, 1);
        };

        $scope.loadList = function () {
            Backend.getList(Authenticate.getToken()).success(function (data) {
                angular.forEach(data['result'], function (item) {
                    if (item.data.finished) {
                        $scope.finishedTodo.push(item);
                    } else {
                        $scope.unfinishedTodo.push(item);
                    }
                })
            });
        };

        // Initialization
        $scope.unfinishedTodo = [];
        $scope.finishedTodo = [];
        $scope.loadList();
    }
);
