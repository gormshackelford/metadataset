coordinates_cols = ['latitude_degrees', 'latitude_minutes', 'latitude_seconds', 'latitude_direction', 'longitude_degrees', 'longitude_minutes', 'longitude_seconds', 'longitude_direction']
minutes_seconds_cols = ['latitude_minutes', 'latitude_seconds', 'longitude_minutes', 'longitude_seconds']

date_cols = ['start_year', 'start_month', 'start_day', 'end_year', 'end_month', 'end_day']
day_cols = ['start_day', 'end_day']
month_cols = ['start_month', 'end_month']
year_cols = ['start_year', 'end_year']

decimal_cols = ['treatment_mean', 'control_mean', 'treatment_sd', 'control_sd', 'treatment_se', 'control_se', 'treatment_mean_before', 'control_mean_before', 'treatment_sd_before', 'control_sd_before', 'treatment_se_before', 'control_se_before', 'lsd', 'z_value']
integer_cols = ['treatment_n', 'control_n', 'treatment_n_before', 'control_n_before', 'n', 'study_id', 'start_year', 'end_year']

study_cols = ['study_id', 'study_name']

data_cols = ['comparison', 'treatment_mean', 'control_mean', 'treatment_sd', 'control_sd', 'treatment_n', 'control_n', 'treatment_se', 'control_se', 'treatment_mean_before', 'control_mean_before', 'treatment_sd_before', 'control_sd_before', 'treatment_n_before', 'control_n_before', 'treatment_se_before', 'control_se_before', 'unit', 'lsd', 'is_significant', 'approximate_p_value', 'p_value', 'z_value', 'n', 'correlation_coefficient', 'note']

generic_metadata_cols = study_cols + date_cols + coordinates_cols + ['country']

col_names = ['outcome'] + data_cols + generic_metadata_cols
