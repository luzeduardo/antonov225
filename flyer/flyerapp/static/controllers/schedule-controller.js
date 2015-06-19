(function() {
 'use strict';
 angular.module('app').controller('ScheduleController', function($scope, $http) {
	$scope.pedido = {
 	    itens: [],
        total: function() {
            var total = 0;
            angular.forEach($scope.pedido.itens, function(item) {
                total += item.qtd * item.preco;
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
            $scope.pedido.itens = data;
        })
	}

	$scope.deleteSchedule = function(index) {
        $http.post('/delete/' + index).success(function(data) {
            $scope.pedido.itens = data;
        })
	}
 });
})();