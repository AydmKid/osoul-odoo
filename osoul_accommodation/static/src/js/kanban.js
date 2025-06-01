odoo.define('osoul_accommodation.image_effect', function(require) {
    "use strict";
    
    var KanbanRecord = require('web.KanbanRecord');
    var FormView = require('web.FormView');
    
    var effects = ['bounce-effect', 'pulse-effect', 'rotate-effect'];
    var effectInterval = 6000; // Interval to switch effects

    var effectManager = {
        init: function() {
            this.currentEffectIndex = 0;
        },

        applyNextEffect: function() {
            var $icon = $('.o_kanban_image_inner_pic_kanban');
            var currentEffect = effects[this.currentEffectIndex];
            
            // Remove all effects
            $icon.removeClass(effects.join(' '));
            
            // Add the new effect
            $icon.addClass(currentEffect);
            
            // Update the effect index
            this.currentEffectIndex = (this.currentEffectIndex + 1) % effects.length;
        },

        startEffectRotation: function() {
            this.applyNextEffect();
            this.effectTimer = setInterval(this.applyNextEffect.bind(this), effectInterval);
        },

        stopEffectRotation: function() {
            clearInterval(this.effectTimer);
        }
    };

    effectManager.init();

    KanbanRecord.include({
        start: function () {
            this._super.apply(this, arguments);
            effectManager.startEffectRotation();
            console.log("KanbanRecord started with effect rotation");
        },

        destroy: function () {
            effectManager.stopEffectRotation();
            this._super.apply(this, arguments);
            console.log("KanbanRecord destroyed");
        },
    });

    FormView.include({
        start: function () {
            this._super.apply(this, arguments);
            effectManager.startEffectRotation();
            console.log("FormView started with effect rotation");
        },

        destroy: function () {
            effectManager.stopEffectRotation();
            this._super.apply(this, arguments);
            console.log("FormView destroyed");
        },
    });
});


