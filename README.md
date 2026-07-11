# dqm-content-qicore-2025
dQM Measure Content (Using QICore 6.0.0, based on FHIR R4 v4.0.1)

These draft FHIR-based measures and shared libraries are translated from the QDM-based versions of eCQMs that were published in May 2025 for the 2026 reporting year, exported from MADiE after final review and updates, in preparation for public comment review.

This repository has 3 branches:
* **imported** - This branch is the direct MADiE exported content (no re-processing of Library and Measure resources), so the narrative is what MADiE produced
* **imported-with-test-cases** - This branch is the direct MADiE export plus the test case exports in the tests directory
* **master** - This branch is the same content, but has been refreshed with the latest CQF Tooling and has narratives built using the latest Liquid templates

Commits to this repository will automatically trigger a build of the continuous integration build, available here:

https://build.fhir.org/ig/cqframework/dqm-content-qicore-2025

## Terminology Expectations

The measures in this repository are the same measures that were posted for public comment in January of 2026. The terminology package in support of those measures is:

http://cts.nlm.nih.gov/fhir/Library/ecqm-fhir-update-2025

> NOTE: The value sets in this repository are limited to expansions of 1000. To obtain the full expansions requires an NLM license and can be downloaded from the Value Set Authority Center downloads site: https://vsac.nlm.nih.gov/download/manifest?rel=20251117&res=dqm.vs.20251117.json

## Repository Structure

This repository is setup like any HL7 FHIR IG project but also includes the CQL files and test data which means the file structure will be as follows:

```
   |-- _genonce.bat
   |-- _genonce.sh
   |-- _refresh.bat
   |-- _refresh.sh
   |-- _updatePublisher.bat
   |-- _updatePublisher.sh
   |-- _updateCQFTooling.bat
   |-- _updateCQFTooling.sh
   |-- ig.ini
   |-- bundles
       |-- mat
           |-- <bundle files>
       |-- measure
           |-- <bundles>
   |-- input
       |-- dqm-content-qicore-2025.xml
       |-- cql
           |-- <library name>.cql
       |-- pagecontent
       |-- resources
           |-- library
               |-- <library name>.json
           |-- measure
               |-- <measure name>.json
       |-- tests
           |-- measure
               |-- <measure name>
                   |-- <test case patient id>
                       |-- <test case resource files>
                   |-- ...
       |-- vocabulary
           |-- valueset
               |-- external
```

## Extracting MAT Packages

CQF Tooling provides support for extracting a MAT exported package into the
directories of this repository so that the measure is included in the published
implementation guide. To do this, place the MAT export files (unzipped) in a
directory in the `bundles\mat` directory, and then run the following tooling
command:

```
[tooling-jar] -ExtractMatBundle bundles\mat\[bundle-directory]\[bundle-file]
```

For example:

```
input-cache\tooling-cli-3.9.1.jar -ExtractMATBundle bundles\mat\CLONE124_v6_03-Artifacts\measure-json-bundle.json
```

## Refresh IG Processing

CQF Tooling provides a "refresh" operation that performs the following functions:

* Translates and validates all CQL source files
* Encodes CQL and ELM content in the corresponding FHIR Library resources
* Refreshes generated content for each knowledge artifact (Library, Measure, PlanDefinition, ActivityDefinition) including parameters, dependencies, and effective data requirements

Whenever changes are made to the CQL, Library, or Measure resources, run the `_refresh` command to refresh the implementation guide content with the new content, and then run `_genonce` to run the publication tooling on the implementation guide (the same process that the continuous integration build uses to publish the implementation guide when commits are made to this repository).


## Measure Package Prep Process

1. Download Measure Zip folder to `bundles\mat` directory.
2. Unzip the folder, then unzip the MeasureExport and TestCaseExport folders within it.
3. Run `_updateCQFTooling.sh` script to ensure CQF tooling jar is present.
4. Update `_extractMATBundle.sh` so that `mat_bundle` points to the JSON file within the MeasureExport directory.
5. Run `_extractMATBundle.sh` to load Measure Resources.
6. Create a directory under `input\tests\measure` with the Measure ID.
7. Copy all files from the TestCaseExport directory to this newly created directory.
8. Update `_extractBundleResources.sh` so that `mat_bundle` points to this newly created directory.
9. Run `_extractBundleResources.sh` to populate test case resources.
10. Run `_refresh.sh` to refresh IG content.
