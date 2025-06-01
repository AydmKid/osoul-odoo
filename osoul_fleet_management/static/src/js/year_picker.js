odoo.define('osoul_fleet.year_picker', function (require) {
    "use strict";

    var fieldRegistry = require('web.field_registry');
    var FieldChar = require('web.basic_fields').FieldChar;

    var YearPicker = FieldChar.extend({
        start: function () {
            this.$input.datepicker({
                format: "yyyy",
                viewMode: "years",
                minViewMode: "years"
            });
            return this._super.apply(this, arguments);
        },
    });

    fieldRegistry.add('year_picker', YearPicker);
});