'use strict';

function checkFocusChange() {
    if (document.focusChangeCountdown == 0) {
        document.getElementById('search').focus();
        document.focusChangeCountdown = 3;
    } else {
        document.focusChangeCountdown -= 1;
    }
    setTimeout(checkFocusChange, 1000);
}

function bibCtrl($scope, Backend, $routeParams) {
    $scope.showPlaceSelector = false;
    $scope.bookCount  = 0;
    $scope.placesUsed = ['Arbeitszimmer', 'Wohnzimmer'];
    $scope.lentCount  = 0;
    $scope.statistics  = function () {
        Backend.statistics().success(function (data) {
            var statistics = angular.fromJson(data);
            $scope.bookCount  = statistics['book_count'];
            $scope.placesUsed = statistics['places_used'];
            $scope.lentCount  = statistics['lent_count'];
        })
    };
    $scope.statistics();

    $scope.setPlaceValue = function (newPlace) {
        $scope.place = newPlace;
    };

    $scope.hidePlaceSelector = function () {
        setTimeout(function () {
            $scope.showPlaceSelector = false;
        }, 30);
    };

    document.focusChangeCountdown = 0;
    checkFocusChange();

    $scope.resetCountdown = function () {
        document.focusChangeCountdown = 5;
    };

    $scope.books = [
        {data: {title: "Beisbielbuch", year: 2011}},
        {data: {title: "Buch 2", year: 1911}},
        {data: {title: "Buch 3", year: 1913}},
        {data: {title: "Buch 4", year: 1914}},
        {data: {title: "Buch 5", year: 1915}},
        {data: {title: "Buch 6", year: 1916}},
        {data: {title: "Buch 7", year: 1917}},
        {data: {title: "Buch 8", year: 1918}}
    ];

    $scope.savedSuccessfully = false;

    $scope.dataInput = function () {
        Backend.searchOrStore($scope.input, $scope.place, $scope.books).success(function (data) {
            $scope.books = angular.fromJson(data)['index'];
            angular.forEach($scope.books, function (book) {
                book['time'] = new Date(book['time'])
                if (!book['data']['title']) {
                    if (book['data']['isbn']) {
                        book['data']['title'] = book['data']['isbn'];
                    } else {
                        book['data']['title'] = book['data']['ean'];
                    }
                }
                if (!book['data']['year']) {
                    book['data']['year'] = "gespeichert " + book['time'].getFullYear();
                }
            });
            $scope.statistics();
        });
    };

    $scope.input = "";
    $scope.dataInput();

    $scope.saveBook = function (book) {
        Backend.update(book).success(function (data) {
            $scope.statistics();
        });
    };
}

bibCtrl.$inject = ['$scope', 'Backend', '$routeParams'];
