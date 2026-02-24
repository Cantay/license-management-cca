/** @odoo-module **/

import { Component, useState, onWillStart, xml } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class LicenseDashboard extends Component {
    static template = xml`
        <div class="o_license_dashboard">
            <div t-if="state.loading" class="text-center p-5">
                <i class="fa fa-spinner fa-spin fa-2x"/>
                <p>Loading dashboard...</p>
            </div>
            <div t-else="" class="container-fluid">
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="card bg-primary text-white">
                            <div class="card-body">
                                <h3><t t-esc="state.data.total_active || 0"/></h3>
                                <p>Total Active Licenses</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-warning text-white">
                            <div class="card-body">
                                <h3><t t-esc="state.data.expiring_30_days || 0"/></h3>
                                <p>Expiring in 30 Days</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-danger text-white">
                            <div class="card-body">
                                <h3><t t-esc="state.data.total_expired || 0"/></h3>
                                <p>Total Expired</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-success text-white">
                            <div class="card-body">
                                <h3><t t-esc="(state.data.total_revenue_active || 0)"/> ₺</h3>
                                <p>Active License Value</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header">
                                <h5>License Overview</h5>
                            </div>
                            <div class="card-body">
                                <p>Dashboard is working! Data loaded successfully.</p>
                                <p>You can extend this with charts and more detailed analytics.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            data: {},
            loading: true
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            const data = await this.orm.call(
                "license.subscription",
                "get_license_dashboard_data",
                []
            );
            this.state.data = data;
            this.state.loading = false;
        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.state.data = {
                total_active: 0,
                expiring_30_days: 0,
                total_expired: 0,
                total_revenue_active: 0
            };
            this.state.loading = false;
        }
    }
}

registry.category("actions").add("license_dashboard", LicenseDashboard);
