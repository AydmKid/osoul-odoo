odoo.define('osoul_fleet_management.tree_button_confirm', function (require) {
    "use strict";

    const ListController = require('web.ListController');
    const ListView = require('web.ListView');
    const viewRegistry = require('web.view_registry');

    // Extend ListController to add confirmation dialog
    const ConfirmableListController = ListController.extend({
        _onButtonClicked(event) {
            const self = this;

            // Get the button's `name` attribute
            const buttonName = event.target.getAttribute('name');
            let confirmMessage = null;

            // Check the button and set the appropriate confirmation message
            if (buttonName === 'action_active') {
                confirmMessage = "Are you sure you want to activate this vehicle?";
            } else if (buttonName === 'action_not_active') {
                confirmMessage = "Are you sure you want to deactivate this vehicle?";
            }

            // Show confirmation dialog
            if (confirmMessage) {
                if (confirm(confirmMessage)) {
                    return this._super.apply(this, arguments); // Proceed with the action
                } else {
                    event.preventDefault(); // Cancel the action
                }
            } else {
                return this._super.apply(this, arguments); // No confirmation needed
            }
        },
    });

    // Extend ListView to use the custom controller
    const ConfirmableListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: ConfirmableListController,
        }),
    });

    // Register the custom view type
    viewRegistry.add('confirmable_list', ConfirmableListView);
});