odoo.define('osoul_tickets.chat_button', function (require) {
    "use strict";

    const rpc = require('web.rpc');
    const Dialog = require('web.Dialog');

    $(document).on('click', '.o_employee_chat_btn', function (ev) {
        ev.preventDefault();
        
        const recordId = $(this).data('record-id');  // Capture the record ID
        console.log("Record ID for chat:", recordId); // Debugging log

        if (!recordId) {
            Dialog.alert(null, "Unable to find the record for chat.", {
                title: "Error",
            });
            return;
        }

        // Fetch the responsible user's partner ID
        rpc.query({
            model: 'ticket.job.order',
            method: 'get_responsible_user_partner',
            args: [recordId],
        }).then((partnerId) => {
            if (!partnerId) {
                Dialog.alert(null, "No responsible user found for chat.", {
                    title: "Error",
                });
                return;
            }

            // Send a chat message to the responsible user
            rpc.query({
                model: 'ticket.job.order',
                method: 'message_post',
                args: [recordId, {
                    body: "Chat message from Kanban view.",
                    partner_ids: [partnerId],
                }],
            }).then(() => {
                Dialog.alert(null, "Message sent to the responsible user!", {
                    title: "Success",
                });
            }).catch(() => {
                Dialog.alert(null, "Failed to send message.", {
                    title: "Error",
                });
            });
        }).catch(() => {
            Dialog.alert(null, "Failed to retrieve responsible user.", {
                title: "Error",
            });
        });
    });
});
