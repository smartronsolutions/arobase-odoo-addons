/* @odoo-module */

import { AttachmentList } from "@mail/core/common/attachment_list";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";

patch(AttachmentList.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
    },

    async onClickReload(attachment) {
        const orm = this.orm
        await orm.call('ir.attachment','create_document_from_attachment',[[attachment.id]]);

        window.location.reload();

    }
});
