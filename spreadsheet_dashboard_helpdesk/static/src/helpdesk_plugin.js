/** @odoo-module */

import { OdooUIPlugin } from "@spreadsheet/plugins";
import * as spreadsheet from "@odoo/o-spreadsheet";

const { featurePluginRegistry } = spreadsheet.registries;

export class HelpdeskPlugin extends OdooUIPlugin {
    static getters = [
        "getHelpdeskTicketCount",
        "getHelpdeskAvgCloseTime",
        "getHelpdeskTopCustomers",
    ];

    constructor(config) {
        super(config);
        this._serverData = config.custom.odooDataProvider?.serverData;
    }

    get serverData() {
        if (!this._serverData) {
            throw new Error("serverData is not defined");
        }
        return this._serverData;
    }

    getHelpdeskTicketCount(args) {
        return this.serverData.batch.get(
            "helpdesk.ticket",
            "spreadsheet_fetch_ticket_count",
            args
        ).count;
    }

    getHelpdeskAvgCloseTime(args) {
        return this.serverData.batch.get(
            "helpdesk.ticket",
            "spreadsheet_fetch_avg_close_time",
            args
        ).avg_days;
    }

    getHelpdeskTopCustomers(args) {
        return this.serverData.batch.get(
            "helpdesk.ticket",
            "spreadsheet_fetch_top_customers",
            args
        ).records;
    }
}

featurePluginRegistry.add("odooHelpdeskFunctions", HelpdeskPlugin);
