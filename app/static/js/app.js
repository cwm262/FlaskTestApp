var myApp = angular.module('myApp', ['ngRoute', 'ngResource', 'angularUtils.directives.dirPagination']);

myApp.config(function ($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: 'static/partials/home.html',
            access: {restricted: true}
        })
        .when('/login', {
            templateUrl: 'static/partials/login.html',
            controller: 'loginController',
            access: {restricted: false}
        })
        .when('/register', {
            templateUrl: 'static/partials/register.html',
            controller: 'registerController',
            access: {restricted: false}
        })
        .when('/students', {
            templateUrl: 'static/partials/students.html',
            controller: 'studentsController',
            access: {restricted: true}
        })
        .when('/students/:paw', {
            templateUrl: 'static/partials/viewStudent.html',
            controller: 'viewStudentController',
            access: {restricted: true}
        })
        .when('/students/:paw/punish', {
            templateUrl: 'static/partials/punish.html',
            controller: 'punishController',
            access: {restricted: true}
        })
        .when('/two', {
            template: '<h1>This is page two!</h1>',
            access: {restricted: false}
        })
        .otherwise({
            redirectTo: '/'
        });
});

myApp.run(function ($rootScope, $location, $route, AuthService) {
    $rootScope.$on('$routeChangeStart',
        function (event, next, current) {
            AuthService.getUserStatus()
                .then(function () {
                    if (next.access.restricted && !AuthService.isLoggedIn()) {
                        $location.path('/login');
                        $route.reload();
                    }
                });
        });
});
