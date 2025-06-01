/** Static file: osoul_tickets/static/src/js/notification_listener.js **/
odoo.define('osoul_tickets.notification_listener', function (require) {
    "use strict";

    const core = require('web.core');
    const bus = require('bus.bus');
    bus.startPolling();  // Start the polling service if not started

    bus.on('notification', this, function (notifications) {
        notifications.forEach(function (notification) {
            if (notification[0] === 'display_notification') {
                const message = notification[1];
                core.bus.trigger('notification', {
                    title: message.title,
                    message: message.message,
                    type: message.type,
                    sticky: message.sticky,
                });
            }
        });
    });
});
