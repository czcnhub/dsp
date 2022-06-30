# generated by datamodel-codegen:
#   filename:  schema.json
#   timestamp: 2022-06-30T18:40:09+00:00

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import AnyUrl, BaseModel, EmailStr, Extra, Field, confloat, constr


class License(BaseModel):
    class Config:
        extra = Extra.forbid

    name: Optional[str] = Field(
        None,
        description='Name of the license under which the resource is released.',
        title='License Name',
    )
    description: str = Field(
        ...,
        description='Text of the license or description of the license for the resource.',
        title='License Description',
    )
    url: Optional[AnyUrl] = Field(
        None,
        description='URL for a page that describes the license for the resource.',
        title='License URL',
    )


class Type(Enum):
    The_content_of_this_resource_can_be_executed_by = 'The content of this resource can be executed by'
    The_content_of_this_resource_was_created_by_a_related_App_or_software_program = (
        'The content of this resource was created by a related App or software program'
    )
    This_resource_is_described_by = 'This resource is described by'
    This_resource_conforms_to_established_standard_described_by = (
        'This resource conforms to established standard described by'
    )
    This_resource_has_another_resource_in_another_format = 'This resource has another resource in another format'
    This_resource_is_a_different_format_of = 'This resource is a different format of'
    This_resource_is_required_by = 'This resource is required by'
    This_resource_requires = 'This resource requires'
    This_resource_is_referenced_by = 'This resource is referenced by'
    The_content_of_this_resource_references = 'The content of this resource references'
    The_content_of_this_resource_is_derived_from = 'The content of this resource is derived from'


class Relation(BaseModel):
    type: Type = Field(
        ...,
        description='The type of relationship that exists between the describe resource and a related resource.',
        title='Relation Type',
    )
    value: constr(max_length=500) = Field(
        ...,
        description='String expressing the Full text citation, URL link for, or description of the related resource',
        title='Value',
    )


class TemporalCoverage(BaseModel):
    name: Optional[str] = Field(
        None,
        description='A string containing a name for the time interval.',
        title='Name',
    )
    start: datetime = Field(
        ...,
        description='A datetime object containing the instant corresponding to the commencement of the time interval (ISO8601 formatted date) - YYYY-MM-DDTHH:MM.',
        title='Start',
    )
    end: datetime = Field(
        ...,
        description='A datetime object containing the instant corresponding to the termination of the time interval (ISO8601 formatted date) - YYYY-MM-DDTHH:MM.',
        title='End',
    )


class SpatialCoverageItem(BaseModel):
    name: Optional[str] = Field(
        None,
        description='A string containing a name for the place associated with the geographic coverage.',
        title='Name',
    )
    east: confloat(lt=180.0, gt=-180.0) = Field(
        ...,
        description='The coordinate of the point location measured in the east direction (between -180 and 180)',
        title='East',
    )
    north: confloat(lt=90.0, gt=-90.0) = Field(
        ...,
        description=' The coordinate of the point location measured in the north direction (between -90 and 90)',
        title='North',
    )
    units: Optional[str] = Field(
        'Decimal degrees',
        description='The units applying to the unlabelled numeric values of north and east.',
        title='Units',
    )
    projection: Optional[str] = Field(
        'WGS 84 EPSG:4326',
        description='The name of the projection used with any parameters required, such as ellipsoid parameters, datum, standard parallels and meridians, zone, etc.',
        title='Projection',
    )


class SpatialCoverageItem1(BaseModel):
    name: Optional[str] = Field(
        None,
        description='A string containing a name for the place associated with the geographic coverage.',
        title='Name',
    )
    northlimit: confloat(lt=90.0, gt=-90.0) = Field(
        ...,
        description='A floating point value containing the constant coordinate for the northernmost face or edge of the bounding box (between -90 and 90)',
        title='North limit',
    )
    eastlimit: confloat(lt=180.0, gt=-180.0) = Field(
        ...,
        description='A floating point value containing the constant coordinate for the easternmost face or edge of the bounding box (between -180 and 180)',
        title='East limit',
    )
    southlimit: confloat(lt=90.0, gt=-90.0) = Field(
        ...,
        description='A floating point value containing the constant coordinate for the southernmost face or edge of the bounding box (between -90 and 90)',
        title='South limit',
    )
    westlimit: confloat(lt=180.0, gt=-180.0) = Field(
        ...,
        description='A floating point value containing the constant coordinate for the westernmost face or edge of the bounding box (between -180 and 180)',
        title='West limit',
    )
    units: Optional[str] = Field(
        'Decimal degrees',
        description='A string containing the units applying to the unlabelled numeric values of northlimit, eastlimit, southlimit, and westlimit.',
        title='Units',
    )
    projection: Optional[str] = Field(
        'WGS 84 EPSG:4326',
        description='A string containing the name of the projection used with any parameters required, such as ellipsoid parameters, datum, standard parallels and meridians, zone, etc.',
        title='Projection',
    )


class Provider(BaseModel):
    class Config:
        extra = Extra.forbid

    name: str = Field(
        ...,
        description='The name of the repository or organization that provides access to the resource.',
        title='Provider Name',
    )
    url: AnyUrl = Field(
        ...,
        description='A URL for the repository or organization that provides access to the resource.',
        title='Provider URL',
    )


class Creator(BaseModel):
    name: constr(max_length=100) = Field(
        ...,
        description='Full name of person or organization. Personal name format: family, given.',
        title='Name',
    )
    organization: constr(max_length=200) = Field(
        ...,
        description='A string containing the name of the organization with which the creator is affiliated',
        title='Organization',
    )
    email: Optional[EmailStr] = Field(
        None,
        description='A string containing an email address for the creator',
        title='Email',
    )
    orcid: Optional[constr(regex=r'(\d{4}-){3}\d{4}')] = Field(
        None, description='ORCID identifier for creator.', title='ORCID'
    )


