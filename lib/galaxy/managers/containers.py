"""
Manager mixins to unify the interface into things that can contain: Datasets
and other (nested) containers.

(e.g. DatasetCollections, Histories, LibraryFolders)

Histories should be DatasetCollections.
Libraries should be DatasetCollections.
"""

import operator

import galaxy.exceptions
import galaxy.util

from galaxy.managers import base

import logging
log = logging.getLogger( __name__ )


# ====
class ContainerManagerMixin( object ):
    """
    A class that tracks/contains two types of items:
        1) some non-container object (such as datasets)
        2) other sub-containers nested within this one

    Levels of nesting are not considered here; In other words,
    each of the methods below only work on the first level of
    nesting.
    """
    # TODO: this should be an open mapping (not just 2)
    #: the classes that can be contained
    contained_class = None
    subcontainer_class = None
    #: how any contents lists produced are ordered
    order_contents_on = None

    # ---- interface
    def contents( self, container ):
        """
        Returns both types of contents: filtered and in some order.
        """
        iters = []
        iters.append( self.contained( container ) )
        iters.append( self.subcontainers( container ) )
        return galaxy.util.merge_sorted_iterables( self.order_contents_on, *iters )

    def contained( self, container ):
        """
        Returns non-container objects.
        """
        return self._filter_contents( container, self.contained_class, **kwds )

    def subcontainers( self, container ):
        """
        Returns only the containers within this one.
        """
        return self._filter_contents( container, self.subcontainer_class, **kwds )

    # ---- private
    def _filter_contents( self, container, content_class, **kwds ):
        # TODO: use list (or by_history etc.)
        container_filter = self._filter_to_contained( container, content_class )
        query = self.session().query( content_class ).filter( container_filter )
        return query

    def _filter_to_contained( self, container, content_class ):
        raise galaxy.exceptions.NotImplemented( 'Abstract class' )

    def _get_content_manager( self, content_class ):
        raise galaxy.exceptions.NotImplemented( 'Abstract class' )


class HistoryAsContainerManagerMixin( ContainerManagerMixin ):

    contained_class = model.HistoryDatasetAssociation
    subcontainer_class = model.HistoryDatasetCollectionAssociation
    order_contents_on = operator.attrgetter( 'hid' )

    def _filter_to_contained( self, container, content_class ):
        return content_class.history == container

    def _get_content_manager( self, content_class ):
        # type snifffing is inevitable
        if   content_class == model.HistoryDatasetAssociation:
            return self.hda_manager
        elif content_class == model.HistoryDatasetCollectionAssociation:
            return self.hdca_manager
        raise TypeError( 'Unknown contents class: ' + str( content_class ) )


class LibraryFolderAsContainerManagerMixin( ContainerManagerMixin ):
    # can contain two types of subcontainer: LibraryFolder, LibraryDatasetCollectionAssociation
    # has as the top level container: Library

    contained_class = model.LibraryDatasetAssociation
    subcontainer_class = model.LibraryFolder
    # subcontainer_class = model.LibraryDatasetCollectionAssociation
    order_contents_on = operator.attrgetter( 'create_time' )

    def _filter_to_contained( self, container, content_class ):
        if content_class == subcontainer_class:
            return subcontainer_class.parent == container
        return contained_class.folder == container

    def _get_content_manager( self, content_class ):
        # type snifffing is inevitable
        if   content_class == model.LibraryDatasetAssociation:
            return self.lda_manager
        elif content_class == model.LibraryFolder:
            return self.folder_manager
        raise TypeError( 'Unknown contents class: ' + str( content_class ) )


class DatasetCollectionAsContainerManagerMixin( ContainerManagerMixin ):

    # (note: unlike the other collections, dc's wrap both contained and subcontainers in this class)
    contained_class = model.DatasetCollectionElement
    subcontainer_class = model.DatasetCollection
    order_contents_on = operator.attrgetter( 'element_index' )

    def _filter_to_contained( self, container, content_class ):
        return content_class.collection == container

    def _get_content_manager( self, content_class ):
        # type snifffing is inevitable
        if   content_class == model.DatasetCollectionElement:
            return self.collection_manager
        elif content_class == model.DatasetCollection:
            return self.collection_manager
        raise TypeError( 'Unknown contents class: ' + str( content_class ) )


# ====
class ContainableModelMixin:
    """
    Mixin for that which goes in a container.
    """

    # ---- interface
    def parent_container( self, containable ):
        """
        Return this item's parent container or None if unrecorded.
        """
        raise galaxy.exceptions.NotImplemented( 'Abstract class' )

    def set_parent_container( self, containable, new_parent_container ):
        raise galaxy.exceptions.NotImplemented( 'Abstract class' )
