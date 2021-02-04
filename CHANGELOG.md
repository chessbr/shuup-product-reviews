# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Enter here all the changes made to the development version

## [1.0.9] - 2021-02-04

- Add package.json

## [1.0.8] - 2020-11-18

### Added

- Add classes to target the Vendor Reviews Option Tabs elements

### Fixed

- Display No Review Text in Vendor Reviews Option Tabs
- Add Show Recommenders to Vendor Reviews Option Tabs
- Add classes to target the Vendor Star Rating elements
- Add Show Recommenders to Vendor Star Rating

## [1.0.7] - 2020-10-28

### Fixed

- Use Shuup static util to fetch the current version of the addon


## [1.0.6] - 2020-10-19

- Add plugin to to render vendor reviews per option


## [1.0.5] - 2020-10-09

### Added

- Add containers with classes to target the elements in Vendor Review Option Rating
- Create Vendor Reviews Option Tabs plugin
  Each tab will contain the overall rating and the comments of the Review Option selected.


## [1.0.3] - 2020-09-28

### Fixed

- Fix issue that was not rendering starts in vendor reviews with options


## [1.0.2] - 2020-09-29

- Update Finnish and Swedish translations


## [1.0.1] - 2020-09-04

- Fix vendor reviews serializer which defined while excluding it
  (defining and excluding is not possible)


## [1.0.0] - 2020-08-07

Add Shuup 2.0 support. Not backwards compatible with 1.x version.

For patching old releases use "shuup1" branch.

## [0.6.4] - 2020-07-24

Last stable release for Shuup 1

- Add option for marketplace staff to define options for vendior reviews.
  These options can be used to categorize/group reviews. For example some
  options could be "Delivery", "Service Quality", "Service Price" etc... after
  the customer can leave review separately for each option.

## [0.6.0] - 2020-01-16

### Added

- Add util to render vendor reviews
- Add REST API endpoints for vendor reviews

### Changed

- Improve caches around vendor reviews
- Make orders available for review when paid instead of completed
