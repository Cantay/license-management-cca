/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import * as spreadsheet from "@odoo/o-spreadsheet";

const { functionRegistry } = spreadsheet.registries;
const { arg, toNumber, toString, toBoolean } = spreadsheet.helpers;

functionRegistry.add("ODOO.HELPDESK.COUNT", {
    description: _t("Get the count of helpdesk tickets based on criteria."),
    args: [
        arg("team_id (number, optional)", _t("Team ID to filter")),
        arg("stage_id (number, optional)", _t("Stage ID to filter")),
        arg("user_id (number, optional)", _t("Assigned user ID to filter")),
        arg("priority (string, optional)", _t("Priority: 0=Low, 1=Medium, 2=High, 3=Very High")),
        arg("date_from (string, optional)", _t("Start date (YYYY-MM-DD)")),
        arg("date_to (string, optional)", _t("End date (YYYY-MM-DD)")),
    ],
    category: "Odoo",
    returns: ["NUMBER"],
    compute: function (
        teamId = { value: null },
        stageId = { value: null },
        userId = { value: null },
        priority = { value: null },
        dateFrom = { value: null },
        dateTo = { value: null }
    ) {
        const args = {
            domain: [],
            team_id: teamId.value ? toNumber(teamId, this.locale) : null,
            stage_id: stageId.value ? toNumber(stageId, this.locale) : null,
            user_id: userId.value ? toNumber(userId, this.locale) : null,
            priority: priority.value ? toString(priority) : null,
            date_from: dateFrom.value ? toString(dateFrom) : null,
            date_to: dateTo.value ? toString(dateTo) : null,
        };

        return this.getters.getHelpdeskTicketCount(args);
    },
});

functionRegistry.add("ODOO.HELPDESK.OPEN", {
    description: _t("Count open (not closed) tickets."),
    args: [
        arg("team_id (number, optional)", _t("Team ID to filter")),
        arg("date_from (string, optional)", _t("Start date (YYYY-MM-DD)")),
        arg("date_to (string, optional)", _t("End date (YYYY-MM-DD)")),
    ],
    category: "Odoo",
    returns: ["NUMBER"],
    compute: function (teamId = { value: null }, dateFrom = { value: null }, dateTo = { value: null }) {
        const args = {
            domain: [],
            team_id: teamId.value ? toNumber(teamId, this.locale) : null,
            closed: false,
            date_from: dateFrom.value ? toString(dateFrom) : null,
            date_to: dateTo.value ? toString(dateTo) : null,
        };

        return this.getters.getHelpdeskTicketCount(args);
    },
});

functionRegistry.add("ODOO.HELPDESK.CLOSED", {
    description: _t("Count closed tickets."),
    args: [
        arg("team_id (number, optional)", _t("Team ID to filter")),
        arg("date_from (string, optional)", _t("Start date (YYYY-MM-DD)")),
        arg("date_to (string, optional)", _t("End date (YYYY-MM-DD)")),
    ],
    category: "Odoo",
    returns: ["NUMBER"],
    compute: function (teamId = { value: null }, dateFrom = { value: null }, dateTo = { value: null }) {
        const args = {
            domain: [],
            team_id: teamId.value ? toNumber(teamId, this.locale) : null,
            closed: true,
            date_from: dateFrom.value ? toString(dateFrom) : null,
            date_to: dateTo.value ? toString(dateTo) : null,
        };

        return this.getters.getHelpdeskTicketCount(args);
    },
});

functionRegistry.add("ODOO.HELPDESK.MAINTENANCE", {
    description: _t("Count tickets with active maintenance agreement."),
    args: [
        arg("team_id (number, optional)", _t("Team ID to filter")),
        arg("date_from (string, optional)", _t("Start date (YYYY-MM-DD)")),
        arg("date_to (string, optional)", _t("End date (YYYY-MM-DD)")),
    ],
    category: "Odoo",
    returns: ["NUMBER"],
    compute: function (teamId = { value: null }, dateFrom = { value: null }, dateTo = { value: null }) {
        const args = {
            domain: [],
            team_id: teamId.value ? toNumber(teamId, this.locale) : null,
            has_maintenance: true,
            date_from: dateFrom.value ? toString(dateFrom) : null,
            date_to: dateTo.value ? toString(dateTo) : null,
        };

        return this.getters.getHelpdeskTicketCount(args);
    },
});

