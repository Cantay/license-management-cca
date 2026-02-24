/** @odoo-module */

import { OdooUIPlugin } from "@spreadsheet/plugins";
import * as spreadsheet from "@odoo/o-spreadsheet";

const { featurePluginRegistry } = spreadsheet.registries;

export class LicensePlugin extends OdooUIPlugin {
    static getters = ["getLicenseCount", "getLicenseTopDealers"];

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

    getLicenseCount(args) {
        return this.serverData.batch.get(
            "license.subscription",
            "spreadsheet_fetch_license_count",
            args
        ).count;
    }

    getLicenseTopDealers(args) {
        return this.serverData.batch.get(
            "license.subscription",
            "spreadsheet_fetch_top_dealers",
            args
        ).records;
    }
}

featurePluginRegistry.add("odooLicenseFunctions", LicensePlugin);
