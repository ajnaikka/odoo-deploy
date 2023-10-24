// bi_advance_branch_pos js
odoo.define('bi_advance_branch_pos.pos', function(require) {
	"use strict";

	const { PosGlobalState, Order, Orderline, Payment } = require('point_of_sale.models');
	const Registries = require('point_of_sale.Registries');


	const PosHomePosGlobalState = (PosGlobalState) => class PosHomePosGlobalState extends PosGlobalState {
		async _processData(loadedData) {
			await super._processData(...arguments);
			console.log("loadedData--------------",loadedData)
		}
		
	}
	Registries.Model.extend(PosGlobalState, PosHomePosGlobalState);


	

});
