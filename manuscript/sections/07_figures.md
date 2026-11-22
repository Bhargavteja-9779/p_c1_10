## Figure captions

**Fig. 1.** Fleet calibration workflow. Only the master unit requires laboratory reference values. Items scanned on the master and on other units of the fleet provide paired difference spectra, from which the error of any linear calibration on unseen units is predicted (Eq. (5)) and minimised (FR-PLS, Eq. (6)); a new unit is qualified from five paired items without laboratory analysis.

![](figures/fig1_workflow.png){width=100%}

**Fig. 2.** Target-label-free prediction of the error of the master calibration on individual units. Predicted RMSEP (Eq. (5): master cross-validation and replicate scans, and the unit's scans of transfer items, without reference values) against the RMSEP realised on independent paired test items. (a) Mango, random item split (62 unit × season cases); (b) mango, population-grouped split — transfer and test fruit from different orchard populations (26 cases); (c) soil (6 properties) and corn, both axes divided by the master's cross-validated RMSE. Each point is one target unit, averaged over split repetitions; dashed line, identity; log–log axes.

![](figures/fig2_unit_risk.png){width=100%}

**Fig. 3.** Error on unseen units relative to the master PLS (leave-one-unit-out; paired test items). Points, physical units (mango and soil: log-ratios averaged over seasons or properties per unit; corn: instrument × property); bars, interquartile range; ticks, median. Orange, proposed; blue, existing transfer methods; grey, reference methods that use information unavailable in target-label-free deployment.

![](figures/fig3_methods.png){width=100%}

**Fig. 4.** Design curves for the mango fleet (seasons 2016–2018, 33 target units). (a) RMSEP of FR-PLS on unseen units and its label-free prediction against the number of fleet units contributing paired spectra (three random unit subsets per size). (b) Qualification of a new unit: RMSEP after label-free bias correction (LFBC) and its prediction against the number of items scanned on the new unit and the master (ten random draws per size); dotted lines, uncorrected RMSEP.

![](figures/fig4_design_curves.png){width=100%}

**Fig. 5.** Physical structure of unit effects. Fraction of each unit's mean paired difference spectrum (unit minus master, raw absorbance) explained by offset, gain, wavelength-shift and bandwidth terms, against the size of the difference. Mango units: one point per unit and season (2016–2018); soil units: one point per unit.

![](figures/fig5_unit_effects.png){width=60%}
