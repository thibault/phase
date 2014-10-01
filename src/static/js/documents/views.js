var Phase = Phase || {};

(function(exports, Phase, Backbone, _) {
    "use strict";

    Phase.Views = {};

    var dispatcher = _.clone(Backbone.Events);

    /**
     * This is the main view, englobing all other views.
     */
    Phase.Views.MainView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render');

            this.documentsCollection = new Phase.Collections.DocumentCollection();

            this.headerView = new Phase.Views.HeaderView();
            this.tableView = new Phase.Views.TableView();
            this.paginationView = new Phase.Views.PaginationView();
            this.buttonView = new Phase.Views.ActionButtonsView();

            this.listenTo(this.documentsCollection, 'add', this.addDocument);

            this.documentsCollection.fetch({
                success: this.render
            });
        },
        addDocument: function(document) {
            this.tableView.addDocumentView(
                new Phase.Views.RowView({ model: document })
            );
        },
        render: function() {
            var displayedDocuments = this.documentsCollection.length;
            var totalDocuments = this.documentsCollection.total;
            this.paginationView.render(displayedDocuments, totalDocuments);

            return this;
        },
        selectRow: function(document) {
        }
    });

    /**
     * The document table header
     */
    Phase.Views.HeaderView = Backbone.View.extend({
        el: 'table#documents thead',
        events: {
            'click #select-all': 'selectAll'
        },
        selectAll: function(event) {
            var target = $(event.currentTarget);
            var checked = target.is(':checked');
            dispatcher.trigger('selectAll', checked);
        }
    });

    /**
     * The whole document table, using sub views to represent rows.
     */
    Phase.Views.TableView = Backbone.View.extend({
        el: 'table#documents tbody',
        addDocumentView: function(documentView) {
            this.$el.append(documentView.render().el);
        }
    });

    /**
     * A single view in the document table
     */
    Phase.Views.RowView = Backbone.View.extend({
        tagName: 'tr',
        template: _.template($('#documents-template').html()),
        events: {
            'click input[type=checkbox]': 'selectRow',
        },
        initialize: function() {
            this.listenTo(dispatcher, 'selectAll', this.checkRow);
        },
        render: function() {
            this.$el.html(this.template(this.model.attributes));
            this.checkbox = this.$el.find('input[type=checkbox]').first();

            return this;
        },
        checkRow: function(checked) {
            this.checkbox.prop('checked', checked);
            this.selectRow();
        },
        selectRow: function() {
            dispatcher.trigger('rowSelected', this.model);
            if (this.checkbox.is(':checked')) {
                this.$el.addClass('selected');
            } else {
                this.$el.removeClass('selected');
            }
        }
    });

    /**
     * A small view to handle the pagination text.
     * "xxx documents on yyy"
     */
    Phase.Views.PaginationView = Backbone.View.extend({
        el: 'p#display-results',
        render: function(displayed, total) {
            var results;
            if (displayed <= 1) {
                results = '' + displayed + ' document on ' + total;
            } else {
                results = '' + displayed + ' documents on ' + total;
            }
            this.$el.html(results);

            return this;
        }
    });

    Phase.Views.ActionButtonsView = Backbone.View.extend({
        el: '#document-list-form form',
        initialize: function() {
            this.buttons = this.$el.find('.navbar-action');
            this.dropdown = this.$el.find('.dropdown-form');
            this.closeBtn = this.dropdown.find('button[data-toggle=dropdown]');

            this.configureForm();
            this.listenToOnce(dispatcher, 'rowSelected', this.activateButtons);
        },
        activateButtons: function() {
            this.buttons.removeClass('disabled');
        },
        configureForm: function() {
            // We update the form action depending on
            // the clicked button
            var form = this.$el;
            this.buttons.on('click', function(event) {
                var action = $(this).data('form-action');
                form.attr('action', action);
            });

            // Prevent closing dropdown on any click
            this.dropdown.parent().on('hide.bs.dropdown', function(e) {
                e.preventDefault();
            });

            // Since we blocked form dropdown to be automaticaly closed,
            // we must manually bind the close button to do it
            this.closeBtn.on('click', function(event) {
                var dropdown = $(this).closest('.dropdown');
                dropdown.toggleClass('open');
            });
        }
    });

})(this, Phase, Backbone, _);
