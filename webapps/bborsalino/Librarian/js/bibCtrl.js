'use strict';

function checkFocusChange() {
    if (document.focusChangeCountdown <= 0) {
        document.getElementById('search').focus();
        document.focusChangeCountdown = 3;
    } else {
        document.focusChangeCountdown -= 1;
    }
    setTimeout(checkFocusChange, 1000);
}

function copyBook(book) {
    var copiedBook = {};
    angular.forEach(book, function(value, key) {
        if (typeof copiedBook[key] === 'object') {
            copiedBook[key] = {};
            angular.forEach(book['data'], function(subvalue, subkey) {
                copiedBook['data'][subkey] = subvalue;
            });
        } else {
            copiedBook[key] = value;
        }
    });
    return copiedBook;
}

function removeEmergencyFields(book) {
    if (book['data']['title'] == book['data']['isbn'] ||
        book['data']['title'] == book['data']['ean']) {
        delete book['data']['title'];
    }
    if (typeof book['data']['year'] === 'string' &&
        book['data']['year'].substr(0, 12) == "gespeichert ") {
        delete book['data']['year'];
    }
    return book;
}

function removeFrontendFields(book) {
    delete book['showSettings'];
    delete book['editMode'];
    return book;
}

bibApp.controller('bibCtrl',
    function ($scope, Backend, Authenticate, $routeParams) {
    // Function Definitions
    $scope.statistics = function () {
        Backend.statistics(Authenticate.getToken()).success(function (data) {
            var statistics = angular.fromJson(data);
            $scope.bookCount  = statistics['book_count'];
            $scope.placesUsed = statistics['places_used'];
            $scope.lentCount  = statistics['lent_count'];
        })
    };

    $scope.resetCountdown = function () {
        document.focusChangeCountdown = 5;
    };

    $scope.dataInput = function () {
        var searchOrStoreResponse = Backend.searchOrStore(
                Authenticate.getToken(),
                $scope.input,
                $scope.place);
        searchOrStoreResponse['promise'].success(function (data) {
            console.log(data);
            $scope.books = angular.fromJson(data)['index'];
            if ($scope.books.length <= 0 && searchOrStoreResponse['savePossible']) {
                $scope.lastSaveInput = $scope.input;
                setTimeout(function () {
                    $scope.input = $scope.lastSaveInput;
                    $scope.dataInput();
                }, 10);
            }
            var incompleteBooks = false;
            angular.forEach($scope.books, function (book) {
                book['showSettings'] = false;
                book['editMode'] = false;
                book['time'] = new Date(book['time']);
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
                if (!book['data']['author']) {
                    incompleteBooks = true;
                }
            });
            if (incompleteBooks) {
                setTimeout(function () {
                    if (searchOrStoreResponse['savePossible']) {
                        console.log("Looking for new data of incomplete books.");
                        $scope.input = $scope.lastSaveInput;
                        $scope.dataInput();
                    }
                }, 3000);
            }
            if (searchOrStoreResponse['savePossible']) {
                $scope.input = "";
                $scope.statistics();
            }
        });
    };

    $scope.setPlaceValue = function (newPlace) {
        $scope.place = newPlace;
    };

    $scope.hidePlaceSelector = function () {
        setTimeout(function () {
            $scope.showPlaceSelector = false;
        }, 30);
    };

    $scope.saveBook = function (book) {
        var sendBook = copyBook(book);
        sendBook = removeEmergencyFields(sendBook);
        sendBook = removeFrontendFields(sendBook);
        // save the preparated book
        Backend.update(Authenticate.getToken(), sendBook).success(function (data) {
            $scope.statistics();
        });
    };

    $scope.duplicateBook = function (book) {
        var duplicate = copyBook(book);
        duplicate = removeEmergencyFields(duplicate);
        duplicate = removeFrontendFields(duplicate);
        Backend.duplicate(Authenticate.getToken(), duplicate).success(function (data) {
            duplicate['time'] = Date.now();
            delete duplicate['_id'];
            delete duplicate['$$hashKey'];
            console.log(duplicate);
            $scope.books.push(duplicate);
            $scope.statistics();
        });
    };

    $scope.removeBook = function (book) {
        Backend.remove(Authenticate.getToken(), book).success(function (data) {
            if (data['success']) {
                for (var i = 0; i < $scope.books.length; i++) {
                    if ($scope.books[i]['_id'] === book['_id']) {
                        $scope.books.splice(i, 1);
                    }
                }
            }
        });
    };

    $scope.hasID = function (book) {
        return book['_id'];
    };

    // Initialization
    $scope.showPlaceSelector = false;
    $scope.bookCount  = 0;
    $scope.placesUsed = ['Arbeitszimmer', 'Wohnzimmer'];
    $scope.lentCount  = 0;
    $scope.books = [];
    $scope.savedSuccessfully = false;
    $scope.input = "";
    $scope.lastSaveInput = "";
    $scope.saved = false;
    document.focusChangeCountdown = 0;
    setTimeout(checkFocusChange, 100);
    $scope.dataInput();
    $scope.statistics();
});
