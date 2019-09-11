odoo.define('web.web_widget_url_pdf_viewer', function (require) {
"use strict";

    var basic_fields = require('web.basic_fields');

    basic_fields.UrlWidget.include({
        _getURI: function (fileURI) {
            var page = this.recordData[this.name + '_page'] || 1;
            if (!fileURI) {
                fileURI = this.value;
            }
            fileURI = encodeURIComponent(fileURI);
            var viewerURL = '/web/static/lib/pdfjs/web/viewer.html?file=';
            return viewerURL + fileURI + '#page=' + page;
        },
        /**
         * @private
         * @override
         */
        _renderReadonly: function () {
            var self = this;
            console.log("TEXT", this.$el.text(this.attrs.text || this.value), this.attrs, this);
            if (this.attrs.url_viewer == 'pdf_viewer') {
                var $iFrame = this.$el.text(this.attrs.text || this.value);
                if (this.value) {
                    $iFrame.replaceWith('<iframe o_pdfview_iframe/>');
                    $iFrame.addClass('o_field_pdfviewer');
                    $iFrame.attr('src', this._getURI(this.value));
                    console.log("IFRAME", $iFrame);
                } else {
                    this._super.apply(this, arguments);
                }
            } else {
                this._super.apply(this, arguments);
            }
        },
    });
});