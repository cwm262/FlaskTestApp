angular.module('myApp').controller('navController',
    ['$scope', '$location', 'AuthService',
        function ($scope, $location, AuthService) {

            $scope.isActive = function(viewLocation){
                return viewLocation === $location.path();
            };

            $scope.goToStudents = function () {
                $location.path('/students');
            };

            $scope.goToHome = function () {
                $location.path('/');
            };

            $scope.logout = function () {
                // call logout from service
                AuthService.logout()
                    .then(function () {
                        $location.path('/login');
                    });
            };
        }]);

angular.module('myApp').controller('loginController',
    ['$scope', '$location', 'AuthService',
        function ($scope, $location, AuthService) {

            if(AuthService.isLoggedIn()){
                $location.path('/');
            }

            $scope.goToRegister = function () {
                $location.path('/register');
            };

            $scope.login = function () {

                // initial values
                $scope.error = false;
                $scope.disabled = true;

                // call login from service
                AuthService.login($scope.loginForm.username, $scope.loginForm.password)
                // handle success
                    .then(function () {
                        $location.path('/');
                        $scope.disabled = false;
                        $scope.loginForm = {};
                    })
                    // handle error
                    .catch(function () {
                        $scope.error = true;
                        $scope.errorMessage = "Invalid username and/or password";
                        $scope.disabled = false;
                        $scope.loginForm = {};
                    });

            };

        }]);

angular.module('myApp').controller('registerController',
    ['$scope', '$location', 'AuthService',
        function ($scope, $location, AuthService) {

            if(AuthService.isLoggedIn()){
                $location.path('/');
            }

            $scope.register = function () {

                // initial values
                $scope.error = false;
                $scope.disabled = true;

                // call register from service
                AuthService.register($scope.registerForm.username,
                    $scope.registerForm.password)
                // handle success
                    .then(function () {
                        $location.path('/login');
                        $scope.disabled = false;
                        $scope.registerForm = {};
                    })
                    // handle error
                    .catch(function () {
                        $scope.error = true;
                        $scope.errorMessage = "Something went wrong!";
                        $scope.disabled = false;
                        $scope.registerForm = {};
                    });

            };

        }]);

angular.module('myApp').controller('studentsController',
    ['$scope', '$http', '$location',
        function ($scope, $http, $location) {

            $scope.pageSize = 10;
            $scope.sortType = 'pawprint';
            $scope.sortReverse = false;

            $http.get('/api/students')
                .success(function (data) {
                    $scope.students = data.objects;
                });

            $scope.viewStudentPage = function (paw) {
                $location.path("/students/" + paw);
            }
        }]);

angular.module('myApp').controller('viewStudentController',
    ['$scope', '$http', '$location', '$routeParams',
        function ($scope, $http, $location, $routeParams) {
            $scope.pageSize = 5;
            $scope.paw = $routeParams.paw;
            $http.get('/api/students/' + $routeParams.paw).success(function (data) {
                $scope.studentData = data;
            });
            var filters = [{"name": "student_id", "op": "like", "val": $routeParams.paw}];
            $http.get('/api/points', {
                params: {
                    q: JSON.stringify({"filters": filters})
                }
            }).success(function (data) {
                $scope.studentPoints = data.objects;
            });
            $scope.punish = function(id){
                $location.path('/students/'+id+'/punish');    
            };
        }
    ]);

angular.module('myApp').controller('punishController',
    ['$scope', '$http', '$location', '$routeParams',
        function ($scope, $http, $location, $routeParams) {
            $scope.paw = $routeParams.paw;
            $http.get('/api/students/' + $routeParams.paw).success(function (data) {
                $scope.studentData = data;
            });
            $scope.whyPunish = '';
            $http.get('/api/infractionTypes').success(function(data){
                $scope.infractions = data.objects;
            });
            $scope.selected = '';
        }
    ]);