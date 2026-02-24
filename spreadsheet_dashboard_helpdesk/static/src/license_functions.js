/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import * as spreadsheet from "@odoo/o-spreadsheet";

const { functionRegistry } = spreadsheet.registries;
const { arg, toNumber, toString } = spreadsheet.helpers;

functionRegistry.add("ODOO.LICENSE.COUNT", {
    description: _t("Get the total count of licenses."),
    args: [
        arg("dealer_id (number, optional)", _t("Dealer ID to filter")),
        arg("state (string, optional)", _t("License state to filter")),
        arg("program_id (number, optional)", _t("Program ID to filter")),
        arg("date_from (string, optional)", _t("Start date (YYYY-MM-DD)")),
        arg("date_to (string, optional)", _t("End date (YYYY-MM-DD)")),
    ],
    category: "Odoo",
    returns: ["NUMBER"],
    compute: function (
        dealerId = { value: null },
        stateArg = { value: "all" },
        programId = { value: null },
        dateFrom = { value: null },
        dateTo = { value: null }
    ) {
        const args = {
            domain: [],
            state: stateArg.value ? toString(stateArg) : 'all',
            dealer_id: dealerId.value ? toNumber(dealerId, this.locale) : null,
            program_id: programId.value ? toNumber(programId, this.locale) : null,
            date_from: dateFrom.value ? toString(dateFrom) : null,
            date_to: dateTo.value ? toString(dateTo) : null,
        };
        return this.getters.getLicenseCount(args);
    },
});

functionRegistry.add("ODOO.LICENSE.ACTIVE", {
    description: _t("Count active licenses."),
    args: [
        arg("dealer_id (number, optional)", _t("Dealer ID to filter")),
        arg("program_id (number, optional)", _t("Program ID to filter")),
        arg("date_from (string, optional)", _t("Start date (YYYY-MM-DD)")),
        arg("date_to (string, optional)", _t("End date (YYYY-MM-DD)")),
    ],
    category: "Odoo",
    returns: ["NUMBER"],
    compute: function (
        dealerId = { value: null },
        programId = { value: null },
        dateFrom = { value: null },
        dateTo = { value: null }
    ) {
        const args = {
            domain: [],
            state: 'active',
            dealer_id: dealerId.value ? toNumber(dealerId, this.locale) : null,
            program_id: programId.value ? toNumber(programId, this.locale) : null,
            date_from: dateFrom.value ? toString(dateFrom) : null,
            date_to: dateTo.value ? toString(dateTo) : null,
        };
        return this.getters.getLicenseCount(args);
    },
});

functionRegistry.add("ODOO.LICENSE.EXPIRED", {
    description: _t("Count expired licenses."),
    args: [
        arg("dealer_id (number, optional)", _t("Dealer ID to filter")),
        arg("program_id (number, optional)", _t("Program ID to filter")),
        arg("date_from (string, optional)", _t("Start date (YYYY-MM-DD)")),
        arg("date_to (string, optional)", _t("End date (YYYY-MM-DD)")),
    ],
    category: "Odoo",
    returns: ["NUMBER"],
    compute: function (
        dealerId = { value: null },
        programId = { value: null },
        dateFrom = { value: null },
        dateTo = { value: null }
    ) {
        const args = {
            domain: [],
            state: 'expired',
            dealer_id: dealerId.value ? toNumber(dealerId, this.locale) : null,
            program_id: programId.value ? toNumber(programId, this.locale) : null,
            date_from: dateFrom.value ? toString(dateFrom) : null,
            date_to: dateTo.value ? toString(dateTo) : null,
        };
        return this.getters.getLicenseCount(args);
    },
});

functionRegistry.add("ODOO.LICENSE.EXPIRING", {
    description: _t("Count licenses that are expiring soon."),
    args: [
        arg("dealer_id (number, optional)", _t("Dealer ID to filter")),
        arg("program_id (number, optional)", _t("Program ID to filter")),
        arg("date_from (string, optional)", _t("Start date (YYYY-MM-DD)")),
        arg("date_to (string, optional)", _t("End date (YYYY-MM-DD)")),
    ],
    category: "Odoo",
    returns: ["NUMBER"],
    compute: function (
        dealerId = { value: null },
        programId = { value: null },
        dateFrom = { value: null },
        dateTo = { value: null }
    ) {
        const args = {
            domain: [],
            state: 'expiring',
            dealer_id: dealerId.value ? toNumber(dealerId, this.locale) : null,
            program_id: programId.value ? toNumber(programId, this.locale) : null,
            date_from: dateFrom.value ? toString(dateFrom) : null,
            date_to: dateTo.value ? toString(dateTo) : null,
        };
        return this.getters.getLicenseCount(args);
    },
});

functionRegistry.add("ODOO.LICENSE.TOP_DEALER_NAME", {
    description: _t("Return the dealer name for the given ranking based on license count."),
    args: [
        arg("rank (number)", _t("Ranking position starting from 1")),
        arg("state (string, optional)", _t("License state to filter (default: active)")),
        arg("program_id (number, optional)", _t("Program ID to filter")),
        arg("date_from (string, optional)", _t("Start date (YYYY-MM-DD)")),
        arg("date_to (string, optional)", _t("End date (YYYY-MM-DD)")),
    ],
    category: "Odoo",
    returns: ["TEXT"],
    compute: function (rankArg, stateArg = { value: "active" }, programIdArg = { value: null }, dateFrom = { value: null }, dateTo = { value: null }) {
        const parsedRank = toNumber(rankArg, this.locale);
        const rank = Math.max(1, Number.isFinite(parsedRank) ? parsedRank : 1);
        const state = stateArg.value ? toString(stateArg) : "active";
        const programId = programIdArg.value ? toNumber(programIdArg, this.locale) : null;

        const response = this.getters.getLicenseTopDealers({
            domain: [],
            state,
            program_id: programId,
            limit: rank,
            date_from: dateFrom.value ? toString(dateFrom) : null,
            date_to: dateTo.value ? toString(dateTo) : null,
        });

        const record = response?.[rank - 1];
        return record?.dealer_name || "";
    },
});

functionRegistry.add("ODOO.LICENSE.TOP_DEALER_COUNT", {
    description: _t("Return the license count for the dealer at the given ranking."),
    args: [
        arg("rank (number)", _t("Ranking position starting from 1")),
        arg("state (string, optional)", _t("License state to filter (default: active)")),
        arg("program_id (number, optional)", _t("Program ID to filter")),
        arg("date_from (string, optional)", _t("Start date (YYYY-MM-DD)")),
        arg("date_to (string, optional)", _t("End date (YYYY-MM-DD)")),
    ],
    category: "Odoo",
    returns: ["NUMBER"],
    compute: function (rankArg, stateArg = { value: "active" }, programIdArg = { value: null }, dateFrom = { value: null }, dateTo = { value: null }) {
        const parsedRank = toNumber(rankArg, this.locale);
        const rank = Math.max(1, Number.isFinite(parsedRank) ? parsedRank : 1);
        const state = stateArg.value ? toString(stateArg) : "active";
        const programId = programIdArg.value ? toNumber(programIdArg, this.locale) : null;

        const response = this.getters.getLicenseTopDealers({
            domain: [],
            state,
            program_id: programId,
            limit: rank,
            date_from: dateFrom.value ? toString(dateFrom) : null,
            date_to: dateTo.value ? toString(dateTo) : null,
        });

        const record = response?.[rank - 1];
        return record?.count || 0;
    },
});