class Contributor(BaseModel):
    name: constr(max_length=100) = Field(
        ...,
        description='Full name of person or organization. Personal name format: family, given.',
        title='Name',
    )
    organization: constr(max_length=200) = Field(
        ...,
        description='A string containing the name of the organization with which the contributor is affiliated.',
        title='Organization',
    )
    email: Optional[EmailStr] = Field(
        None,
        description='A string containing an email address for the contributor.',
        title='Email',
    )
    orcid: Optional[constr(regex=r'(\d{4}-){3}\d{4}')] = Field(
        None, description='ORCID identifier for contributor.', title='ORCID'
    )


class Award(BaseModel):
    class Config:
        extra = Extra.forbid

    fundingAgency: str = Field(
        ...,
        description='Name of the agency or organization that funded the creation of the resource.',
        title='Funding agency name',
    )
    awardNumber: str = Field(
        ...,
        description='A unique numeric or string identifer for the grant or project.',
        title='Award number or identifier',
    )
    awardName: str = Field(
        ...,
        description='The name or title of the grant or project.',
        title='Award name',
    )
    awardURL: Optional[AnyUrl] = Field(
        None,
        description='A string containing a URL pointing to a website describing the award or funding agency.',
        title='Award URL',
    )


class RelationType(Enum):
    The_content_of_this_resource_can_be_executed_by = 'The content of this resource can be executed by'
    The_content_of_this_resource_was_created_by_a_related_App_or_software_program = (
        'The content of this resource was created by a related App or software program'
    )
    This_resource_is_described_by = 'This resource is described by'
    This_resource_conforms_to_established_standard_described_by = (
        'This resource conforms to established standard described by'
    )
    This_resource_has_another_resource_in_another_format = 'This resource has another resource in another format'
    This_resource_is_a_different_format_of = 'This resource is a different format of'
    This_resource_is_required_by = 'This resource is required by'
    This_resource_requires = 'This resource requires'
    This_resource_is_referenced_by = 'This resource is referenced by'
    The_content_of_this_resource_references = 'The content of this resource references'
    The_content_of_this_resource_is_derived_from = 'The content of this resource is derived from'


class Relation1(BaseModel):
    type: RelationType = Field(
        ...,
        description='The type of relationship with the related resource',
        title='Relation type',
    )
    value: constr(max_length=500) = Field(
        ...,
        description='String expressing the Full text citation, URL link for, or description of the related resource',
        title='Value',
    )


class GenericDatasetSchemaForCzNetDataSubmissionPortalV100(BaseModel):
    name: constr(max_length=300) = Field(
        ...,
        description='Descriptive name or title for the resource.',
        title='Name or title',
    )
    description: str = Field(
        ...,
        description='A string containing a description/abstract for the resource.',
        title='Description or abstract',
    )
    keywords: List[str] = Field(
        ...,
        description='A list of free text keywords related to the resource.',
        min_items=2,
        title='Subject Keywords',
        unique_items=True,
    )
    creators: List[Creator] = Field(
        ...,
        description='Creators of the resource in order of importance.',
        min_items=1,
        title='Creators',
        unique_items=True,
    )
    contributors: Optional[List[Contributor]] = Field(
        [],
        description='Contributors to the resource in order of importance.',
        title='Contributors',
        unique_items=True,
    )
    license: Optional[License] = Field(
        None,
        description='License under which the resource is released for access and reuse.',
        title='License',
    )
    funders: List[Award] = Field(
        ...,
        description='Source of grants/awards that funded creation of all or part of the resource.',
        min_items=1,
        title='Funding agency information',
        unique_items=True,
    )
    relations: Optional[List[Relation]] = Field(
        None,
        description='Raw textual references (e.g., a bibligraphic citation) for publications and datasets related to this resource.',
        title='Related resources',
    )
    notes: Optional[str] = Field(
        None,
        description='Additional notes related to the resource.',
        title='Additional notes',
    )
    version: Optional[str] = Field(
        None,
        description='A version tag string for the resource - e.g., v1.0.0. Mostly relevant for software and dataset uploads. Any string will be accepted, but semantically-versioned tag is recommended.',
        title='Version',
    )
    url: AnyUrl = Field(
        ...,
        description='URL for the landing page that describes the resource and where the content of the resource can be accessed.',
        title='URL',
    )
    identifier: Optional[str] = Field(
        None,
        description='A globally unique and persistent identifier for the submission.',
        title='Identifier',
    )
    temporalCoverage: Optional[TemporalCoverage] = Field(
        None,
        description='The temporal coverage of the resource. The time period that it describes or applies to.',
        title='Temporal coverage',
    )
    spatialCoverage: Optional[Union[SpatialCoverageItem, SpatialCoverageItem1]] = Field(
        None,
        description='The place(s) that are the focus of the resource. The geospatial area that the resource describes, the spatial topic of a resource, the spatial applicability of a resource, or jurisdiction under with a resource is relevant.',
        title='Spatial coverage',
    )
    provider: Provider = Field(
        ...,
        description='The repository or organization that provides access to the resource.',
        title='Provider',
    )
    dateCreated: Optional[datetime] = Field(
        None,
        description='The date on which the resource was originally created (ISO8601 formatted date) - YYYY-MM-DDTHH:MM.',
        title='Date created',
    )
    dateModified: Optional[datetime] = Field(
        None,
        description='The date on which the resource was last modified (ISO8601 formatted date) - YYYY-MM-DDTHH:MM.',
        title='Date modified',
    )
    datePublished: datetime = Field(
        ...,
        description='The date on which the resource was permanently published (ISO8601 formatted date) - YYYY-MM-DDTHH:MM.',
        title='Date published',
    )
