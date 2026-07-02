/** @odoo-module */

import publicWidget from '@web/legacy/js/public/public_widget';
import { jsonrpc } from '@web/core/network/rpc_service';

publicWidget.registry.VehiclePortal = publicWidget.Widget.extend({
    selector: '#wrapwrap',
    events: {
        'change #brand_select': '_onChangeBrand',
    },

    /**
     * @override
     */
    start: function () {
        return this._super.apply(this, arguments);
    },

    _onChangeBrand: async function (ev) {
        const brandId = ev.currentTarget.value;
        const modelSelect = this.el.querySelector('#model_select');

        if (brandId) {
            const data = await jsonrpc('/get_models_by_brand', { brand_id: brandId });
            modelSelect.innerHTML = '<option value="">Select Model</option>';
            data.forEach(function (m) {
                modelSelect.innerHTML += `<option value="${m.id}">${m.name}</option>`;
            });
        } else {
            modelSelect.innerHTML = '<option value="">Select Model</option>';
        }
    },
});
