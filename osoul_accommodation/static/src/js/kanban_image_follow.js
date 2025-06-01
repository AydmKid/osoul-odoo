odoo.define('osoul_accommodation.image_tilt', function(require) {
    "use strict";
    
    var KanbanRecord = require('web.KanbanRecord');
    var FormView = require('web.FormView');
    
    var tiltEffect = {
        init: function() {
            this.animationEnabled = true;
            this.originalSrc = '/osoul_accommodation/static/src/img/eye.png'; // Replace with the path to your original image
            this.newSrc = '/osoul_accommodation/static/src/img/eye-close.png'; // Replace with the path to your new image
            console.log("Tilt effect initialized");
        },

        _onMouseMove: function(event) {
            if (!this.animationEnabled) return;

            var $image = $('.o_kanban_image_inner_pic');
            if (!$image.length) {
                console.log("No image found for tilt effect");
                return;
            }
            var mouseX = event.pageX;
            var mouseY = event.pageY;
            var centerX = $image.offset().left + $image.width() / 2;
            var centerY = $image.offset().top + $image.height() / 2;
            var deltaX = mouseX - centerX;
            var deltaY = mouseY - centerY;
            var percentX = deltaX / ($image.width() / 2);
            var percentY = deltaY / ($image.height() / 2);
            var rotateX = percentY * 2; // Adjust the multiplier for more/less tilt
            var rotateY = -percentX * 2; // Adjust the multiplier for more/less tilt

            $image.css({
                'transform': 'rotateX(' + rotateX + 'deg) rotateY(' + rotateY + 'deg)',
            });
        },

        _onMouseLeave: function(event) {
            if (!this.animationEnabled) return;

            var $image = $('.o_kanban_image_inner_pic');
            $image.css({
                'transform': '',
            });
        },

        _onImageClick: function(event) {
            var $image = $(event.currentTarget);
            console.log("Image clicked");
            if ($image.attr('src') === this.originalSrc) {
                $image.attr('src', this.newSrc);
                console.log("Changed to new image");
                this.animationEnabled = false;
            } else {
                $image.attr('src', this.originalSrc);
                console.log("Restored to original image");
                this.animationEnabled = true;
            }
        },
    };

    tiltEffect.init();

    function bindEvents() {
        if (!tiltEffect.eventsBound) {
            $(document).on('mousemove', tiltEffect._onMouseMove.bind(tiltEffect));
            $(document).on('mouseleave', tiltEffect._onMouseLeave.bind(tiltEffect));
            $(document).on('click', '.o_kanban_image_inner_pic', tiltEffect._onImageClick.bind(tiltEffect));
            tiltEffect.eventsBound = true;
            console.log("Events bound");
        }
    }

    function unbindEvents() {
        if (tiltEffect.eventsBound) {
            $(document).off('mousemove', tiltEffect._onMouseMove.bind(tiltEffect));
            $(document).off('mouseleave', tiltEffect._onMouseLeave.bind(tiltEffect));
            $(document).off('click', '.o_kanban_image_inner_pic', tiltEffect._onImageClick.bind(tiltEffect));
            tiltEffect.eventsBound = false;
            console.log("Events unbound");
        }
    }

    KanbanRecord.include({
        start: function () {
            this._super.apply(this, arguments);
            setTimeout(bindEvents, 100); // Adding a small delay
            console.log("KanbanRecord started");
        },

        destroy: function () {
            unbindEvents();
            this._super.apply(this, arguments);
            console.log("KanbanRecord destroyed");
        },
    });

    FormView.include({
        start: function () {
            this._super.apply(this, arguments);
            setTimeout(bindEvents, 100); // Adding a small delay
            console.log("FormView started");
        },

        destroy: function () {
            unbindEvents();
            this._super.apply(this, arguments);
            console.log("FormView destroyed");
        },
    });
});


