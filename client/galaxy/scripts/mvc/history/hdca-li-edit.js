import HDCA_LI from "mvc/history/hdca-li";
import DC_VIEW_EDIT from "mvc/collection/collection-view-edit";
import faIconButton from "ui/fa-icon-button";
import _l from "utils/localization";

//==============================================================================
var _super = HDCA_LI.HDCAListItemView;
/** @class Editing view for HistoryDatasetCollectionAssociation.
 */
var HDCAListItemEdit = _super.extend(
    /** @lends HDCAListItemEdit.prototype */ {
        /** logger used to record this.log messages, commonly set to console */
        //logger              : console,

        /** Override to return editable versions of the collection panels */
        _getFoldoutPanelClass: function() {
            var collectionType = this.model.get("collection_type");
            switch (collectionType) {
                case "list":
                    return DC_VIEW_EDIT.ListCollectionViewEdit;
                case "paired":
                    return DC_VIEW_EDIT.PairCollectionViewEdit;
                case "list:paired":
                    return DC_VIEW_EDIT.ListOfPairsCollectionViewEdit;
                case "list:list":
                    return DC_VIEW_EDIT.ListOfListsCollectionViewEdit;
            }
            throw new TypeError(`Unknown collection_type: ${collectionType}`);
        },

        // ......................................................................... delete
        /** In this override, add the delete button. */
        _renderPrimaryActions: function() {
            this.log(`${this}._renderPrimaryActions`);
            // render the display, edit attr and delete icon-buttons
            return _super.prototype._renderPrimaryActions.call(this).concat([this._renderDeleteButton()]);
        },

        /** Render icon-button to delete this collection. */
        _renderDeleteButton: function() {
            var deleted = this.model.get("deleted");
            return faIconButton({
                title: deleted ? _l("Dataset collection is already deleted") : _l("Delete"),
                classes: "delete-btn",
                faIcon: "fa-times",
                disabled: deleted,
                onclick: () => {
                    // ...bler... tooltips being left behind in DOM (hover out never called on deletion)
                    this.$el.find(".icon-btn.delete-btn").trigger("mouseout");
                    this.model["delete"]();
                }
            });
        },

        // ......................................................................... misc
        /** string rep */
        toString: function() {
            var modelString = this.model ? `${this.model}` : "(no model)";
            return `HDCAListItemEdit(${modelString})`;
        }
    }
);

//==============================================================================
export default {
    HDCAListItemEdit: HDCAListItemEdit
};