functionRegistry.add("ODOO.HELPDESK.FREESUPPORT", {
    description: _t("Count tickets with active free support."),
    args: [
        arg("team_id (number, optional)", _t("Team ID to filter")),
        arg("date_from (string, optional)", _t("Start date (YYYY-MM-DD)")),
        arg("date_to (string, optional)", _t("End date (YYYY-MM-DD)")),
    ],
    category: "Odoo",
    returns: ["NUMBER"],
    compute: function (teamId = { value: null }, dateFrom = { value: null }, dateTo = { value: null }) {
        const args = {
            domain: [],
            team_id: teamId.value ? toNumber(teamId, this.locale) : null,
            has_free_support: true,
            date_from: dateFrom.value ? toString(dateFrom) : null,
            date_to: dateTo.value ? toString(dateTo) : null,
        };

        return this.getters.getHelpdeskTicketCount(args);
    },
});

functionRegistry.add("ODOO.HELPDESK.AVG.CLOSE", {
    description: _t("Get average days to close tickets."),
    args: [
        arg("team_id (number, optional)", _t("Team ID to filter")),
        arg("date_from (string, optional)", _t("Start date (YYYY-MM-DD)")),
        arg("date_to (string, optional)", _t("End date (YYYY-MM-DD)")),
    ],
    category: "Odoo",
    returns: ["NUMBER"],
    compute: function (teamId = { value: null }, dateFrom = { value: null }, dateTo = { value: null }) {
        const args = {
            team_id: teamId.value ? toNumber(teamId, this.locale) : null,
            date_from: dateFrom.value ? toString(dateFrom) : null,
            date_to: dateTo.value ? toString(dateTo) : null,
        };

        return {
            value: this.getters.getHelpdeskAvgCloseTime(args),
            format: "#,##0.00",
        };
    },
});

functionRegistry.add("ODOO.HELPDESK.TOP_CUSTOMER_NAME", {
    description: _t("Get the customer name by ranking based on ticket count."),
    args: [
        arg("rank (number)", _t("Ranking position starting from 1")),
        arg("team_id (number, optional)", _t("Team ID to filter")),
        arg("include_closed (boolean, optional)", _t("Include closed tickets (default: false)")),
        arg("date_from (string, optional)", _t("Start date (YYYY-MM-DD)")),
        arg("date_to (string, optional)", _t("End date (YYYY-MM-DD)")),
    ],
    category: "Odoo",
    returns: ["TEXT"],
    compute: function (rankArg, teamId = { value: null }, includeClosed = { value: false }, dateFrom = { value: null }, dateTo = { value: null }) {
        const parsedRank = toNumber(rankArg, this.locale);
        const rank = Math.max(1, Number.isFinite(parsedRank) ? parsedRank : 1);
        const includeClosedValue = includeClosed.value !== null && includeClosed.value !== undefined
            ? toBoolean(includeClosed)
            : false;
        const args = {
            domain: [],
            team_id: teamId.value ? toNumber(teamId, this.locale) : null,
            closed: includeClosedValue ? null : false,
            limit: rank,
            date_from: dateFrom.value ? toString(dateFrom) : null,
            date_to: dateTo.value ? toString(dateTo) : null,
        };

        const response = this.getters.getHelpdeskTopCustomers(args);
        const record = response?.[rank - 1];
        return record?.partner_name || "";
    },
});

functionRegistry.add("ODOO.HELPDESK.TOP_CUSTOMER_COUNT", {
    description: _t("Get the ticket count for the customer at the given ranking."),
    args: [
        arg("rank (number)", _t("Ranking position starting from 1")),
        arg("team_id (number, optional)", _t("Team ID to filter")),
        arg("include_closed (boolean, optional)", _t("Include closed tickets (default: false)")),
        arg("date_from (string, optional)", _t("Start date (YYYY-MM-DD)")),
        arg("date_to (string, optional)", _t("End date (YYYY-MM-DD)")),
    ],
    category: "Odoo",
    returns: ["NUMBER"],
    compute: function (rankArg, teamId = { value: null }, includeClosed = { value: false }, dateFrom = { value: null }, dateTo = { value: null }) {
        const parsedRank = toNumber(rankArg, this.locale);
        const rank = Math.max(1, Number.isFinite(parsedRank) ? parsedRank : 1);
        const includeClosedValue = includeClosed.value !== null && includeClosed.value !== undefined
            ? toBoolean(includeClosed)
            : false;
        const args = {
            domain: [],
            team_id: teamId.value ? toNumber(teamId, this.locale) : null,
            closed: includeClosedValue ? null : false,
            limit: rank,
            date_from: dateFrom.value ? toString(dateFrom) : null,
            date_to: dateTo.value ? toString(dateTo) : null,
        };

        const response = this.getters.getHelpdeskTopCustomers(args);
        const record = response?.[rank - 1];
        return record?.count || 0;
    },
});
