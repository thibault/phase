var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Models = {};

    Phase.Models.Document = Backbone.Model.extend({
        idAttribute: 'pk'
    });

    /**
     * Represents a single search query set of parameters
     */
    Phase.Models.Search = Backbone.Model.extend({
        defaults: {
            search_terms: '',
            sort_by: 'sort_key',
            start: 0,
            size: Phase.Config.paginateBy
        },
        fromForm: function(form) {
            data = form.serializeArray();
            self = this;
            _.each(data, function(field) {
                self.set(field.name, field.value);
            });
        },
        nextPage: function() {
            var start = this.get('start');
            var size = this.get('size');
            this.set('start', start + size);
        },
        reset: function() {
            var start = this.defaults.start;
            var size = this.defaults.size;
        }
    });

})(this, Phase, Backbone, _);
