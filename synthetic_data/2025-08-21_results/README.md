# Community Notes Synthetic Data Results

This folder contains summary results for experiments analyzing the Community Notes algorithm's performance under various synthetic conditions.

## Experiment Descriptions

The following experiments are included in this dataset:

### Bad actor experiments
- **`bad_actor_no_bias_grid`**: Varying frequency of bad rater behavior (`st_prop`) and percentage of bad raters (`bhvr_rate`)
- **`bad_actor_with_bias_grid`**: Varying `st_prop` and `bhvr_rate` with bias
- **`multi_bad_actor_no_bias`**: Fixed `st_prop=0.2`, varying `bhvr_rate`
- **`multi_bad_actor_with_bias`**: Fixed `st_prop=0.2`, varying `bhvr_rate` with bias
- **`multi_bad_actor_with_bias_bhvr_1`**: Fixed `bhvr_rate=1`, varying `st_prop`

### Rater bias experiments
- **`homophily`**: Rater-note homophily effects
- **`iu_var`**: Rater helpfulness variability
- **`note_pol`**: Note polarization effects
- **`user_pol`**: User polarization effects

### Combined bias experiments (to-be-updated)
- **`Homophily_HIGH_UPol_HIGH_NPol_HIGH`**: High homophily, high user polarization, high note polarization
- **`Homophily_HIGH_UPol_LOW_NPol_LOW`**: High homophily, low user polarization, low note polarization
- **`Homophily_LOW_UPol_HIGH_NPol_LOW`**: Low homophily, high user polarization, low note polarization
- **`Homophily_LOW_UPol_LOW_NPol_HIGH`**: Low homophily, low user polarization, high note polarization
- **`Homophily_LOW_UPol_LOW_NPol_LOW`**: Low homophily, low user polarization, low note polarization

## Data organization

Summary results for reputation filter enabled (`helpfulness_True`) and disabled (`helpfulness_False`) are stored in the `FP_count` folder of each respective experiment.

## CSV Column Definitions

The CSV files in the `FP_count` folders contain the following columns:

### Basic parameters
- **`params`**: Parameter string identifying the experimental configuration. Usually has the form `{st_prop}-r_fun-{bhvr_rate}-notes` or `{no_run}-r_fun-{bhvr_rate}-notes`. In plotting, we need to map the file name to the individual params depending on the experiments. This mapping is defined in the field `"fname_params_to_params"` in `definitions.json`. The order of elements in the list corresponds to the order of the param in the file name pattern.
- **`run_result_dir`**: Path to the actual directory containing run results
- **`condition`** (`fn<0, fn>=0, fn<0_inferred, fn>=0_inferred, all`): Condition based on note factor: 
    - `fn<0`, `fn>=0` for REAL left- and right-leaning notes
    - `fn<0_inferred`, `fn>=0_inferred` for INFERRED left- and right-leaning notes
    - `all` for all notes
Twos of the following columns, depending on the experiment:
- **`st_prop`**: Percentage of bad raters (0.0 to 1.0)
- **`bhvr_rate`**: Frequency of bad rater behavior (0.0 to 1.0)
- **`dhom`**: Rater-note homophily, $E_h$
- **`var_iu`**: Rater helpfulness variability, $\sigma_u^I$
- **`mu_fnr`**: Note polarization, $\rho_n$
- **`mu_fur`**: Rater polarization, $\rho_u$

### Raw Counts
A given note has two labels: 
- **Inferred label** (uppercase): published (H) or unpublished (U)
- **Ground truth label** (lowercase): helpful (h) or unhelpful (u)

- **`n_H`**: Number of notes classified as helpful (published) by the algorithm
- **`n_U`**: Number of notes classified as unhelpful (unpublished) by the algorithm
- **`n_h`**: Number of notes that are truly helpful (ground truth)
- **`n_u`**: Number of notes that are truly unhelpful (ground truth)
- **`n_uH`**: Number of false positives (truly unhelpful notes classified as helpful)
- **`n_hU`**: Number of false negatives (truly helpful notes classified as unhelpful)

### Error Rate Metrics
- **`p_u_H`**: **Pollution rate** - P(truly unhelpful | published) = n_uH / n_H
- **`p_h_U`**: **Suppression rate** - P(truly helpful | unpublished) = n_hU / n_h
- **`p_H_u`**: **Infiltration rate** - P(published | truly unhelpful) = n_uH / n_u
- **`p_U_h`**: **Waste rate** - P(unpublished | truly helpful) = n_hU / n_U

## Calculating proportions of published notes for each bias, real and inferred 

These proportions can be calculated using the raw counts defined above. Here's an example for fn<0:

```python
import pandas as pd 

# Load the data
df = pd.read_csv('synthetic_data/2025-08-21_results/bad_actor_with_bias_grid/FP_count/helpfulness_False.csv')

# NOTE: group by parameter before this step
# Filter by condition
left_real = df[df.condition == "fn<0"]
left_inferred = df[df.condition == "fn<0_inferred"]
all_notes = df[df.condition == "all"]

# Proportion of notes published with fn<0
left_p_published_inferred = left_inferred['n_H'] / all_notes['n_H']
left_p_published_real = left_real['n_H'] / all_notes['n_H']

```

## Scripts to create plots

The plotting scripts are available in the notebooks, numbered by the order they appear in the manuscript. They use `definitions.json` to understand how file names map to experimental parameters, and `stylesheet.mplstyle` to define the formatting of the plots. 
