'use strict';
/*
 * This module is licensed under the MIT License (MIT).
 *
 * Copyright (c) 2014 Johannes Merkert <jonny@pinae.net>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

var ui = angular.module('pinytoUi', []);

ui.directive('pinytoButton', function () {
    return {
        restrict: 'E',
        transclude: true,
        scope: {
            color: '@'
        },
        link: function ($scope, element, attrs) {
            element[0].firstChild.style.boxShadow = '1px 2px 5px rgba(0, 0, 0, 0.5)';
            element[0].firstChild.style.border = 'border: 0 solid black';
            element[0].firstChild.style.borderRadius = '3px';
            element[0].firstChild.style.cursor = 'pointer';
            element[0].firstChild.style.display = 'inline-block';
            element[0].firstChild.style.padding = '0';
            element[0].firstChild.style.margin = '0';
            element[0].firstChild.style.overflow = 'hidden';
            element[0].firstChild.style.zIndex = '0';
            element[0].firstChild.style.position = 'relative';
            element[0].firstChild.style.top = '0';
            element[0].firstChild.style.left = '0';
            element[0].firstChild.childNodes[0].style.width = '0';
            element[0].firstChild.childNodes[0].style.height = '0';
            element[0].firstChild.childNodes[0].style.overflow = 'visible';
            element[0].firstChild.childNodes[1].style.backgroundColor = 'rgba(255, 255, 255, 0)';
            element[0].firstChild.childNodes[1].style.zIndex = '1';
            element[0].firstChild.childNodes[1].style.padding = '6px 15px';
            element[0].firstChild.childNodes[1].style.margin = '0';
            $scope.animationBlobs = [];
            element.bind('mouseenter', function () {
                element[0].firstChild.childNodes[1].style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
            });
            element.bind('mouseleave', function () {
                element[0].firstChild.style.boxShadow = '1px 2px 5px rgba(0, 0, 0, 0.5)';
                element[0].firstChild.style.top = '0';
                element[0].firstChild.style.left = '0';
                element[0].firstChild.childNodes[1].style.backgroundColor = 'rgba(255, 255, 255, 0)';
            });
            element.bind('mousedown', function ($event) {
                $event.preventDefault();
                var posX = $event.offsetX;
                if (!posX) { posX = $event.layerX; }
                var posY = $event.offsetY;
                if (!posY) { posY = $event.layerY; }
                var blob = {
                    element: document.createElement('DIV'),
                    position: [posX, posY],
                    size: 0
                };
                blob.element.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
                blob.element.style.position = 'relative';
                blob.element.style.zIndex = '2';
                $scope.animationBlobs.push(blob);
                element[0].firstChild.childNodes[0].appendChild(blob.element);
                element[0].firstChild.style.boxShadow = '0 1px 4px rgba(0, 0, 0, 0.5)';
                element[0].firstChild.style.top = '1px';
                element[0].firstChild.style.left = '1px';
                $scope.animateBlobs();
            });
            element.bind('mouseup', function () {
                element[0].firstChild.style.boxShadow = '1px 2px 5px rgba(0, 0, 0, 0.5)';
                element[0].firstChild.style.top = '0';
                element[0].firstChild.style.left = '0';
            });
            attrs.$observe('color', function () {
                element[0].firstChild.style.backgroundColor = $scope.color;
            });
        },
        controller: function ($scope, $timeout) {
            $scope.animateBlobs = function () {
                var i = 0;
                while (i < $scope.animationBlobs.length) {
                    var blob = $scope.animationBlobs[i];
                    if (blob.size < 100) {
                        blob.size = blob.size + (100-blob.size*0.7)/5;
                        blob.element.style.width = blob.size + 'px';
                        blob.element.style.height = blob.size + 'px';
                        blob.element.style.borderRadius = (blob.size / 2) + 'px';
                        blob.element.style.opacity = 10 / blob.size;
                        blob.element.style.left = (blob.position[0] - blob.size / 2) + 'px';
                        blob.element.style.top = (blob.position[1] - blob.size / 2) + 'px';
                        i++;
                    } else {
                        blob.element.parentNode.removeChild(blob.element);
                        $scope.animationBlobs.splice(i, 1);
                    }
                }
                if ($scope.animationBlobs.length > 0) {
                    $timeout($scope.animateBlobs, 28);
                }
            };
        },
        template: '<div><div></div><div style="z-index: 4;"><ng-transclude></ng-transclude></div></div>'
    };
});