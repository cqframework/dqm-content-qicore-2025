# Discrepancy Report
| Details | Value |
| --- | --- |
| Generated | 2026-07-15 12:01:05.015384 |
| Total Measures | 72 |
| Total Test Cases | 5826 |
| Measures with Discrepancies | 3 |


| Discrepancy Summary | Measure Count | Test Case Count |
|---|:---:|:---:|
| Missing Results | 0 | 0 |
| Missing Populations | 0 | 0 |
| Mismatched Test Cases | 3 | 4 |


_Note: Measures can have multiple discrepancies, so the Measures with Discrepancies count may not match the summary counts._
## Measures with No Discrepancies (69)
- CMS2FHIRPCSDepScreenAndFollowUp
- CMS22FHIRPCSBPScreeningFollowUp
- CMS50FHIRReceiptofSpecialistReport
- CMS56FHIRFuncStatHipReplacement
- CMS68FHIRDocumentationCurrentMeds
- CMS69FHIRPCSBMIScreenAndFollowUp
- CMS71FHIRSTKAnticoagAFFlutter
- CMS72FHIRSTKAntithromboticDay2
- CMS74FHIRDentalCariesPrevention
- CMS75FHIRChildrenDentalDecay
- CMS90FHIRFSAforHeartFailure
- CMS104FHIRSTKDCAntithrombotic
- CMS108FHIRVTEProphylaxis
- CMS117FHIRChildImmunStatus
- CMS122FHIRDiabetesAssessGT9Pct
- CMS124FHIRCervicalCancerScreen
- CMS125FHIRBreastCancerScreen
- CMS128FHIRAntidepressantMgmt
- CMS129FHIRProstCaBoneScanUse
- CMS130FHIRColorectalCancerScrn
- CMS131FHIRDiabetesEyeExam
- CMS133FHIRCataracts2040BCVA90Days
- CMS135FHIRACEIorARBorARNIforHF
- CMS136FHIRChildADHDMedFollowUp
- CMS137FHIRSUDTxInitEngagement
- CMS138FHIRTobaccoScrnCessation
- CMS139FHIRFallRiskScreening
- CMS142FHIRCommWithDrManagingDiab
- CMS143FHIRPOAGOpticNerveEval
- CMS144FHIRHFBetaBlockerForLVSD
- CMS146FHIRApproTestPharyngitis
- CMS149FHIRDementiaCognitiveAssess
- CMS153FHIRChlamydiaScreening
- CMS154FHIRAppropriateTxforURI
- CMS155FHIRWgtAssessCounseling
- CMS156FHIRHighRiskMedsElderly
- CMS157FHIRPainIntensityQuantified
- CMS159FHIRDepRemissionat12Months
- CMS165FHIRControllingHighBP
- CMS190FHIRVTEProphylaxisICU
- CMS314FHIRHIVViralSuppression
- CMS0334FHIRPCCesareanBirth
- CMS347FHIRStatinPreventionTxCVD
- CMS349FHIRHIVScreening
- CMS506FHIRSafeUseofOpioids
- CMSFHIR529HybridHospitalWideReadmission
- CMS645FHIRBoneDensityPCADTherapy
- CMS646FHIRIntravesicalBCGTherapy
- CMS771FHIRUrinarySymptomScoreBPH
- CMS816FHIRHHHypo
- CMS819FHIRHHORAE
- CMS826FHIRHHPI
- CMS832FHIRHHAKI
- CMSFHIR844HybridHospitalWideMortality
- CMS871FHIRHHHyper
- CMS951FHIRKidneyHealthEval
- CMS986FHIRMalnutritionScore
- CMS996FHIRAptTxforSTEMI
- CMS1028FHIRPCSevereOBComps
- CMS1056FHIRCTClinical
- CMS1074FHIRCTIQR
- CMS1154ScreeningPrediabetesFHIR
- CMS1157FHIRHIVRetention
- CMS1173FHIRDiagnosticDelayVTE
- CMS1188FHIRHIVSTITesting
- CMS1206FHIRCTOQR
- CMS1218FHIRHHRF
- CMS1244FHIRECATHOQR
- CMS1264FHIRECATREHQR
## Measures with Discrepancies (3)
| Measure | Total Test Cases | Missing Results | Missing Populations | Mismatched Test Cases |
|---|:---:|:---:|:---:|:---:|
| CMS145FHIRCADBBlockerTPMIorLVSD | 106 | 0 | 0 | 0.94%   (1) |
| CMS177FHIRChildMDDSuicideAssmt | 41 | 0 | 0 | 2.44%   (1) |
| CMS1017FHIRHHFI | 65 | 0 | 0 | 3.08%   (2) |


#### CMS145FHIRCADBBlockerTPMIorLVSD

Mismatched Test Cases (1 of 106)
| Test Case | Group | Population | Expected | Actual |
|---|---|---|:---:|:---:|
| 1f70822b-c513-4c3a-8162-49f0bb9c914b | Group_2 | Denominator Exception | 0 | 1 |


#### CMS177FHIRChildMDDSuicideAssmt

Mismatched Test Cases (1 of 41)
| Test Case | Group | Population | Expected | Actual |
|---|---|---|:---:|:---:|
| 85e6225c-a9bb-4338-a228-297564e38c4d | Group_1 | Initial Population<br>Denominator | 0<br>0 | 1<br>1 |


#### CMS1017FHIRHHFI

Mismatched Test Cases (2 of 65)
| Test Case | Group | Population | Expected | Actual |
|---|---|---|:---:|:---:|
| 0dfafc1a-cf94-4ca1-becf-c1b843896810 | Group_1 | Numerator Exclusion | 1 | 0 |
| 5ff2713d-ca89-42ae-91bb-cba3e1d9a487 | Group_1 | Numerator Exclusion | 1 | 0 |


