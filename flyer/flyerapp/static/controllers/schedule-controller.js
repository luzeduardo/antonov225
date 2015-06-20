(function() {
 'use strict';
 angular.module('app').controller('ScheduleController', function($scope, $http) {

     $http.get('/schedules/').success(function(data) {
        console.log(data);
        $scope.schedule.itens = data;
     })

     $scope.schedule = {
        total: function() {
            var total = 0;
            angular.forEach($scope.schedule.itens, function(item) {
                total += item.price;
            })
            return total;
        }
	}

	$scope.addSchedule = function() {
        var produto = {
            descricao: 'A guerra dos tronos - The Board Game',
            preco: 150.0,
            qtd: 1
        }

        $http.post('/add/', {item: produto}).success(function(data) {
            $scope.schedule.itens = data;
        })
	}

	$scope.deleteSchedule = function(index) {
        $http.post('/delete/' + index).success(function(data) {
            $scope.schedule.itens = data;
        })
	}

    $scope.getSchedule = function(index) {
        $http.get('/schedule/' + index).success(function(data) {
            $scope.schedule.itens = data;
        })
	}

 });
})();