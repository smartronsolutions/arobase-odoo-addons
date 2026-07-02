/* @odoo-module */

import { Attachment } from "@mail/core/common/attachment_model";
import { patch } from "@web/core/utils/patch";

patch(Attachment.prototype, {
    update(data) {
        super.update(...arguments);
        if (data["enable_digitizer"]) {
            this.enable_digitizer = data["enable_digitizer"];
        }
    },
});
