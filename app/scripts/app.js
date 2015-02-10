'use strict';

angular
  .module('tubeHighApp', [
    'ngRoute'
  ])
  .run(function ($rootScope, $route) {
    $rootScope.$on('$routeChangeSuccess', function (newVal, oldVal) {
      if (oldVal !== newVal) {
        document.title = $route.current.title;
      }
    })
  })
  .config(function ($routeProvider, $locationProvider) {
    $locationProvider.html5Mode(true);
    $routeProvider
      .when('/category/:categoryName/', {
        templateUrl: 'views/videos.html',
        controller: 'VidCtrl'
      })
      .when('/categories/', {
        title: 'Porn Categories | tubeHigh.com',
        templateUrl: 'views/categories.html',
        controller: 'CategoryCtrl'
      })
      .when('/', {
        title: 'Porn Categories | tubeHigh.com',
        templateUrl: 'views/categories.html',
        controller: 'CategoryCtrl'
      })
      .otherwise({
        redirectTo: '/'
      });
  })
  .controller('CategoryCtrl', function ($http) {
    var cat = this;
    // $http.get("http://54.148.153.124:8000/categories/")
    $http.get("http://localhost:8000/categories/")
      .success(function (response) {
        cat.category_objects = response;
      });
  })
  .controller('VidCtrl', function ($http, $routeParams) {
    var vid = this;
    document.title = $routeParams['categoryName'] + ' Tube | tubeHigh.com';
    // $http.get("http://54.148.153.124:8000/category/" + $routeParams['categoryName'] + '/')
    $http.get("http://localhost:8000/category/" + $routeParams['categoryName'] + '/')
      .success(function (response) {
        vid.video_objects = response;
      });
  });
